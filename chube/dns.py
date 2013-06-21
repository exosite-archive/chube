"""Module for DNS-related models."""
from .api import api_handler
from .util import RequiresParams
from .model import *


class Domain(Model):
    direct_attrs = [
        # IDs
        DirectAttr("api_id", u"DOMAINID", int, int,
                   update_as="domainid"),

        # Properties
        DirectAttr("domain", u"DOMAIN", unicode, unicode,
                   update_as="domain"),
        DirectAttr("description", u"description", unicode, unicode,
                   update_as="description"),
        DirectAttr("zone_type", u"TYPE", unicode, unicode,
                   update_as="type"),
        DirectAttr("zone_type", u"TYPE", unicode, unicode,
                   update_as="type"),
        DirectAttr("soa_email", u"SOA_EMAIL", unicode, unicode,
                   update_as="soa_email"),
        DirectAttr("retry_sec", u"RETRY_SEC", int, int,
                   update_as="retry_sec"),
        DirectAttr("expire_sec", u"EXPIRE_SEC", int, int,
                   update_as="expire_sec"),
        DirectAttr("ttl_sec", u"TTL_SEC", int, int,
                   update_as="ttl_sec"),
        DirectAttr("master_ips_str", u"MASTER_IPS", unicode, unicode,
                   update_as="master_ips"),
        DirectAttr("axfr_ips_str", u"AXFR_IPS", unicode, unicode,
                   update_as="axfr_ips"),
        DirectAttr("status", u"STATUS", int, int),
    ]

    # The `master_ips` attribute is based on `master_ips_str`
    def master_ips_getter(self):
        """Returns the zone's master DNS servers, as an array of IP addresses."""
        ips = self.master_ips_str.split(",")
        return ips
    def master_ips_setter(self, val):
        """Sets the zone's master DNS servers.

           `val`: A list of IP address strings."""
        self.master_ips_str = ",".join(val)
    master_ips = property(master_ips_getter, master_ips_setter)

    @classmethod
    def search(cls, **kwargs):
        """Returns the list of Linode instances that match the given criteria.
        
           The special paramater `location_begins` allows you to case-insensitively
           match the beginning of the location string. For example,
           `Linode.search(label_begins='web-')`."""
        a = [cls.from_api_dict(d) for d in api_handler.linode_list()]
        if kwargs.has_key("label_begins"):
            a = [linode_obj for linode_obj in a if
                 linode_obj.label.lower().startswith(kwargs["label_begins"].lower())]
            del kwargs["label_begins"]
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

    def create_disk(self, **kwargs):
        """Adds a disk. See `help(Disk.create)` for more info."""
        return Disk.create(linode=self.api_id, **kwargs)

    def boot(self, **kwargs):
        """Boots the Linode.
 
           `config` (optional): A Config object or a numerical Config ID."""
        api_args = {"linodeid": self.api_id}
        if kwargs.has_key("config"):
            if type(kwargs["config"]) is not int:
                api_args["configid"] = kwargs["config"].api_id
            else:
                api_args["configid"] = kwargs["config"]
        rval = api_handler.linode_boot(**api_args)
        return Job.find(linode=self.api_id, api_id=rval["JobID"], include_finished=True)

    def reboot(self, **kwargs):
        """Reboots the Linode.
        
           `config` (optional): A Config object or a numerical Config ID."""
        api_args = {"linodeid": self.api_id}
        if kwargs.has_key("config"):
            if type(kwargs["config"]) is not int:
                api_args["configid"] = kwargs["config"].api_id
            else:
                api_args["configid"] = kwargs["config"]
        rval = api_handler.linode_reboot(**api_args)
        return Job.find(linode=self.api_id, api_id=rval["JobID"], include_finished=True)

    def shutdown(self, **kwargs):
        """Shuts down the Linode."""
        rval = api_handler.linode_shutdown(linodeid=self.api_id)
        return Job.find(linode=self.api_id, api_id=rval["JobID"], include_finished=True)

    @RequiresParams("plan", "datacenter", "payment_term")
    def clone(self, **kwargs):
        """Clones a Linode and gives you full privileges to it.

           `plan` (required): Can be a Plan object or a numeric plan ID.
           `datacenter` (required): Can be a Datacenter object or a numeric datacenter ID.
           `payment_term` (required): An integer number of months that represents a valid
               Linode payment term (1, 12, or 24 at the time of this writing)."""
        plan, datacenter, payment_term = (kwargs["plan"], kwargs["datacenter"],
                                          kwargs["payment_term"])
        if type(plan) is not int: plan = plan.api_id
        if type(datacenter) is not int: datacenter = datacenter.api_id
        rval = api_handler.linode_clone(linodeid=self.api_id, planid=plan, datacenterid=datacenter, paymentterm=payment_term)
        return Linode.find(api_id=rval["LinodeID"])

    @RequiresParams("plan")
    def resize(self, **kwargs):
        """Moves a Linode to a new server on a different Plan.

           `plan` (required): Can be a Plan object or a numeric plan ID."""
        plan = kwargs["plan"]
        if type(plan) is not int: plan = plan.api_id
        api_handler.linode_resize(linodeid=self.api_id, planid=plan)


