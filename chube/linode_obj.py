"""Module for the Linode model.

   In case you're wondering, this module is called 'linode_obj' instead of 'linode'
   because the latter conflicts with the Python Linode bindings."""
from .api import api_handler
from .util import RequiresParams
from .model import *
from .datacenter import Datacenter


class Linode(Model):
    direct_attrs = [
        # IDs
        DirectAttr("api_id", u"LINODEID", int, int,
                   update_as="linodeid"),
        DirectAttr("datacenter_id", u"DATACENTERID", int, int),

        # Properties
        DirectAttr("label", u"LABEL", unicode, unicode,
                   update_as="label"),
        DirectAttr("display_group", u"LPM_DISPLAYGROUP", unicode, unicode,
                   update_as="lpm_displaygroup"),
        DirectAttr("create_dt", u"CREATE_DT", unicode, unicode),
        DirectAttr("total_hd", u"TOTALHD", int, int),
        DirectAttr("total_xfer", u"TOTALXFER", int, int),
        DirectAttr("total_ram", u"TOTALRAM", int, int),

        # Dynamic values
        DirectAttr("status", u"STATUS", int, int),
        DirectAttr("alert_cpu_enabled", u"ALERT_CPU_ENABLED", bool, bool,
                   update_as="alert_cpu_enabled"),
        DirectAttr("alert_cpu_threshold", u"ALERT_CPU_THRESHOLD", int, int,
                   update_as="alert_cpu_threshold"),
        DirectAttr("alert_diskio_enabled", u"ALERT_DISKIO_ENABLED", bool, bool,
                   update_as="alert_diskio_enabled"),
        DirectAttr("alert_diskio_threshold", u"ALERT_DISKIO_THRESHOLD", int, int,
                   update_as="alert_diskio_threshold"),
        DirectAttr("alert_bwin_enabled", u"ALERT_BWIN_ENABLED", bool, bool,
                   update_as="alert_bwin_enabled"),
        DirectAttr("alert_bwin_threshold", u"ALERT_BWIN_THRESHOLD", int, int,
                   update_as="alert_bwin_threshold"),
        DirectAttr("alert_bwout_enabled", u"ALERT_BWOUT_ENABLED", bool, bool,
                   update_as="alert_bwout_enabled"),
        DirectAttr("alert_bwout_threshold", u"ALERT_BWOUT_THRESHOLD", int, int,
                   update_as="alert_bwout_threshold"),
        DirectAttr("alert_bwquota_enabled", u"ALERT_BWQUOTA_ENABLED", bool, bool,
                   update_as="alert_bwquota_enabled"),
        DirectAttr("alert_bwquota_threshold", u"ALERT_BWQUOTA_THRESHOLD", int, int,
                   update_as="alert_bwquota_threshold"),
        DirectAttr("backup_weekly_daily", u"BACKUPWEEKLYDAY", int, int,
                   update_as="backupweeklydaily"),
        DirectAttr("backup_window", u"BACKUPWINDOW", int, int,
                   update_as="backupwindow"),
        DirectAttr("watchdog", u"WATCHDOG", bool, bool,
                   update_as="watchdog")
    ]

    # The `datacenter` attribute is done with a deferred lookup.
    def datacenter_getter(self):
        return Datacenter.find(api_id=self.datacenter_id)
    def datacenter_setter(self, val):
        raise NotImplementedError("You can't just go around changing the `datacenter` property. Who do you think you are?")
    datacenter = property(datacenter_getter, datacenter_setter)

    # The `ipaddresses` attribute
    def ipaddresses_getter(self):
        return IPAddress.search(linode=self.api_id)
    def ipaddresses_setter(self, val):
        raise NotImplementedError("Cannot set `ipaddresses` directly; use `add_private_ip` instead.")
    ipaddresses = property(ipaddresses_getter, ipaddresses_setter)

 
    @classmethod
    def search(cls, **kwargs):
        """Returns the list of Linode instances that match the given criteria.
        
           The special paramater `location_begins` allows you to case-insensitively
           match the beginning of the location string. For example,
           `Linode.search(location_begins='dallas')`."""
        a = [cls.from_api_dict(d) for d in api_handler.linode_list()]
        if kwargs.has_key("location_begins"):
            a = [linode_obj for linode_obj in a if
                 linode_obj.location.lower().startswith(kwargs["location_begins"].lower())]
            del kwargs["location_begins"]
        for k, v in kwargs.items():
            a = [linode_obj for linode_obj in a if getattr(linode_obj, k) == v]
        return a

    @classmethod
    def find(cls, **kwargs):
        """Returns a single Linode instance that matches the given criteria.

           For example, `Linode.find(api_id=4)`.

           Raises an exception if there is not exactly one Linode matching the criteria."""
        a = cls.search(**kwargs)
        if len(a) < 1: raise RuntimeError("No Linode found with the given criteria (%s)" % (kwargs,))
        if len(a) > 1: raise RuntimeError("More than one Linode found with the given criteria (%s)" % (kwargs,))
        return a[0]

    @classmethod
    @RequiresParams("plan", "datacenter", "payment_term")
    def create(cls, **kwargs):
        """Creates a new Linode.

           `plan`: Either a Plan object or a numeric plan ID from `avail.linodeplans`
           `datacenter`: Either a Datacenter object or a numeric datacenter ID from
               `avail.datacenters`
           `payment_term`: An integer number of months that represents a valid Linode
               payment term (1, 12, or 24 at the time of this writing)."""
        plan, datacenter, payment_term = (kwargs["plan"], kwargs["datacenter"], kwargs["payment_term"])
        if type(plan) is not int: plan = plan.api_id
        if type(datacenter) is not int: datacenter = datacenter.api_id
        rval = api_handler.linode_create(planid=plan, datacenterid=datacenter, paymentterm=payment_term)
        new_linode_id = rval[u"LinodeID"]
        return cls.find(api_id=new_linode_id)

    def save(self):
        """Saves the Linode object to the API."""
        api_params = {}
        attrs = [attr for attr in self.direct_attrs if attr.is_savable()]
        for attr in attrs:
            api_params[attr.update_as] = attr.api_type(getattr(self, attr.local_name))
        api_handler.linode_update(**api_params)

    def refresh(self):
        """Refreshes the Linode object with a new API call."""
        new_inst = Linode.find(api_id=self.api_id)
        for attr in self.direct_attrs:
            setattr(self, attr.local_name, getattr(new_inst, attr.local_name))
        del new_inst

    def destroy(self):
        """Deletes the Linode."""
        api_handler.linode_delete(linodeid=self.api_id, skipchecks=True)

    def __repr__(self):
        return "<Linode api_id=%d, label='%s'>" % (self.api_id, self.label)

    def add_private_ip(self):
        """Adds a private IP address to the Linode and returns it."""
        rval = api_handler.linode_ip_addprivate(linodeid=self.api_id)
        return IPAddress.find(linode=self.api_id, api_id=rval["IPAddressID"])


