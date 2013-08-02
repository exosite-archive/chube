from .api import api_handler
from .model import *
from .util import keywords_only

class Distribution(Model):
    direct_attrs = [
        DirectAttr("api_id", u"DISTRIBUTIONID", int, int),
        DirectAttr("label", u"LABEL", unicode, unicode),
        DirectAttr("create_dt", u"CREATE_DT", unicode, unicode),
        DirectAttr("min_image_size", u"MINIMAGESIZE", int, int),
        DirectAttr("is_64bit", u"IS64BIT", bool, int),
        DirectAttr("requires_pvops_distro", u"REQUIRESPVOPSKERNEL", bool, int)
    ]

    @classmethod
    @keywords_only
    def search(cls, **kwargs):
        """Returns the list of Distribution instances that match the given criteria.
 
           The special paramater `label_begins` allows you to case-insensitively
           match the beginning of the label string. For example,
           `Distribution.search(label_begins='Debian 7')`."""
        a = [cls.from_api_dict(d) for d in api_handler.avail_distributions()]
        if kwargs.has_key("label_begins"):
            a = [distro for distro in a if
                 distro.label.lower().startswith(kwargs["label_begins"].lower())]
            del kwargs["label_begins"]
        for k, v in kwargs.items():
            a = [distro for distro in a if getattr(distro, k) == v]
        return a

    @classmethod
    @keywords_only
    def find(cls, **kwargs):
        """Returns a single Distribution instance that matches the given criteria.

           For example, `Distribution.find(api_id=12)`.

           Raises an exception if there is not exactly one Distribution matching the criteria."""
        a = cls.search(**kwargs)
        if len(a) < 1: raise RuntimeError("No Distribution found with the given criteria (%s)" % (kwargs,))
        if len(a) > 1: raise RuntimeError("More than one Distribution found with the given criteria (%s)" % (kwargs,))
        return a[0]

    def refresh(self):
        """Refreshes the distro with a new API call."""
        new_inst = Distribution.find(api_id=self.api_id)
        for attr in self.direct_attrs:
            setattr(self, attr.local_name, getattr(new_inst, attr.local_name))
        del new_inst

    def __repr__(self):
        return "<Distribution label='%s'>" % self.label


class DistributionTest:
    """Suite of integration tests to run when `chube test Distribution` is called."""
    @classmethod
    def run(cls):
        import random

        print "~~~ Listing all distros"
        print
        distros = Distribution.search()
        print "~~~ %d distros listed" % (len(distros),)
        print

        sample_distro = random.sample(distros, 1)[0]

        distro_id = sample_distro.api_id
        print "~~~ Fetching distro '%s' by distro ID" % (sample_distro.label)
        print
        distro = Distribution.find(api_id=distro_id)
        print "api_id = %d" % (distro.api_id,)
        print "label = '%s'" % (distro.label,)
        print "is_64bit = %s" % (distro.is_64bit,)
        print
        assert distro.label == sample_distro.label

        print "~~~ Refreshing the distro '%s'" % (distro.label)
        print
        distro.refresh()
        assert distro.label == sample_distro.label

        print "~~~ Tests passed!"
