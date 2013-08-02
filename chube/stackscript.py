"""Module for the Stackscript model."""
import json

from .api import api_handler
from .util import RequiresParams, keywords_only
from .model import *
from .distribution import Distribution


class StackscriptInput:
    """The inputs required by a Stackscript.
    
       Use like
       
           ssi = StackscriptInput(blah="1", foo="2,3,4")
           ssi.add_input("bar", "baz")"""
    def __init__(self, **kwargs):
        self._responses = kwargs
    def add_input(self, name, val):
        self._responses[name] = val
    def __str__(self):
        return json.dumps(self._responses)


class Stackscript(Model):
    direct_attrs = [
        # IDs
        DirectAttr("api_id", u"STACKSCRIPTID", int, int,
                   update_as="stackscriptid"),
        DirectAttr("distribution_id_list", u"DISTRIBUTIONIDLIST", unicode, unicode,
                   update_as="distributionidlist"),

        # Properties
        DirectAttr("label", u"LABEL", unicode, unicode,
                   update_as="label"),
        DirectAttr("description", u"DESCRIPTION", unicode, unicode,
                   update_as="description"),
        DirectAttr("script", u"SCRIPT", unicode, unicode,
                   update_as="script"),
        DirectAttr("is_public", u"ISPUBLIC", bool, int,
                   update_as="ispublic"),
        DirectAttr("rev_note", u"REV_NOTE", unicode, unicode,
                   update_as="rev_note"),

        # Dynamic values
        DirectAttr("latest_rev", u"LATESTREV", int, int),
        DirectAttr("rev_dt", u"REV_DT", unicode, unicode),
        DirectAttr("create_dt", u"CREATE_DT", unicode, unicode),
        DirectAttr("user_id", u"USERID", int, int),
        DirectAttr("deployments_active", u"DEPLOYMENTSACTIVE", int, int),
        DirectAttr("deployments_total", u"DEPLOYMENTSTOTAL", int, int)
    ]

    # The `distributions` attribute is based on `distribution_id_list`
    def _distributions_getter(self):
        """Returns the list of distributions associated with the Stackscript."""
        distributions = []
        for distribution_id in self.distribution_id_list.split(","):
            distributions.append(Distribution.find(linode=self.linode_id, api_id=int(distribution_id)))
        return distributions
    def _distributions_setter(self, val):
        """Updates the list of distributions associated with the configuration.

           `val`: An 8-element list of Distribution objects."""
        distribution_ids = []
        for distribution in val:
            distribution_ids.append(distribution.api_id)
        self.distribution_id_list = ",".join(map(str, distribution_ids))
    distributions = property(_distributions_getter, _distributions_setter)

    @classmethod
    @keywords_only
    def search(cls, **kwargs):
        """Returns the list of Stackscript instances that match the given criteria.
        
           The special paramater `label_begins` allows you to case-insensitively
           match the beginning of the label string. For example,
           `Stackscript.search(label_begins='web-')`."""
        a = [cls.from_api_dict(d) for d in api_handler.stackscript_list()]
        if kwargs.has_key("label_begins"):
            a = [stackscript for stackscript in a if
                 stackscript.label.lower().startswith(kwargs["label_begins"].lower())]
            del kwargs["label_begins"]
        for k, v in kwargs.items():
            a = [stackscript for stackscript in a if getattr(stackscript, k) == v]
        return a

    @classmethod
    @keywords_only
    def find(cls, **kwargs):
        """Returns a single Stackscript instance that matches the given criteria.

           For example, `Stackscript.find(api_id=4)`.

           Raises an exception if there is not exactly one Stackscript matching the criteria."""
        a = cls.search(**kwargs)
        if len(a) < 1: raise RuntimeError("No Stackscript found with the given criteria (%s)" % (kwargs,))
        if len(a) > 1: raise RuntimeError("More than one Stackscript found with the given criteria (%s)" % (kwargs,))
        return a[0]

    @classmethod
    @RequiresParams("label", "distributions", "script")
    @keywords_only
    def create(cls, **kwargs):
        """Creates a new Stackscript.

           `label` (required): The name of the new stackscript.
           `distributions` (required): An array of either Distribution objects or numeric
               Distribution IDs.
           `script` (required): The contents of the stackscript.
           `description` (optional): A summary of what the stackscript does.
           `is_public` (optional): Whether the stackscript should be listed publicly
               (default: False)
           `rev_note` (optional): A note about the first revision of the stackscript."""
        label, distributions, script = (kwargs["label"], kwargs["distributions"], kwargs["script"])
        distribution_ids = []
        for d in distributions:
            if type(d) is int: distribution_ids.append(d)
            else: distribution_ids.append(d.api_id)
        distribution_id_list = ",".join(map(str, distribution_ids))

        api_args = {"label": label, "distributionidlist": distribution_id_list,
                    "script": script}
        for k in ("description", "is_public", "rev_note"):
            if kwargs.has_key(k):
                api_args[k] = kwargs[k]

        rval = api_handler.stackscript_create(**api_args)
        new_stackscript_id = rval[u"StackScriptID"]
        return cls.find(api_id=new_stackscript_id)

    def save(self):
        """Saves the Stackscript object to the API."""
        api_params = self.api_update_params()
        api_handler.stackscript_update(**api_params)

    def refresh(self):
        """Refreshes the Stackscript object with a new API call."""
        new_inst = Stackscript.find(api_id=self.api_id)
        for attr in self.direct_attrs:
            setattr(self, attr.local_name, getattr(new_inst, attr.local_name))
        del new_inst

    def destroy(self):
        """Deletes the Stackscript."""
        api_handler.stackscript_delete(stackscriptid=self.api_id)

    def __repr__(self):
        return "<Stackscript api_id=%d, label='%s'>" % (self.api_id, self.label)


class StackscriptTest:
    """Suite of integration tests to run when `chube test Stackscript` is called."""
    @classmethod
    def run(cls):
        import random

        SUFFIX_CHARS = "abcdefghijklmnopqrtuvwxyz023456789"
        SUFFIX_LEN = 8
        stackscript_suffix = "".join(random.sample(SUFFIX_CHARS, SUFFIX_LEN))
        stackscript_name = "chube-test-%s" % (stackscript_suffix,)

        print "~~~ Creating Stackscript '%s'" % (stackscript_name,)
        print
        ss = Stackscript.create(label=stackscript_name,
                                distributions=Distribution.search(label_begins=u"Debian "),
                                script=u"#!/bin/bash\n\n/bin/true")
        print ss
        print


        print "~~~ Updating Stackscript '%s' with a new script and a revision note" % (ss.label)
        print
        ss.script = u"#!/bin/bash\n\n/bin/false"
        ss.rev_note = "Shbibbity bop!"
        ss.save()

        
        print "~~~ Listing our stackscripts"
        print
        rslt = Stackscript.search(is_public=False)
        print rslt
        print
        assert([s for s in rslt if ss.api_id == s.api_id])


        print "~~~ Finding the stackscript we just created"
        print
        ss = Stackscript.find(api_id=ss.api_id)
        print ss
        print


        print "~~~ Refreshing the stackscript"
        print
        ss.refresh()


        print "~~~ Deleting the stackscript '%s'" % (ss.label,)
        ss.destroy()
