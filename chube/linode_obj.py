"""Module for the Linode model.

   In case you're wondering, this module is called 'linode_obj' instead of 'linode'
   because the latter conflicts with the Python Linode bindings."""
import time

from .api import api_handler
from .util import RequiresParams, keywords_only
from .model import *
from .datacenter import Datacenter


class Linode(Model):
    """Linode API object."""

    # Macros for the values of `status`
    STATUS_BOOTFAILED = -2
    STATUS_CREATING = -1
    STATUS_BRANDNEW = 0
    STATUS_RUNNING = 1
    STATUS_OFF = 2
    STATUS_SHUTTINGDOWN = 3
    STATUS_SAVED = 4

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
    def _datacenter_getter(self):
        return Datacenter.find(api_id=self.datacenter_id)
    def _datacenter_setter(self, val):
        raise NotImplementedError("You can't just go around changing the `datacenter` property. Who do you think you are?")
    datacenter = property(_datacenter_getter, _datacenter_setter)

    # The `ipaddresses` attribute
    def _ipaddresses_getter(self):
        return IPAddress.search(linode=self.api_id)
    def _ipaddresses_setter(self, val):
        raise NotImplementedError("Cannot set `ipaddresses` directly; use `add_private_ip` instead.")
    ipaddresses = property(_ipaddresses_getter, _ipaddresses_setter)

    # The `configs` attribute
    def _configs_getter(self):
        return Config.search(linode=self.api_id)
    def _configs_setter(self, val):
        raise NotImplementedError("Cannot set `configs` directly; use `add_config` instead.")
    configs = property(_configs_getter, _configs_setter)

    # The `configs` attribute
    def _disks_getter(self):
        return Disk.search(linode=self.api_id)
    def _disks_setter(self, val):
        raise NotImplementedError("Cannot set `disks` directly; use `create_disk` instead.")
    disks = property(_disks_getter, _disks_setter)

    # The `all_jobs` attribute
    def _all_jobs_getter(self):
        return Job.search(linode=self.api_id, include_finished=True)
    def _all_jobs_setter(self, val):
        raise NotImplementedError("Cannot set `all_jobs` attribute.")
    all_jobs = property(_all_jobs_getter, _all_jobs_setter)

    # The `pending_jobs` attribute
    def _pending_jobs_getter(self):
        return Job.search(linode=self.api_id, include_finished=False)
    def _pending_jobs_setter(self, val):
        raise NotImplementedError("Cannot set `pending_jobs` attribute.")
    pending_jobs = property(_pending_jobs_getter, _pending_jobs_setter)

    @classmethod
    @keywords_only
    def search(cls, **kwargs):
        """Returns the list of Linode instances that match the given criteria.
        
           The special paramater `label_begins` allows you to case-insensitively
           match the beginning of the label string. For example,
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
    @keywords_only
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
    @keywords_only
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
        api_params = self.api_update_params()
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
        return IPAddress.find(linode=self.api_id, api_id=rval["IPADDRESSID"])

    @keywords_only
    def create_disk(self, **kwargs):
        """Adds a disk. See `help(Disk.create)` for more info."""
        if kwargs.has_key('linode'):
            if type(kwargs['linode']) is not int: kwargs['linode'] = kwargs['linode'].api_id
            if kwargs['linode'] != self.api_id:
                raise RuntimeError("Received 'linode' argument that differed from the instance")
        return Disk.create(linode=self.api_id, **kwargs)

    def is_up(self):
        """Determines whether the instance is up."""
        return self.status == Linode.STATUS_RUNNING

    @keywords_only
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

    @keywords_only
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

    @keywords_only
    def shutdown(self, **kwargs):
        """Shuts down the Linode."""
        rval = api_handler.linode_shutdown(linodeid=self.api_id)
        return Job.find(linode=self.api_id, api_id=rval["JobID"], include_finished=True)

    @RequiresParams("plan", "datacenter", "payment_term")
    @keywords_only
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
    @keywords_only
    def resize(self, **kwargs):
        """Moves a Linode to a new server on a different Plan.

           `plan` (required): Can be a Plan object or a numeric plan ID."""
        plan = kwargs["plan"]
        if type(plan) is not int: plan = plan.api_id
        api_handler.linode_resize(linodeid=self.api_id, planid=plan)


class IPAddress(Model):
    direct_attrs = [
        # IDs
        DirectAttr("api_id", u"IPADDRESSID", int, int),
        DirectAttr("linode_id", u"LINODEID", int, int),

        # Properties
        DirectAttr("address", u"IPADDRESS", unicode, unicode),
        DirectAttr("rdns_name", u"RDNS_NAME", unicode, unicode),
        DirectAttr("is_public", u"ISPUBLIC", bool, int)
    ]

    # The `linode` attribute is done with a deferred lookup.
    def _linode_getter(self):
        return Linode.find(api_id=self.linode_id)
    def _linode_setter(self, val):
        raise NotImplementedError("Cannot assign IP address to a different Linode")
    linode = property(_linode_getter, _linode_setter)

    @classmethod
    @RequiresParams("linode")
    @keywords_only
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
    @keywords_only
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


class Config(Model):
    direct_attrs = [
        # IDs
        DirectAttr("api_id", u"ConfigID", int, int,
                   update_as="configid"),
        DirectAttr("linode_id", u"LinodeID", int, int,
                   update_as="linodeid"),
        DirectAttr("kernel_id", u"KernelID", int, int,
                   update_as="kernelid"),

        # Properties
        DirectAttr("label", u"Label", unicode, unicode,
                   update_as="label"),
        DirectAttr("comments", u"Comments", unicode, unicode,
                   update_as="comments"),
        DirectAttr("run_level", u"RunLevel", unicode, unicode,
                   update_as="runlevel"),
        DirectAttr("ram_limit", u"RAMLimit", int, int,
                   update_as="ramlimit"),
        DirectAttr("disk_list", u"DiskList", unicode, unicode,
                   update_as="disklist"),
        DirectAttr("root_device_custom", u"RootDeviceCustom", unicode, unicode,
                   update_as="rootdevicecustom"),
        DirectAttr("root_device_ro", u"RootDeviceRO", bool, int,
                   update_as="rootdevicero"),
        DirectAttr("root_device_num", u"RootDeviceNum", int, int,
                   update_as="rootdevicenum"),

        # `helper` properties
        DirectAttr("helper_xen", u"helper_xen", bool, int,
                   update_as="helper_xen"),
        DirectAttr("helper_libtls", u"helper_libtls", bool, int,
                   update_as="helper_libtls"),
        DirectAttr("helper_depmod", u"helper_depmod", bool, int,
                   update_as="helper_depmod"),
        DirectAttr("helper_disable_updatedb", u"helper_disableUpdateDB", bool, int,
                   update_as="helper_disableupdatedb")
    ]

    # The `linode` attribute is done with a deferred lookup.
    def _linode_getter(self):
        return Linode.find(api_id=self.linode_id)
    def _linode_setter(self, val):
        raise NotImplementedError("Cannot assign Config to a different Linode")
    linode = property(_linode_getter, _linode_setter)

    # The `disks` attribute is based on `disk_list`
    def _disks_getter(self):
        """Returns the list of disks associated with the configuration.

           If any slot is empty, `None` will be returned in that slot."""
        disks = []
        for disk_id in self.disk_list.split(","):
            if disk_id == "": disks.append(None)
            else: disks.append(Disk.find(linode=self.linode_id, api_id=int(disk_id)))
        return disks
    def _disks_setter(self, val):
        """Updates the list of disks associated with the configuration.

           `val`: An 8-element list of Disk objects and None objects."""
        disk_ids = []
        for disk in val:
            if disk is None:
                disk_ids.append("")
            else:
                disk_ids.append(disk.api_id)
        if len(disk_ids) != 9:
            raise "A Config must have exactly 9 disks. Use `None` for empty slots."
        self.disk_list = ",".join(map(str, disk_ids))
    disks = property(_disks_getter, _disks_setter)

    @classmethod
    @RequiresParams("linode", "kernel", "label", "disks")
    @keywords_only
    def create(cls, **kwargs):
        """Creates a new Config.

           `linode`: Either a Linode object or a numeric Linode ID
           `kernel`: Either a Kernel object or a numeric kernel ID from `avail.kernels`
           `label`: The name of the new config.
           `disks`: Either an array of `Disk` and `None` objects, or an array of disk IDs
               and `None` objects."""
        linode, kernel, label, disks = (kwargs["linode"], kwargs["kernel"], kwargs["label"],
                                        kwargs["disks"])
        if type(linode) is not int: linode = linode.api_id
        if type(kernel) is not int: kernel = kernel.api_id
        if disks[0] is None: raise RuntimeError("The first disk slot may not be empty.")

        disklist = []
        for d in disks:
            if d is None: disklist.append(u"")
            elif type(d) is not int: disklist.append(unicode(d.api_id))
            else: disklist.append(unicode(d))
        disklist = u",".join(disklist)

        rval = api_handler.linode_config_create(linodeid=linode, kernelid=kernel, label=label,
                                                disklist=disklist)
        new_config_id = rval[u"ConfigID"]
        return cls.find(api_id=new_config_id, linode=linode)

    @classmethod
    @RequiresParams("linode")
    @keywords_only
    def search(cls, **kwargs):
        """Returns the list of Config instances that match the given criteria.
        
           At least `linode` is required. It can be a Linode object or a numeric Linode ID."""
        linode = kwargs["linode"]
        if type(linode) is not int: linode = linode.api_id
        a = [cls.from_api_dict(d) for d in api_handler.linode_config_list(linodeid=linode)]
        del kwargs["linode"]

        for k, v in kwargs.items():
            a = [conf for conf in a if getattr(conf, k) == v]
        return a

    @classmethod
    @RequiresParams("api_id", "linode")
    @keywords_only
    def find(cls, **kwargs):
        """Returns a single Config instance that matches the given criteria.

           For example, `Config.find(api_id=102382061, linode=819201)`.

           Both parameters are required. `linode` may be a Linode ID or a Linode object."""
        linode = kwargs["linode"]
        if type(linode) is not int: linode = linode.api_id
        a = [cls.from_api_dict(d) for d in api_handler.linode_config_list(linodeid=linode, configid=kwargs["api_id"])]
        return a[0]

    def save(self):
        """Saves the Config object to the API."""
        api_params = self.api_update_params()
        api_handler.linode_config_update(**api_params)

    def refresh(self):
        """Refreshes the Config object with a new API call."""
        new_inst = Config.find(api_id=self.api_id, linode=self.linode_id)
        for attr in self.direct_attrs:
            setattr(self, attr.local_name, getattr(new_inst, attr.local_name))
        del new_inst

    def destroy(self):
        """Deletes the Config object."""
        api_handler.linode_config_delete(linodeid=self.linode.api_id, configid=self.api_id)

    def __repr__(self):
        return "<Config api_id=%d, label='%s'>" % (self.api_id, self.label)


class Disk(Model):
    direct_attrs = [
        # IDs
        DirectAttr("api_id", u"DISKID", int, int,
                   update_as="diskid"),
        DirectAttr("linode_id", u"LINODEID", int, int,
                   update_as="linodeid"),

        # Properties
        DirectAttr("label", u"LABEL", unicode, unicode,
                   update_as="label"),
        DirectAttr("is_read_only", u"ISREADONLY", bool, int,
                   update_as="isreadonly"),
        DirectAttr("type", u"TYPE", unicode, unicode),
        DirectAttr("update_dt", u"UPDATE_DT", unicode, unicode),
        DirectAttr("create_dt", u"CREATE_DT", unicode, unicode),
        DirectAttr("status", u"STATUS", int, int),
        DirectAttr("size", u"SIZE", int, int)
    ]

    # The `linode` attribute is done with a deferred lookup.
    def _linode_getter(self):
        return Linode.find(api_id=self.linode_id)
    def _linode_setter(self, val):
        raise NotImplementedError("Cannot assign Disk to a different Linode")
    linode = property(_linode_getter, _linode_setter)

    @classmethod
    @RequiresParams("linode")
    @keywords_only
    def search(cls, **kwargs):
        """Returns the list of Disk instances that match the given criteria.
        
           At least `linode` is required. It can be a Linode object or a numeric Linode ID."""
        linode = kwargs["linode"]
        if type(linode) is not int: linode = linode.api_id
        a = [cls.from_api_dict(d) for d in api_handler.linode_disk_list(linodeid=linode)]
        del kwargs["linode"]

        for k, v in kwargs.items():
            a = [addr for addr in a if getattr(addr, k) == v]
        return a

    @classmethod
    @RequiresParams("api_id", "linode")
    @keywords_only
    def find(cls, **kwargs):
        """Returns a single Disk instance that matches the given criteria.

           For example, `Disk.find(api_id=102382061, linode=819201)`.

           Both parameters are required. `linode` may be a Linode ID or a Linode object."""
        linode = kwargs["linode"]
        if type(linode) is not int: linode = linode.api_id
        a = [cls.from_api_dict(d) for d in api_handler.linode_disk_list(linodeid=linode, diskid=kwargs["api_id"])]
        return a[0] 

    @classmethod
    @keywords_only
    def create(cls, **kwargs):
        """Creates a new Disk.
        
           `distribution` (optional): If provided, then this method will pass
               your arguments through to `create_from_distribution`.
           `stackscript` (optional): If provided, then this method will pass your
               arguments through to `create_from_stackscript`.
           
           If neither of those parameters is given, then we'll pass your arguments
           through to `create_straightup`."""
        if kwargs.has_key("distribution"): return cls.create_from_distribution(**kwargs)
        if kwargs.has_key("stackscript"): return cls.create_from_stackscript(**kwargs)
        return cls.create_straightup(**kwargs)

    @classmethod
    @RequiresParams("linode", "stackscript", "ss_input", "distribution", "label", "size", "root_pass")
    @keywords_only
    def create_from_stackscript(cls, **kwargs):
        """Creates a new Disk based on a Stackscript.

           `linode`: Either a Linode object or a numeric Linode ID.
           `stackscript`: Either a Stackscript object or a numeric Stackscript ID.
           `ss_input`: The UDF responses for the Stackscript (a StackscriptInput instance).
           `distribution`: Either a Distribution object or a numeric Distribution ID.
           `label`: The name of the new disk.
           `size`: The size, in MB, of the new disk.
           `root_pass`: The root user's password."""
        linode, stackscript, ss_input, distribution, label, size, root_pass = (
            kwargs["linode"], kwargs["stackscript"], kwargs["ss_input"],
            kwargs["distribution"], kwargs["label"], kwargs["size"], kwargs["root_pass"])
        if type(linode) is not int: linode = linode.api_id
        if type(stackscript) is not int: stackscript = stackscript.api_id
        if type(distribution) is not int: distribution = distribution.api_id
        rval = api_handler.linode_disk_createfromstackscript(
            linodeid=linode, stackscriptid=stackscript,
            stackscriptudfresponses=unicode(ss_input), distributionid=distribution,
            label=label, size=size, rootpass=root_pass)
        new_disk_id = rval[u"DiskID"]
        return cls.find(api_id=new_disk_id, linode=linode)

    @classmethod
    @RequiresParams("linode", "distribution", "label", "size", "root_pass")
    @keywords_only
    def create_from_distribution(cls, **kwargs):
        """Creates a new Disk based on a Distribution.

           `linode`: Either a Linode object or a numeric Linode ID
           `distribution`: Either a Distribution object or a numeric Distribution ID.
           `label`: The name of the new disk.
           `size`: The size, in MB, of the disk.
           `root_pass`: The root user's password.
           `root_ssh_key` (optional): Contents of the root user's `.ssh/authorized_keys` file."""
        linode, distribution, label, fstype, size, root_pass = (
            kwargs["linode"], kwargs["distribution"], kwargs["label"],
            kwargs["size"], kwargs["size"], kwargs["root_pass"])
        if type(linode) is not int: linode = linode.api_id
        if type(distribution) is not int: distribution = distribution.api_id
        if kwargs.has_key("root_ssh_key"):
            root_ssh_key = kwargs["root_ssh_key"]
        else:
            root_ssh_key = ""
        rval = api_handler.linode_disk_createfromdistribution(
            linodeid=linode, distributionid=distribution, label=label, size=size,
            rootpass=root_pass, rootsshkey=root_ssh_key)
        new_disk_id = rval[u"DiskID"]
        return cls.find(api_id=new_disk_id, linode=linode)

    @classmethod
    @RequiresParams("linode", "label", "fstype", "size")
    @keywords_only
    def create_straightup(cls, **kwargs):
        """Creates a new Disk.

           `linode`: Either a Linode object or a numeric Linode ID
           `label`: The name of the new disk.
           `fstype`: Either 'ext3', 'swap', or 'raw'.
           `size`: The size in MB of this disk."""
        linode, label, fstype, size = (kwargs["linode"], kwargs["label"], kwargs["fstype"],
                                       kwargs["size"])
        if type(linode) is not int: linode = linode.api_id
        rval = api_handler.linode_disk_create(linodeid=linode, label=label, type=fstype,
                                              size=size)
        new_disk_id = rval[u"DiskID"]
        return cls.find(api_id=new_disk_id, linode=linode)

    def save(self):
        """Saves the Disk object to the API."""
        api_params = self.api_update_params()
        api_handler.linode_disk_update(**api_params)

    def refresh(self):
        """Refreshes the Disk object with a new API call."""
        new_inst = Disk.find(api_id=self.api_id, linode=self.linode_id)
        for attr in self.direct_attrs:
            setattr(self, attr.local_name, getattr(new_inst, attr.local_name))
        del new_inst

    def destroy(self):
        """Deletes the Disk."""
        api_handler.linode_disk_delete(linodeid=self.linode.api_id, diskid=self.api_id)

    def resize(self, new_size):
        """Resizes the Disk.

           `new_size`: The new size of the disk, in MB."""
        api_handler.linode_disk_resize(linodeid=self.linode.api_id, diskid=self.api_id,
                                       size=new_size)

    def duplicate(self):
        """Performs a bit-for-bit copy of a disk image."""
        rval = api_handler.linode_disk_duplicate(linodeid=self.linode.api_id, diskid=self.api_id)
        return Disk.find(linode=self.linode.api_id, api_id=rval["DiskID"])

    def __repr__(self):
        return "<Disk api_id=%d, label='%s'>" % (self.api_id, self.label)