class IPAddress(Model):
    direct_attrs = [
        # IDs
        DirectAttr("api_id", u"IPADDRESSID", int, int),
        DirectAttr("linode_id", u"LINODEID", int, int),

        # Properties
        DirectAttr("address", u"IPADDRESS", unicode, unicode),
        DirectAttr("rdns_name", u"RDNS_NAME", unicode, unicode),
        DirectAttr("is_public", u"ISPUBLIC", bool, int),
    ]

    # The `linode` attribute is done with a deferred lookup.
    def linode_getter(self):
        return Linode.find(api_id=self.linode_id)
    def linode_setter(self, val):
        raise NotImplementedError("Cannot assign IP address to a different Linode")
    linode = property(linode_getter, linode_setter)

    @classmethod
    @RequiresParams("linode")
    def search(cls, **kwargs):
        """Returns the list of IPAddress instances that match the given criteria.
        
           At least `linode` is required. It can be a Linode object or a numeric Linode ID."""
        linode = kwargs["linode"]
        if type(linode) is not int: linode = linode.api_id
        a = [cls.from_api_dict(d) for d in api_handler.linode_ip_list(linodeid=linode)]
        del kwargs["linode"]

        for k, v in kwargs.items():
            a = [addr for addr in a if getattr(addr, k) == v]
        return a

    @classmethod
    @RequiresParams("api_id", "linode")
    def find(cls, **kwargs):
        """Returns a single IPAddress instance that matches the given criteria.

           For example, `IPAddress.find(api_id=102382061, linode=819201)`.

           Both parameters are required. `linode` may be a Linode ID or a Linode object."""
        linode = kwargs["linode"]
        if type(linode) is not int: linode = linode.api_id
        a = [cls.from_api_dict(d) for d in api_handler.linode_ip_list(linodeid=linode, ipaddressid=kwargs["api_id"])]
        return a[0]

    def refresh(self):
        """Refreshes the IPAddress object with a new API call."""
        new_inst = IPAddress.find(api_id=self.api_id, linode=self.linode_id)
        for attr in self.direct_attrs:
            setattr(self, attr.local_name, getattr(new_inst, attr.local_name))
        del new_inst

    def __repr__(self):
        return "<IPAddress api_id=%d, address='%s'>" % (self.api_id, self.address)


