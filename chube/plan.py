from decimal import Decimal

from .api import api_handler
from .model import *
from .util import keywords_only

class Plan(Model):
    direct_attrs = [
        DirectAttr("api_id", u"PLANID", int, int),
        DirectAttr("disk", u"DISK", int, int),
        DirectAttr("ram", u"RAM", int, int),
        DirectAttr("label", u"LABEL", unicode, unicode),
        DirectAttr("price", u"PRICE", Decimal, Decimal),
        DirectAttr("xfer", u"XFER", int, int),
    ]

    @classmethod
    @keywords_only
    def search(cls, **kwargs):
        """Returns the list of all Plan instances."""
        a = [cls.from_api_dict(d) for d in api_handler.avail_linodeplans()]
        for k, v in kwargs.items():
            a = [plan for plan in a if getattr(plan, k) == v]
        return a

    @classmethod
    @keywords_only
    def find(cls, **kwargs):
        """Returns a single Plan instance that matches the given criteria.

           For example, `Plan.find(api_id=4)`.

           Raises an exception if there is not exactly one Plan matching the criteria."""
        a = cls.search(**kwargs)
        if len(a) < 1: raise RuntimeError("No Plan found with the given criteria (%s)" % (kwargs,))
        if len(a) > 1: raise RuntimeError("More than one Plan found with the given criteria (%s)" % (kwargs,))
        return a[0]

    def refresh(self):
        """Refreshes the plan with a new API call."""
        new_inst = Plan.find(api_id=self.api_id)
        for attr in self.direct_attrs:
            setattr(self, attr.local_name, getattr(new_inst, attr.local_name))
        del new_inst

    def __repr__(self):
        return "<Plan label='%s'>" % self.label


class PlanTest:
    """Suite of integration tests to run when `chube test Plan` is called."""
    @classmethod
    def run(cls):
        import random

        print "~~~ Listing all plans"
        print
        plans = Plan.search()
        print plans
        print

        sample_plan = random.sample(plans, 1)[0]

        plan_id = sample_plan.api_id
        print "~~~ Fetching plan '%s' by plan ID" % (sample_plan.label)
        print
        plan = Plan.find(api_id=plan_id)
        print "api_id = %d" % (plan.api_id,)
        print "disk = %d" % (plan.disk,)
        print "ram = %d" % (plan.ram,)
        print "label = %s" % (plan.label,)
        print "price = %0.2f" % (plan.price,)
        print "xfer = %d" % (plan.xfer,)
        print
        assert plan.label == sample_plan.label

        print "~~~ Fetching plan with 2048 MB of RAM"
        print
        plan = Plan.find(ram=2048)
        assert plan.label == u"Linode 2048"

        print "~~~ Refreshing the plan '%s'" % (plan.label)
        print
        plan.refresh()
        assert plan.label == u"Linode 2048"

        print "~~~ Tests passed!"