class LinodeTest:
    """Suite of integration tests to run when `chube test Linode` is called."""
    @classmethod
    def run(cls):
        import random

        from .plan import Plan
        from .kernel import Kernel
        from .distribution import Distribution
        from .stackscript import Stackscript, StackscriptInput

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
        print "~~~ Updating Linode '%s' with the display group '%s'" % (linode_a.label, chube_display_group,)
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
        print "~~~ Updating Linode '%s' with the display group '%s'" % (linode_b.label, chube_display_group,)
        print
        linode_b.label = linode_b_name
        linode_b.display_group = chube_display_group
        linode_b.save()

        print "~~~ Waiting for job(s) to finish on Linode '%s'" % (linode_a.label,)
        print
        [j.wait() for j in linode_a.pending_jobs]
        print "~~~ Cloning Linode '%s'" % (linode_a.label,)
        print
        a_clone = linode_a.clone(plan=plan, datacenter=datacenter, payment_term=1)

        print "~~~ Destroying clone Linode '%s'" % (a_clone.label,)
        print
        a_clone.destroy()

        print "~~~ Adding private IP address to Linode '%s'" % (linode_b_name,)
        print
        ip = linode_b.add_private_ip()
        print ip
        print

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


        disk_suffix = "".join(random.sample(SUFFIX_CHARS, SUFFIX_LEN))
        disk_name = "chube-test-%s" % (disk_suffix,)
        print "~~~ Creating a Disk from scratch for Linode '%s'" % (linode_obj.label,)
        print
        disk = Disk.create(linode=linode_obj, label=disk_name, fstype="ext3", size=1000)
        print disk
        print
        print "~~~ Duplicating the disk '%s'" % (disk.label,)
        print
        print disk.duplicate()
        print


        disk_suffix = "".join(random.sample(SUFFIX_CHARS, SUFFIX_LEN))
        disk_name = "chube-test-%s" % (disk_suffix,)
        print "~~~ Creating a Disk from a distribution for Linode '%s'" % (linode_obj.label,)
        print
        distro = Distribution.find(label=u"Debian 7")
        disk = Disk.create(linode=linode_obj, distribution=distro, label=disk_name, size=1000, root_pass="czGgsxCvFHkR")
        print disk
        print
        print "~~~ Destroying disk '%s'" % (disk.label,)
        print
        disk.destroy()


        disk_suffix = "".join(random.sample(SUFFIX_CHARS, SUFFIX_LEN))
        disk_name = "chube-test-%s" % (disk_suffix,)
        stackscript_suffix = "".join(random.sample(SUFFIX_CHARS, SUFFIX_LEN))
        stackscript_name = "chube-test-%s" % (stackscript_suffix,)
        print "~~~ Creating a Disk from a stackscript for Linode '%s'" % (linode_obj.label,)
        print
        distro = Distribution.find(label=u"Debian 7")
        stackscript = Stackscript.create(label=stackscript_name, distributions=[distro],
                                         script=u"#!/bin/bash\n\n/bin/true")
        ss_input = StackscriptInput(blah="foo")
        disk = Disk.create(linode=linode_obj, stackscript=stackscript,
                           ss_input=ss_input, distribution=distro,
                           label=disk_name, size=1000, root_pass="czGgsxCvFHkR")
        print disk
        print
        stackscript.destroy()


        print "~~~ Creating a Config for Linode '%s' using disk '%s'" % (linode_obj.label, disk.label)
        print
        kerns = Kernel.search()
        kern = [k for k in kerns if k.label.lower().startswith("latest 32 bit ")][0]
        config_suffix = "".join(random.sample(SUFFIX_CHARS, SUFFIX_LEN))
        config_name = "chube-test-%s" % (config_suffix,)
        config = Config.create(linode=linode_obj, kernel=kern, label=config_name,
                               disks=[disk] + 8 * [None])
        print config
        print


        print "~~~ Searching for that config"
        print
        rslt = Config.search(linode=linode_obj, api_id=config.api_id)
        print rslt
        print
        assert len(rslt) == 1


        print "~~~ Creating and adding swap space for Linode '%s'" % (linode_obj.label,)
        print
        swap_disk_suffix = "".join(random.sample(SUFFIX_CHARS, SUFFIX_LEN))
        swap_disk_name = "chube-test-%s" % (swap_disk_suffix,)
        swap_disk = linode_obj.create_disk(label=swap_disk_name, fstype="swap", size=1000)
        config.disks = [disk, None, swap_disk] + 6 * [None]
        config.save()


        print "~~~ Checking for presence of that swap space in the Config's `disks` attribute"
        print
        assert bool([d for d in config.disks if d is not None and d.api_id == swap_disk.api_id])


        print "~~~ Refreshing the Linode '%s'" % (linode_obj.label,)
        print
        linode_obj.refresh()
        print linode_obj
        print


        print "~~~ Booting the Linode '%s'" % (linode_obj.label,)
        print
        job = linode_obj.boot(config=config)
        print "~~~ Listing all jobs for Linode '%s'" % (linode_obj.label,)
        print
        rslt_1 = Job.search(linode=linode_obj, include_finished=True)
        print rslt_1
        print 
        print "~~~ Listing all jobs for Linode '%s' the other way" % (linode_obj.label,)
        print
        rslt_2 = linode_obj.all_jobs
        assert sorted([j.api_id for j in rslt_1]) == sorted([j.api_id for j in rslt_2])
        print rslt_2
        print
        print "~~~ Listing active jobs for Linode '%s'" % (linode_obj.label,)
        print
        print linode_obj.pending_jobs
        print


        print "~~~ Waiting for the boot job '%s' to finish" % (job.label,)
        print
        job.wait()
        print "duration = %d" % (job.duration,)
        print "is_success() = %s" % (job.is_success(),)
        print "message = '%s'" % (job.message,)
        print


        print "~~~ Rebooting the Linode '%s'" % (linode_b.label,)
        print
        job = linode_obj.reboot(config=config)


        print "~~~ Shutting down Linode '%s'" % (linode_a.label,)
        print
        job = linode_a.shutdown()

 
        print "~~~ Deleting Linode '%s'" % (linode_a.label,)
        print
        linode_a.destroy()
        print "~~~ Deleting Linode '%s'" % (linode_b.label,)
        print
        linode_b.destroy()

        print "~~~ Tests passed!"
