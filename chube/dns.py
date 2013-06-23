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
    def master_ips_getter(self):
        """Returns the zone's master DNS servers, as an array of IP addresses.
        
           The string given by the API is something like "127.0.0.1;127.0.0.2;". """
        ips = self.master_ips_str.rstrip(";").split(";")
        return ips
    def master_ips_setter(self, val):
        """Sets the zone's master DNS servers.

           `val`: A list of IP address strings."""
        self.master_ips_str = ";".join(val) + ";"
    master_ips = property(master_ips_getter, master_ips_setter)

    # The `axfr_ips` attribute is based on `axfr_ips_str`
    def axfr_ips_getter(self):
        """Returns the IP addresses allowed to AXFR the zone, as an array of strings.
        
           The string given by the API is something like "127.0.0.1;127.0.0.2;" """
        ips = self.axfr_ips_str.rstrip(";").split(";")
        return ips
    def axfr_ips_setter(self, val):
        """Sets the IP addresses allowed to AXFR the zone.

           `val`: A list of IP address strings."""
        self.axfr_ips_str = ";".join(val) + ";"
    axfr_ips = property(axfr_ips_getter, axfr_ips_setter)

    @classmethod
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

    def save(self):
        """Saves the Domain object to the API."""
        api_params = {}
        attrs = [attr for attr in self.direct_attrs if attr.is_savable()]
        for attr in attrs:
            api_params[attr.update_as] = attr.api_type(getattr(self, attr.local_name))
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

        print "~~~ Destroying domain '%s'" % (domain.domain,)
        print
        domain.destroy()

        print "~~~ Tests passed!"
