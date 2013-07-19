"""Module for Nodebalancer-related models."""
from .api import api_handler
from .util import RequiresParams
from .model import *


class Nodebalancer(Model):
    direct_attrs = [
        # IDs
        DirectAttr("api_id", u"NODEBALANCERID", int, int,
                   update_as="nodebalancerid"),

        # Properties
        DirectAttr("label", u"LABEL", unicode, unicode,
                   update_as="label"),
        DirectAttr("client_conn_throttle", u"CLIENTCONNTHROTTLE", int, int,
                   update_as="clientconnthrottle"),
        DirectAttr("hostname", u"HOSTNAME", unicode, unicode),
        DirectAttr("address4", u"ADDRESS4", unicode, unicode),
        DirectAttr("address6", u"ADDRESS6", unicode, unicode),
        DirectAttr("status", u"STATUS", unicode, unicode,
                   may_be_absent=True, default=u"")
    ]

    @classmethod
    def search(cls, **kwargs):
        """Returns the list of Nodebalancer instances that match the given criteria.
        
           The special paramater `label_begins` allows you to case-insensitively
           match the beginning of the `label` string. For example,
           `Nodebalancer.search(label_begins='fremont-')`."""
        a = [cls.from_api_dict(d) for d in api_handler.nodebalancer_list()]
        if kwargs.has_key("label_begins"):
            a = [nodebalancer for nodebalancer in a if
                 nodebalancer.label.lower().startswith(kwargs["label_begins"].lower())]
            del kwargs["label_begins"]
        for k, v in kwargs.items():
            a = [nodebalancer for nodebalancer in a if getattr(nodebalancer, k) == v]
        return a

    @classmethod
    def find(cls, **kwargs):
        """Returns a single Nodebalancer instance that matches the given criteria.

           For example, `Nodebalancer.find(label="fremont-nb-00")`.

           Raises an exception if there is not exactly one Nodebalancer matching the criteria."""
        a = cls.search(**kwargs)
        if len(a) < 1: raise RuntimeError("No Nodebalancer found with the given criteria (%s)" % (kwargs,))
        if len(a) > 1: raise RuntimeError("More than one Nodebalancer found with the given criteria (%s)" % (kwargs,))
        return a[0]

    @classmethod
    @RequiresParams("datacenter", "payment_term")
    def create(cls, **kwargs):
        """Creates a new Nodebalancer.

           `datacenter` (required): The datacenter in which to create the nodebalancer.
               It can be a Datacenter object or a numeric Datacenter ID.
           `payment_term` (required): An integer number of months that represents a
               valid Nodebalancer payment term (1, 12, or 24 at the time of this writing.)"""
        datacenter, payment_term = (kwargs["datacenter"], kwargs["payment_term"])
        if type(datacenter) is not int: datacenter = datacenter.api_id
        rval = api_handler.nodebalancer_create(datacenterid=datacenter, paymentterm=payment_term)
        new_nodebalancer_id = rval[u"NodeBalancerID"]
        return cls.find(api_id=new_nodebalancer_id)

    def save(self):
        """Saves the Nodebalancer object to the API."""
        api_params = self.api_update_params()
        api_handler.nodebalancer_update(**api_params)

    def refresh(self):
        """Refreshes the Nodebalancer object with a new API call."""
        new_inst = Nodebalancer.find(api_id=self.api_id)
        for attr in self.direct_attrs:
            setattr(self, attr.local_name, getattr(new_inst, attr.local_name))
        del new_inst

    def destroy(self):
        """Deletes the Nodebalancer."""
        api_handler.nodebalancer_delete(nodebalancerid=self.api_id)

    def __repr__(self):
        return "<Nodebalancer api_id=%d, label='%s'>" % (self.api_id, self.label)


class NodebalancerTest:
    """Suite of integration tests to run when `chube test Nodebalancer` is called."""
    @classmethod
    def run(cls):
        import random
        from .datacenter import Datacenter

        SUFFIX_CHARS = "abcdefghijklmnopqrtuvwxyz023456789"
        SUFFIX_LEN = 8
        nodebalancer_suffix = "".join(random.sample(SUFFIX_CHARS, SUFFIX_LEN))
        nodebalancer_name = "chube-test-%s" % (nodebalancer_suffix,)

        dc = Datacenter.find(location_begins="dallas")
        print "~~~ Creating Nodebalancer '%s'" % (nodebalancer_name,)
        print
        nodebalancer = Nodebalancer.create(datacenter=dc, payment_term=1)
        print nodebalancer
        print
        print "hostname = '%s'" % (nodebalancer.hostname,)
        print "address4 = '%s'" % (nodebalancer.address4,)
        print "status = '%s'" % (nodebalancer.status,)
        print

        print "~~~ Setting nodebalancer's label and connection throttling"
        print
        nodebalancer.label = nodebalancer_name
        nodebalancer.client_conn_throttle = 17
        print "~~~ Saving change"
        print
        nodebalancer.save()
        print "~~~ Refreshing nodebalancer from API"
        print
        nodebalancer.refresh()
        print nodebalancer
        print "client_conn_throttle = %d" % (nodebalancer.client_conn_throttle,)
        print
        assert nodebalancer.label == nodebalancer_name
        assert nodebalancer.client_conn_throttle == 17

        print "~~~ Destroying nodebalancer '%s'" % (nodebalancer.label,)
        print
        nodebalancer.destroy()

        print "~~~ Tests passed!"