class Job(Model):
    direct_attrs = [
        # IDs
        DirectAttr("api_id", u"JOBID", int, int),
        DirectAttr("linode_id", u"LINODEID", int, int),

        # Properties
        DirectAttr("label", u"LABEL", unicode, unicode),
        DirectAttr("entered_dt", u"ENTERED_DT", unicode, unicode),
        DirectAttr("start_dt", u"HOST_START_DT", unicode, unicode),
        DirectAttr("finish_dt", u"HOST_FINISH_DT", unicode, unicode),
        DirectAttr("action", u"ACTION", unicode, unicode),
        DirectAttr("message", u"HOST_MESSAGE", unicode, unicode),

        # This can come back as either the empty string or an int, so we
        # like to massage it as a property before giving it to the user.
        DirectAttr("_duration_str", u"DURATION", unicode, unicode),
        # This can come back as either the empty string or an int, so we
        # would prefer it if the user used our convenience methods.
        DirectAttr("_host_success", u"HOST_SUCCESS", unicode, unicode)
    ]

    # The `linode` attribute is done with a deferred lookup.
    def _linode_getter(self):
        return Linode.find(api_id=self.linode_id)
    def _linode_setter(self, val):
        raise NotImplementedError("Cannot assign Job to a different Linode")
    linode = property(_linode_getter, _linode_setter)

    # The `duration` attribute needs to be massaged before returning it to the
    # user. If the job isn't finished yet, we'll return `None`.
    def _duration_getter(self):
        if self._duration_str == u"":
            return None
        return int(self._duration_str)
    def _duration_setter(self, val):
        raise NotImplementedError("Cannot set Job duration")
    duration = property(_duration_getter, _duration_setter)

    # The `host_success` attribute doesn't fit neatly into a type, so we provide
    # these convenience methods.
    def is_done(self):
        """Determines whether the Job is finished (either successfully or unsuccessfully)."""
        return self._host_success in (u"0", u"1")
    def is_success(self):
        """Determines whether the Job finished successfully.
        
           Returns False if the job either hasn't finished yet _or_ has failed."""
        return self._host_success == u"1"
    def is_fail(self):
        """Determines whether the Job has failed."""
        return self._host_success == u"0"

    @classmethod
    @RequiresParams("linode")
    @keywords_only
    def search(cls, **kwargs):
        """Returns the list of Job instances that match the given criteria.
        
           `linode` (required): A Linode object or a numeric Linode ID.
           `include_finished` (optional): If True, we will search not only pending
               jobs but all jobs."""
        include_finished = False
        if kwargs.has_key("include_finished"):
            include_finished = kwargs["include_finished"]
            del kwargs["include_finished"]

        linode = kwargs["linode"]
        if type(linode) is not int: linode = linode.api_id
        a = [cls.from_api_dict(d) for d in api_handler.linode_job_list(linodeid=linode, pendingonly=(not include_finished))]
        del kwargs["linode"]

        for k, v in kwargs.items():
            a = [addr for addr in a if getattr(addr, k) == v]
        return a

    @classmethod
    @keywords_only
    def find(cls, **kwargs):
        """Returns a single Job instance that matches the given criteria.

           For example, `Job.find(api_id=102382061, linode=819201)`.

           Both parameters are required. `linode` may be a Linode ID or a Linode object."""
        a = cls.search(**kwargs)
        if len(a) < 1: raise RuntimeError("No Job found with the given criteria (%s)" % (kwargs,))
        if len(a) > 1: raise RuntimeError("More than one Job found with the given criteria (%s)" % (kwargs,))
        return a[0]

    def wait(self, timeout=120, check_interval=5):
        """Blocks until the job is finished.

           `timeout` (optional): Number of seconds to wait before giving up.
           `check_interval` (optional): How often to check, in seconds.

           Raises a `RuntimeError` if the timeout is reached. Raises a `ValueError` if
           the job fails."""
        for t in range(0, timeout, check_interval):
            self.refresh()
            if self.is_fail():
                raise ValueError("Job '%s' on Linode '%s' failed" % (self.label, self.linode.label))
            if self.is_success():
                return
            time.sleep(check_interval)
        raise RuntimeError("Job '%s' on Linode '%s' took longer than %d seconds to complete; aborting." % (self.label, self.linode.label, timeout))

    def refresh(self):
        """Refreshes the Job object with a new API call."""
        new_inst = Job.find(api_id=self.api_id, linode=self.linode_id)
        for attr in self.direct_attrs:
            setattr(self, attr.local_name, getattr(new_inst, attr.local_name))
        del new_inst

    def __repr__(self):
        return "<Job api_id=%d, label='%s'>" % (self.api_id, self.label)


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


        print "~~~ Making sure that Linode.create_disk correctly handles extra 'linode' argument"
        print
        a_suffix = "".join(random.sample(SUFFIX_CHARS, SUFFIX_LEN))
        b_suffix = "".join(random.sample(SUFFIX_CHARS, SUFFIX_LEN))
        a_disk_name = "chube-test-%s" % (a_suffix,)
        b_disk_name = "chube-test-%s" % (b_suffix,)
        a_disk = linode_obj.create_disk(linode=linode_obj, label=a_disk_name, fstype="swap", size=1000)
        try:
            b_disk = linode_obj.create_disk(linode=2, label=b_disk_name, fstype="swap", size=1000)
        except RuntimeError:
            # This is the expected behavior. You shouldn't be able to call create_disk on a Linode
            # and pass a different Linode.
            pass
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

        print "~~~ Deleting Config '%s'" % (config.label,)
        print
        config.destroy()
 
        print "~~~ Deleting Linode '%s'" % (linode_a.label,)
        print
        linode_a.destroy()
        print "~~~ Deleting Linode '%s'" % (linode_b.label,)
        print
        linode_b.destroy()

        print "~~~ Tests passed!"
