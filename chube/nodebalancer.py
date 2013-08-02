"""Module for Nodebalancer-related models."""
from .api import api_handler
from .util import RequiresParams, keywords_only
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
    @keywords_only
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
    @keywords_only
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
    @keywords_only
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

    # The `configs` attribute
    def _configs_getter(self):
        return NodebalancerConfig.search(nodebalancer=self.api_id)
    def _configs_setter(self, val):
        raise NotImplementedError("Cannot set `configs` directly; use `add_config` instead.")
    configs = property(_configs_getter, _configs_setter)

    @keywords_only
    def add_config(self, **kwargs):
        """Creates a new NodebalancerConfig for the Nodebalancer and returns it."""
        return NodebalancerConfig.create(nodebalancer=self.api_id)

    @keywords_only
    def search_configs(self, **kwargs):
        """Returns the list of NodebalancerConfig instances that match the given criteria."""
        a = [NodebalancerConfig.from_api_dict(api_dict) for api_dict in api_handler.nodebalancer_config_list(nodebalancerid=self.api_id)]
        for k, v in kwargs.items():
            a = [config for config in a if getattr(config, k) == v]
        return a

    @keywords_only
    def find_config(self, **kwargs):
        """Returns a single NodebalancerConfig instance that matches the given criteria.

           Raises an exception if there's not exactly one match."""
        a = self.search_configs(**kwargs)
        if len(a) < 1: raise RuntimeError("No NodebalancerConfig found with the given criteria (%s)" % (kwargs,))
        if len(a) > 1: raise RuntimeError("More than one NodebalancerConfig found with the given criteria (%s)" % (kwargs,))
        return a[0]

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
    @keywords_only
    def create(cls, **kwargs):
        """Creates a new NodebalancerConfig.

           `nodebalancer`: Either a Nodebalancer object or a numeric Nodebalancer ID."""
        nodebalancer = kwargs["nodebalancer"]
        if type(nodebalancer) is not int: nodebalancer = nodebalancer.api_id
        rval = api_handler.nodebalancer_config_create(nodebalancerid=nodebalancer)
        new_config_id = rval[u"ConfigID"]
        return cls.find(api_id=new_config_id, nodebalancer=nodebalancer)

    @classmethod
    @RequiresParams("nodebalancer")
    @keywords_only
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
    @keywords_only
    def find(cls, **kwargs):
        """Returns a single NodebalancerConfig instance that matches the given criteria.

           For example, `NodebalancerConfig.find(api_id=102382061, nodebalancer=819201)`.

           Both parameters are required. `nodebalancer` may be a Nodebalancer ID or a Nodebalancer object."""
        nodebalancer = kwargs["nodebalancer"]
        if type(nodebalancer) is not int: nodebalancer = nodebalancer.api_id
        a = [cls.from_api_dict(d) for d in api_handler.nodebalancer_config_list(nodebalancerid=nodebalancer, configid=kwargs["api_id"])]
        return a[0]

    # The `nodes` attribute
    def _nodes_getter(self):
        return NodebalancerNode.search(config=self.api_id)
    def _nodes_setter(self, val):
        raise NotImplementedError("Cannot set `nodes` directly; use `add_node` instead.")
    nodes = property(_nodes_getter, _nodes_setter)

    @RequiresParams("label", "address")
    @keywords_only
    def add_node(self, **kwargs):
        """Creates a new Node for the Nodebalancer and returns it.

           See NodebalancerNode.create.__doc__ for param info."""
        return NodebalancerNode.create(config=self.api_id, label=kwargs["label"], address=kwargs["address"])

    @keywords_only
    def search_nodes(self, **kwargs):
        """Returns the list of NodebalancerNode instances that match the given criteria."""
        a = [NodebalancerNode.from_api_dict(api_dict) for api_dict in api_handler.nodebalancer_node_list(configid=self.api_id)]
        for k, v in kwargs.items():
            a = [config for config in a if getattr(config, k) == v]
        return a

    @keywords_only
    def find_node(self, **kwargs):
        """Returns a single NodebalancerNode instance that matches the given criteria.

           Raises an exception if there's not exactly one match."""
        a = self.search_nodes(**kwargs)
        if len(a) < 1: raise RuntimeError("No NodebalancerNode found with the given criteria (%s)" % (kwargs,))
        if len(a) > 1: raise RuntimeError("More than one NodebalancerNode found with the given criteria (%s)" % (kwargs,))
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


