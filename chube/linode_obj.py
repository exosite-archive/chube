"""Module for the Linode model.

   In case you're wondering, this module is called 'linode_obj' instead of 'linode'
   because the latter conflicts with the Python Linode bindings."""
from .api import api_handler
from .model import *

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

    def refresh(self):
        """Refreshes the linode_obj with a new API call."""
        new_inst = Linode.find(api_id=self.api_id)
        for attr in self.direct_attrs:
            setattr(self, attr.local_name, getattr(new_inst, attr.local_name))
        del new_inst

    def __repr__(self):
        return "<Linode api_id=%d, label='%s'>" % (self.api_id, self.label)


class LinodeTest:
    """Suite of integration tests to run when `chube test Linode` is called."""
    @classmethod
    def run(cls):
        import random

        print "~~~ Listing all Linodes"
        print
        linode_objs = Linode.search()
        print linode_objs
        print

        sample_linode_obj = random.sample(linode_objs, 1)[0]

        linode_obj_id = sample_linode_obj.api_id
        print "~~~ Fetching linode_obj '%s' by Linode ID" % (sample_linode_obj.label)
        print
        linode_obj = Linode.find(api_id=linode_obj_id)
        print "api_id = %d" % (linode_obj.api_id,)
        print "datacenter_id = %d" % (linode_obj.datacenter_id,)
        print "label = '%s'" % (linode_obj.label,)
        print "display_group = '%s'" % (linode_obj.display_group,)
        print "create_dt = '%s'" % (linode_obj.create_dt)
        print
        assert linode_obj.api_id == sample_linode_obj.api_id
        assert linode_obj.watchdog == sample_linode_obj.watchdog

        print "~~~ Refreshing the Linode '%s'" % (linode_obj.label)
        print
        linode_obj.refresh()
        print linode_obj
        print

        print "~~~ Tests passed!"
