from .api import api_handler
from .model import *
from .util import keywords_only

class Datacenter(Model):
    direct_attrs = [
        DirectAttr("api_id", u"DATACENTERID", int, int),
        DirectAttr("location", u"LOCATION", unicode, unicode),
    ]

    @classmethod
    @keywords_only
    def search(cls, **kwargs):
        """Returns the list of Datacenter instances that match the given criteria.

           The special paramater `location_begins` allows you to case-insensitively
           match the beginning of the location string. For example,
           `Datacenter.search(location_begins='dallas')`."""
        a = [cls.from_api_dict(d) for d in api_handler.avail_datacenters()]
        if kwargs.has_key("location_begins"):
            a = [datacenter for datacenter in a if
                 datacenter.location.lower().startswith(kwargs["location_begins"].lower())]
            del kwargs["location_begins"]
        for k, v in kwargs.items():
            a = [datacenter for datacenter in a if getattr(datacenter, k) == v]
        return a

    @classmethod
    @keywords_only
    def find(cls, **kwargs):
        """Returns a single Datacenter instance that matches the given criteria.

           For example, `Datacenter.find(api_id=4)`.

           Raises an exception if there is not exactly one Datacenter matching the criteria."""
        a = cls.search(**kwargs)
        if len(a) < 1: raise RuntimeError("No Datacenter found with the given criteria (%s)" % (kwargs,))
        if len(a) > 1: raise RuntimeError("More than one Datacenter found with the given criteria (%s)" % (kwargs,))
        return a[0]

    def refresh(self):
        """Refreshes the datacenter with a new API call."""
        new_inst = Datacenter.find(api_id=self.api_id)
        for attr in self.direct_attrs:
            setattr(self, attr.local_name, getattr(new_inst, attr.local_name))
        del new_inst

    def __repr__(self):
        return "<Datacenter location='%s'>" % self.location


class DatacenterTest:
    """Suite of integration tests to run when `chube test Datacenter` is called."""
    @classmethod
    def run(cls):
        import random

        print "~~~ Listing all datacenters"
        print
        datacenters = Datacenter.search()
        print datacenters
        print

        sample_datacenter = random.sample(datacenters, 1)[0]

        datacenter_id = sample_datacenter.api_id
        print "~~~ Fetching datacenter '%s' by datacenter ID" % (sample_datacenter.location)
        print
        datacenter = Datacenter.find(api_id=datacenter_id)
        print "api_id = %d" % (datacenter.api_id,)
        print "location = %s" % (datacenter.location,)
        print
        assert datacenter.location == sample_datacenter.location

        print "~~~ Fetching datacenter with location starting 'dallas'"
        print
        datacenter = Datacenter.find(location_begins="dallas")
        print datacenter
        print
        assert datacenter.location == u"Dallas, TX, USA"

        print "~~~ Refreshing the datacenter '%s'" % (datacenter.location)
        print
        datacenter.refresh()
        print datacenter
        print
        assert datacenter.location == u"Dallas, TX, USA"

        print "~~~ Tests passed!"