class NodebalancerNode(Model):
    direct_attrs = [
        # IDs
        DirectAttr("api_id", u"NODEID", int, int,
                   update_as="nodeid"),
        DirectAttr("config_id", u"CONFIGID", int, int),
        DirectAttr("nodebalancer_id", u"NODEBALANCERID", int, int),

        # Properties
        DirectAttr("weight", u"WEIGHT", int, int,
                   update_as="weight"),
        DirectAttr("address", u"ADDRESS", unicode, unicode,
                   update_as="address"),
        DirectAttr("label", u"LABEL", unicode, unicode,
                   update_as="label"),
        DirectAttr("mode", u"MODE", unicode, unicode,
                   update_as="mode"),
        DirectAttr("status", u"STATUS", unicode, unicode)
    ]

    # The `config` attribute is done with a deferred lookup.
    def _config_getter(self):
        return NodebalancerConfig.find(api_id=self.config_id)
    def _config_setter(self, val):
        raise NotImplementedError("Cannot assign NodebalancerNode to a different NodebalancerConfig")
    config = property(_config_getter, _config_setter)

    # The `nodebalancer` attribute is done with a deferred lookup.
    def _nodebalancer_getter(self):
        return Nodebalancer.find(api_id=self.nodebalancer_id)
    def _nodebalancer_setter(self, val):
        raise NotImplementedError("Cannot assign NodebalancerNode to a different Nodebalancer")
    nodebalancer = property(_nodebalancer_getter, _nodebalancer_setter)

    @classmethod
    @RequiresParams("config", "label", "address")
    @keywords_only
    def create(cls, **kwargs):
        """Creates a new NodebalancerNode.

           `config` (required): Either a NodebalancerConfig object or a numeric Config ID.
           `label` (required): A label for the new NodebalancerNode.
           `address` (required): The address:port combination for communication with the node."""
        config, label, address = kwargs["config"], kwargs["label"], kwargs["address"]
        if type(config) is not int: config = config.api_id
        rval = api_handler.nodebalancer_node_create(configid=config, label=label, address=address)
        new_node_id = rval[u"NodeID"]
        return cls.find(api_id=new_node_id, config=config)

    @classmethod
    @RequiresParams("config")
    @keywords_only
    def search(cls, **kwargs):
        """Returns the list of NodebalancerNode instances that match the given criteria.
        
           At least `config` is required. It can be a NodebalancerConfig object or a numeric
           Config ID.
           
           The special paramater `label_begins` allows you to case-insensitively match the
           beginning of the label string. For example,
           `NodebalancerNode.search(config=my_conf, label_begins='web-')`."""
        config = kwargs["config"]
        if type(config) is not int: config = config.api_id
        a = [cls.from_api_dict(d) for d in api_handler.nodebalancer_node_list(configid=config)]
        del kwargs["config"]

        if kwargs.has_key("label_begins"):
            a = [linode_obj for linode_obj in a if
                 linode_obj.label.lower().startswith(kwargs["label_begins"].lower())]
            del kwargs["label_begins"]

        for k, v in kwargs.items():
            a = [conf for conf in a if getattr(conf, k) == v]
        return a

    @classmethod
    @RequiresParams("config")
    @keywords_only
    def find(cls, **kwargs):
        """Returns a single NodebalancerNode instance that matches the given criteria.

           For example, `NodebalancerNode.find(config=819201, label='fhwgwhgds')`.

           `config` (required) may be a Config ID or a Config object."""
        a = cls.search(**kwargs)
        if len(a) < 1: raise RuntimeError("No NodeBalancerNode found with the given criteria (%s)" % (kwargs,))
        if len(a) > 1: raise RuntimeError("More than one NodeBalancerNode found with the given criteria (%s)" % (kwargs,))
        return a[0]

    def save(self):
        """Saves the NodebalancerNode object to the API."""
        api_params = self.api_update_params()
        api_handler.nodebalancer_node_update(**api_params)

    def refresh(self):
        """Refreshes the NodebalancerNode object with a new API call."""
        new_inst = NodebalancerNode.find(api_id=self.api_id, config=self.config_id)
        for attr in self.direct_attrs:
            setattr(self, attr.local_name, getattr(new_inst, attr.local_name))
        del new_inst

    def destroy(self):
        """Deletes the NodebalancerNode object."""
        api_handler.nodebalancer_node_delete(nodeid=self.api_id)

    def __repr__(self):
        return "<NodebalancerNode api_id=%d, label='%s'>" % (self.api_id, self.label)


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
        conf = nodebalancer.add_config()
        print conf
        print "nodebalancer = %s" % (conf.nodebalancer,)
        print


        print "~~~ Setting protocol and port for config and saving"
        print
        conf.protocol = "tcp"
        conf.port = 11210
        conf.save()


        print "~~~ Listing Nodebalancer configs"
        print
        conf_list = nodebalancer.configs
        print conf_list
        print
        assert conf.api_id in [c.api_id for c in conf_list]


        print "~~~ Searching for that config"
        print
        searched_conf = nodebalancer.find_config(port=conf.port)
        assert searched_conf.api_id == conf.api_id


        node_suffix = "".join(random.sample(SUFFIX_CHARS, SUFFIX_LEN))
        node_name = "chube-test-%s" % (node_suffix,)
        print "~~~ Adding node '%s' to the config" % (node_name,)
        print
        node = conf.add_node(label=node_name, address="192.168.127.127:53")
        print node
        print

        
        print "~~~ Changing the node's weight"
        print
        node.weight = 119
        node.save()
        

        print "~~~ Listing Config's nodes"
        print
        node_list = conf.nodes
        print node_list
        print
        assert node.api_id in [n.api_id for n in node_list]


        print "~~~ Searching for the node"
        print
        searched_node = conf.find_node(api_id=node.api_id)
        assert node.weight == searched_node.weight
        assert node.label == searched_node.label


        print "~~~ Destroying node '%s'" % (node.label)
        print
        node.destroy()


        print "~~~ Destroying config '%s'" % (repr(conf))
        print 
        conf.destroy()


        print "~~~ Destroying nodebalancer '%s'" % (nodebalancer.label,)
        print
        nodebalancer.destroy()

        print "~~~ Tests passed!"
