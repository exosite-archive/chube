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


class NodebalancerConfig(Model):
    direct_attrs = [
        # IDs
        DirectAttr("api_id", u"CONFIGID", int, int,
                   update_as="configid"),
        DirectAttr("nodebalancer_id", u"NODEBALANCERID", int, int),

        # Properties
        DirectAttr("algorithm", u"ALGORITHM", unicode, unicode,
                   update_as="algorithm"),
        DirectAttr("check", u"CHECK", unicode, unicode,
                   update_as="check"),
        DirectAttr("check_attempts", u"CHECK_ATTEMPTS", unicode, unicode,
                   update_as="check_attempts"),
        DirectAttr("check_body", u"CHECK_BODY", unicode, unicode,
                   update_as="check_body"),
        DirectAttr("check_interval", u"CHECK_INTERVAL", int, int,
                   update_as="check_interval"),
        DirectAttr("check_path", u"CHECK_PATH", unicode, unicode,
                   update_as="check_path"),
        DirectAttr("check_timeout", u"CHECK_TIMEOUT", unicode, unicode,
                   update_as="check_timeout"),
        DirectAttr("port", u"PORT", int, int,
                   update_as="port"),
        DirectAttr("protocol", u"PROTOCOL", unicode, unicode,
                   update_as="protocol"),
        DirectAttr("stickiness", u"STICKINESS", unicode, unicode,
                   update_as="stickiness")
    ]

    # The `nodebalancer` attribute is done with a deferred lookup.
    def _nodebalancer_getter(self):
        return Nodebalancer.find(api_id=self.nodebalancer_id)
    def _nodebalancer_setter(self, val):
        raise NotImplementedError("Cannot assign NodebalancerConfig to a different Nodebalancer")
    nodebalancer = property(_nodebalancer_getter, _nodebalancer_setter)

    @classmethod
    @RequiresParams("nodebalancer")
    def create(cls, **kwargs):
        """Creates a new NodebalancerConfig.

           `nodebalancer`: Either a Nodebalancer object or a numeric Linode ID."""
        nodebalancer = kwargs["nodebalancer"]
        if type(nodebalancer) is not int: nodebalancer = nodebalancer.api_id
        rval = api_handler.nodebalancer_config_create(nodebalancerid=nodebalancer)
        print rval
        new_config_id = rval[u"ConfigID"]
        return cls.find(api_id=new_config_id, nodebalancer=nodebalancer)

    @classmethod
    @RequiresParams("nodebalancer")
    def search(cls, **kwargs):
        """Returns the list of NodebalancerConfig instances that match the given criteria.
        
           At least `nodebalancer` is required. It can be a Nodebalancer object or a numeric
           Nodebalancer ID."""
        nodebalancer = kwargs["nodebalancer"]
        if type(nodebalancer) is not int: nodebalancer = nodebalancer.api_id
        a = [cls.from_api_dict(d) for d in api_handler.nodebalancer_config_list(nodebalancerid=nodebalancer)]
        del kwargs["nodebalancer"]

        for k, v in kwargs.items():
            a = [conf for conf in a if getattr(conf, k) == v]
        return a

    @classmethod
    @RequiresParams("api_id", "nodebalancer")
    def find(cls, **kwargs):
        """Returns a single NodebalancerConfig instance that matches the given criteria.

           For example, `NodebalancerConfig.find(api_id=102382061, nodebalancer=819201)`.

           Both parameters are required. `nodebalancer` may be a Nodebalancer ID or a Nodebalancer object."""
        nodebalancer = kwargs["nodebalancer"]
        if type(nodebalancer) is not int: nodebalancer = nodebalancer.api_id
        a = [cls.from_api_dict(d) for d in api_handler.nodebalancer_config_list(nodebalancerid=nodebalancer, configid=kwargs["api_id"])]
        return a[0]

    def save(self):
        """Saves the NodebalancerConfig object to the API."""
        api_params = self.api_update_params()
        api_handler.nodebalancer_config_update(**api_params)

    def refresh(self):
        """Refreshes the NodebalancerConfig object with a new API call."""
        new_inst = NodebalancerConfig.find(api_id=self.api_id, nodebalancer=self.nodebalancer_id)
        for attr in self.direct_attrs:
            setattr(self, attr.local_name, getattr(new_inst, attr.local_name))
        del new_inst

    def destroy(self):
        """Deletes the NodebalancerConfig object."""
        api_handler.nodebalancer_config_delete(configid=self.api_id)

    def __repr__(self):
        return "<NodebalancerConfig api_id=%d, protocol='%s', port='%s'>" % (self.api_id, self.protocol, self.port)


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


        print "~~~ Searching for that nodebalancer"
        print
        searched_nb = Nodebalancer.find(hostname=nodebalancer.hostname)
        assert searched_nb.api_id == nodebalancer.api_id
        assert searched_nb.client_conn_throttle == nodebalancer.client_conn_throttle


        print "~~~ Refreshing nodebalancer from API"
        print
        nodebalancer.refresh()
        print nodebalancer
        print "client_conn_throttle = %d" % (nodebalancer.client_conn_throttle,)
        print
        assert nodebalancer.label == nodebalancer_name
        assert nodebalancer.client_conn_throttle == 17

        
        print "~~~ Creating config for nodebalancer"
        print
        conf = NodebalancerConfig.create(nodebalancer=nodebalancer)
        print
        print conf
        print "nodebalancer = %s" % (conf.nodebalancer,)
        print


        print "~~~ Setting protocol and port for config and saving"
        print
        conf.protocol = "tcp"
        conf.port = 11210
        conf.save()


        print "~~~ Searching for that config"
        print
        searched_conf = NodebalancerConfig.search(nodebalancer=nodebalancer)[0]
        assert searched_conf.api_id == conf.api_id


        print "~~~ Destroying config '%s'" % (repr(conf))
        print 
        conf.destroy()


        print "~~~ Destroying nodebalancer '%s'" % (nodebalancer.label,)
        print
        nodebalancer.destroy()

        print "~~~ Tests passed!"