class LinodeTest:
    """Suite of integration tests to run when `chube test Linode` is called."""
    @classmethod
    def run(cls):
        import random

        from .plan import Plan
        from .datacenter import Datacenter

        SUFFIX_CHARS = "abcdefghijklmnopqrtuvwxyz023456789"
        SUFFIX_LEN = 8
        display_group_suffix = "".join(random.sample(SUFFIX_CHARS, SUFFIX_LEN))
        chube_display_group = "chube-test-%s" % (display_group_suffix)
        linode_a_suffix = "".join(random.sample(SUFFIX_CHARS, SUFFIX_LEN))
        linode_a_name = "chube-test-%s" % (linode_a_suffix,)
        linode_b_suffix = "".join(random.sample(SUFFIX_CHARS, SUFFIX_LEN))
        linode_b_name = "chube-test-%s" % (linode_b_suffix,)

        print "~~~ Creating Linode '%s' by specifying Datacenter and Plan IDs" % (linode_a_name,)
        print
        plan = Plan.find(label="Linode 1024")
        datacenter = Datacenter.find(location_begins="dallas")
        linode_a = Linode.create(plan=plan.api_id, datacenter=datacenter.api_id, payment_term=1)
        print linode_a
        print
        print "watchdog = %s" % (linode_a.watchdog,)
        print "datacenter = %s" % (linode_a.datacenter,)

        print
        print "~~~ Updating Linode '%s' with the display group '%s'" % (linode_a_name, chube_display_group,)
        print
        linode_a.label = linode_a_name
        linode_a.display_group = chube_display_group
        linode_a.save()

        print "~~~ Creating Linode '%s' by specifying Datacenter and Plan objects" % (linode_b_name,)
        print
        plan = Plan.find(label="Linode 1024")
        datacenter = Datacenter.find(location_begins="london")
        linode_b = Linode.create(plan=plan.api_id, datacenter=datacenter.api_id, payment_term=1)
        print linode_b
        print
        print "~~~ Updating Linode '%s' with the display group '%s'" % (linode_b_name, chube_display_group,)
        print
        linode_b.label = linode_b_name
        linode_b.display_group = chube_display_group
        linode_b.save()

        print "~~~ Adding private IP address to Linode '%s'" % (linode_b_name,)
        print
        ip = linode_b.add_private_ip()
        print ip

        print "~~~ Fetching the IP addresses for Linode '%s'" % (linode_b_name,)
        print
        ips = linode_b.ipaddresses
        print ips
        print

        print "~~~ Listing all Linodes in the display group '%s'" % (chube_display_group,)
        print
        linode_objs = Linode.search(display_group=chube_display_group)
        print linode_objs
        print

        sample_linode_obj = random.sample(linode_objs, 1)[0]

        linode_obj_id = sample_linode_obj.api_id
        print "~~~ Fetching linode_obj '%s' by Linode ID" % (sample_linode_obj.label,)
        print
        linode_obj = Linode.find(api_id=linode_obj_id)
        print "api_id = %d" % (linode_obj.api_id,)
        print "datacenter_id = %d" % (linode_obj.datacenter_id,)
        print "datacenter = %s" % (linode_obj.datacenter,)
        print "label = '%s'" % (linode_obj.label,)
        print "display_group = '%s'" % (linode_obj.display_group,)
        print "create_dt = '%s'" % (linode_obj.create_dt,)
        print
        assert linode_obj.api_id == sample_linode_obj.api_id
        assert linode_obj.watchdog == sample_linode_obj.watchdog

        print "~~~ Refreshing the Linode '%s'" % (linode_obj.label,)
        print
        linode_obj.refresh()
        print linode_obj
        print

        print "~~~ Deleting Linode '%s'" % (linode_a.label,)
        print
        linode_a.destroy()
        print "~~~ Deleting Linode '%s'" % (linode_b.label,)
        print
        linode_b.destroy()

        print "~~~ Tests passed!"
