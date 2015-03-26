"""Module for DNS-related models."""
from .api import api_handler
from .util import RequiresParams, keywords_only
from .model import *


class Domain(Model):
    direct_attrs = [
        # IDs
        DirectAttr("api_id", u"DOMAINID", int, int,
                   update_as="domainid"),

        # Properties
        DirectAttr("domain", u"DOMAIN", unicode, unicode,
                   update_as="domain"),
        DirectAttr("description", u"DESCRIPTION", unicode, unicode,
                   update_as="description"),
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
    def _master_ips_getter(self):
        """Returns the zone's master DNS servers, as an array of IP addresses.
        
           The string given by the API is something like "127.0.0.1;127.0.0.2;". """
        ips = self.master_ips_str.rstrip(";").split(";")
        # API returns ['"none"'] or ['none'] if there are no IPs authorized.
        if ips == [u'"none"'] or ips == [u"none"]: return []
        return ips
    def _master_ips_setter(self, val):
        """Sets the zone's master DNS servers.

           `val`: A list of IP address strings."""
        self.master_ips_str = ";".join(val)
    master_ips = property(_master_ips_getter, _master_ips_setter)

    # The `axfr_ips` attribute is based on `axfr_ips_str`
    def _axfr_ips_getter(self):
        """Returns the IP addresses allowed to AXFR the zone, as an array of strings.
        
           The string given by the API is something like "127.0.0.1;127.0.0.2;" """
        ips = self.axfr_ips_str.rstrip(";").split(";")
        # API returns ['"none"'] or ['none'] if there are no IPs authorized.
        if ips == [u'"none"'] or ips == [u"none"]: return []
        return ips
    def _axfr_ips_setter(self, val):
        """Sets the IP addresses allowed to AXFR the zone.

           `val`: A list of IP address strings."""
        self.axfr_ips_str = ";".join(val)
    axfr_ips = property(_axfr_ips_getter, _axfr_ips_setter)

    @classmethod
    @keywords_only
    def search(cls, **kwargs):
        """Returns the list of Domain instances that match the given criteria.
        
           The special paramater `domain_begins` allows you to case-insensitively
           match the beginning of the `domain` string. For example,
           `Domain.search(domain_begins='www.')`.
           
           The `domain_ends` parameter is analogous. For example,
           `Domain.search(domain_ends='.org')`."""
        a = [cls.from_api_dict(d) for d in api_handler.domain_list()]
        if kwargs.has_key("domain_begins"):
            a = [domain for domain in a if
                 domain.domain.lower().startswith(kwargs["domain_begins"].lower())]
            del kwargs["domain_begins"]
        if kwargs.has_key("domain_ends"):
            a = [domain for domain in a if
                 domain.domain.lower().endswith(kwargs["domain_ends"].lower())]
            del kwargs["domain_ends"]
        for k, v in kwargs.items():
            a = [domain for domain in a if getattr(domain, k) == v]
        return a

    @classmethod
    @keywords_only
    def find(cls, **kwargs):
        """Returns a single Domain instance that matches the given criteria.

           For example, `Domain.find(domain="www.example.com")`.

           Raises an exception if there is not exactly one Domain matching the criteria."""
        a = cls.search(**kwargs)
        if len(a) < 1: raise RuntimeError("No Domain found with the given criteria (%s)" % (kwargs,))
        if len(a) > 1: raise RuntimeError("More than one Domain found with the given criteria (%s)" % (kwargs,))
        return a[0]

    @classmethod
    @RequiresParams("domain", "zone_type")
    @keywords_only
    def create(cls, **kwargs):
        """Creates a new Domain.

           `domain` (required): The domain's hostname (e.g. "example.com")
           `zone_type` (required): "master" or "slave" 
           `soa_email` (required if type is 'master'): The email address to put in the
               zone's SOA record."""
        domain, zone_type = (kwargs["domain"], kwargs["zone_type"])
        api_args = {"domain": domain, "type": zone_type}
        if zone_type == "master":
            try:
                api_args["soa_email"] = kwargs["soa_email"]
            except KeyError:
                raise KeyError("Parameter `soa_email` is required when zone type is 'master')")
        rval = api_handler.domain_create(**api_args)
        new_domain_id = rval[u"DomainID"]
        return cls.find(api_id=new_domain_id)

    @RequiresParams("record_type")
    @keywords_only
    def add_record(self, **kwargs):
        """Adds a DNS record to the domain.

           `record_type` (required): "A", "MX", "CNAME", etc.
           `name` (optional): The left-hand side of the DNS record.
           `target` (optional): The right-hand side of the DNS record.
           `ttl_sec` (optional): The TTL in seconds. 0 for Linode's default."""
        api_args = {"domainid": self.api_id}
        api_args["type"] = kwargs["record_type"]
        if kwargs.has_key("name"): api_args["name"] = kwargs["name"]
        if kwargs.has_key("target"): api_args["target"] = kwargs["target"]
        if kwargs.has_key("ttl_sec"): api_args["ttl_sec"] = kwargs["ttl_sec"]
        if kwargs.has_key("priority"): api_args["priority"] = kwargs["priority"]
        rval = api_handler.domain_resource_create(**api_args)
        return Record.find(domain=self.api_id, api_id=rval["ResourceID"])

    @keywords_only
    @keywords_only
    def search_records(self, **kwargs):
        """Returns the list of Record instances that match the given criteria.
        
           Has a special `name_begins` parameter that does what you'd expect."""
        a = [Record.from_api_dict(api_dict) for api_dict in api_handler.domain_resource_list(domainid=self.api_id)]
        if kwargs.has_key("name_begins"):
            a = [record for record in a if record.name.lower().startswith(kwargs["name_begins"].lower())]
            del kwargs["name_begins"]
        for k, v in kwargs.items():
            a = [record for record in a if getattr(record, k) == v]
        return a

    @keywords_only
    def find_record(self, **kwargs):
        """Returns a single Record instance that matches the given criteria.
 
           Raises an exception if there's not exactly one match."""
        a = self.search_records(**kwargs)
        if len(a) < 1: raise RuntimeError("No Record found with the given criteria (%s)" % (kwargs,))
        if len(a) > 1: raise RuntimeError("More than one Record found with the given criteria (%s)" % (kwargs,))
        return a[0]

    def save(self):
        """Saves the Domain object to the API."""
        api_params = self.api_update_params()
        api_handler.domain_update(**api_params)

    def refresh(self):
        """Refreshes the Domain object with a new API call."""
        new_inst = Domain.find(api_id=self.api_id)
        for attr in self.direct_attrs:
            setattr(self, attr.local_name, getattr(new_inst, attr.local_name))
        del new_inst

    def destroy(self):
        """Deletes the Domain."""
        api_handler.domain_delete(domainid=self.api_id)

    def __repr__(self):
        return "<Domain api_id=%d, domain='%s'>" % (self.api_id, self.domain)


class Record(Model):
    direct_attrs = [
        # IDs
        DirectAttr("api_id", u"RESOURCEID", int, int,
                   update_as="resourceid"),
        DirectAttr("domain_id", u"DOMAINID", int, int,
                   update_as="domainid"),

        # Properties
        DirectAttr("record_type", u"TYPE", unicode, unicode,
                   update_as="type"),
        DirectAttr("name", u"NAME", unicode, unicode,
                   update_as="name"),
        DirectAttr("target", u"TARGET", unicode, unicode,
                   update_as="target"),
        DirectAttr("ttl_sec", u"TTL_SEC", int, int,
                   update_as="ttl_sec"),

        # These can come back as either the empty string or an int, so we
        # like to massage it as a property before giving it to the user.
        DirectAttr("_weight_api_val", u"WEIGHT", unicode, unicode,
                   update_as="weight", update_only_if_type=int),
        DirectAttr("_port_api_val", u"PORT", unicode, unicode,
                   update_as="port", update_only_if_type=int),
        DirectAttr("_priority_api_val", u"PRIORITY", unicode, unicode,
                   update_as="priority", update_only_if_type=int),
    ]

    # The `domain` attribute is done with a deferred lookup.
    def _domain_getter(self):
        return Domain.find(api_id=self.domain_id)
    def _domain_setter(self, val):
        raise NotImplementedError("Cannot assign Record to a different Domain")
    domain = property(_domain_getter, _domain_setter)

    # The `weight` attribute needs to be massaged before returning it to the
    # user. It can come back from the API either as an empty string or an int.
    def weight_getter(self):
        if self._weight_api_val == u"":
            return None
        return int(self._weight_api_val)
    def weight_setter(self, val):
        self._weight_api_val = int(val)
    weight = property(weight_getter, weight_setter)

    # See the comments for the `weight` property. Same deal.
    def port_getter(self):
        if self._port_api_val == u"":
            return None
        return int(self._port_api_val)
    def port_setter(self, val):
        self._port_api_val = int(val)
    port = property(port_getter, port_setter)

    # See the comments for the `weight` property. Same deal.
    def priority_getter(self):
        if self._priority_api_val == u"":
            return None
        return int(self._priority_api_val)
    def priority_setter(self, val):
        self._priority_api_val = int(val)
    priority = property(priority_getter, priority_setter)

    @classmethod
    @keywords_only
    def create(cls, **kwargs):
        """DNS records can't be created directly. Use `Domain.add_record()` instead."""
        raise NotImplementedError(cls.__doc__)

    @classmethod
    @RequiresParams("domain")
    @keywords_only
    def search(cls, **kwargs):
        """Returns the list of Record instances that match the given criteria.
        
           At least `domain` is required. It can be a Domain object or a numeric Domain ID."""
        domain = kwargs["domain"]
        if type(domain) is not int: domain = domain.api_id
        a = [cls.from_api_dict(d) for d in api_handler.domain_resource_list(domainid=domain)]
        del kwargs["domain"]

        for k, v in kwargs.items():
            a = [addr for addr in a if getattr(addr, k) == v]
        return a

    @classmethod
    @RequiresParams("domain")
    @keywords_only
    def find(cls, **kwargs):
        """Returns a single Record instance that matches the given criteria.

           For example, `Record.find(api_id=82061, domain=9201)`.

           Both parameters are required. `domain` may be a Domain ID or a Domain object."""
        a = cls.search(**kwargs)
        if len(a) < 1: raise RuntimeError("No Domain found with the given criteria (%s)" % (kwargs,))
        if len(a) > 1: raise RuntimeError("More than one Domain found with the given criteria (%s)" % (kwargs,))
        return a[0]

    def save(self):
        """Saves the Record object to the API."""
        api_params = self.api_update_params()
        api_handler.domain_resource_update(**api_params)

    def refresh(self):
        """Refreshes the Record object with a new API call."""
        new_inst = Record.find(api_id=self.api_id, domain=self.domain_id)
        for attr in self.direct_attrs:
            setattr(self, attr.local_name, getattr(new_inst, attr.local_name))
        del new_inst

    def destroy(self):
        """Destroys the DNS record."""
        api_handler.domain_resource_delete(domainid=self.domain_id, resourceid=self.api_id)

    def __repr__(self):
        return "<Record api_id=%d, record_type='%s', name='%s'>" % (self.api_id, self.record_type, self.name)


class DomainTest:
    """Suite of integration tests to run when `chube test Domain` is called."""
    @classmethod
    def run(cls):
        import random

        SUFFIX_CHARS = "abcdefghijklmnopqrtuvwxyz023456789"
        SUFFIX_LEN = 8
        domain_suffix = "".join(random.sample(SUFFIX_CHARS, SUFFIX_LEN))
        domain_name = "chube-test-%s.com" % (domain_suffix,)

        print "~~~ Creating Domain '%s'" % (domain_name,)
        print
        domain = Domain.create(domain=domain_name, zone_type="master", soa_email="admin@example.com")
        print domain
        print
        print "domain = %s" % (domain.domain,)
        print "ttl_sec = %s" % (domain.ttl_sec,)
        print

        print "~~~ Setting domain's TTL and axfr_ips"
        print
        domain.ttl_sec = 300
        domain.axfr_ips = ["127.0.0.1", "127.0.0.2"]
        print "~~~ Saving change"
        print
        domain.save()
        print "~~~ Refreshing domain from API"
        print
        domain.refresh()
        print domain
        print "ttl_sec = %d" % (domain.ttl_sec,)
        print "axfr_ips = %s" % (repr(domain.axfr_ips),)
        assert domain.axfr_ips_str in ["127.0.0.1;127.0.0.2;", "127.0.0.2;127.0.0.1;"]
        print
        print "~~~ Removing AXFR IPs"
        print
        domain.axfr_ips = []
        domain.save()
        domain.refresh()
        assert domain.axfr_ips_str in ["", "none", '"none"']


        print "~~~ Searching for domains"
        print
        print "~~~ By prefix"
        print
        rslt = Domain.search(domain_begins=domain.domain[:-2])
        print rslt
        print
        assert [d for d in Domain.search() if d.api_id == domain.api_id]
        print "~~~ By suffix"
        print
        rslt = Domain.search(domain_ends=domain.domain[2:])
        print rslt
        print
        assert [d for d in Domain.search() if d.api_id == domain.api_id]

        print "~~~ Creating A record 'foo.%s' => 127.0.0.1" % (domain.domain,)
        print
        r = domain.add_record(record_type="A", name="foo", target="127.0.0.1")
        print r
        print

        print "~~~ Changing the target of record 'foo.%s' to 127.0.0.2" % (domain.domain,)
        print
        r.target = "127.0.0.2"
        r.save()

        print "~~~ Creating CNAME record 'bar.%s' => 'foo.%s'" % (domain.domain,domain.domain,)
        print
        r = domain.add_record(record_type="CNAME", name="bar", target=("foo.%s" % (domain.domain,)))
        print r
        print

        print "~~~ Checking domain on CNAME record '%s'" % (r.name,)
        print
        print r.domain
        print
        assert r.domain.domain == domain.domain

        print "~~~ Destroying CNAME record '%s' => '%s'" % (r.name,r.target,)
        print
        r.destroy()
        assert r.api_id not in [r.api_id for r in domain.search_records()]

        print "~~~ Destroying domain '%s'" % (domain.domain,)
        print
        domain.destroy()

        print "~~~ Tests passed!"
