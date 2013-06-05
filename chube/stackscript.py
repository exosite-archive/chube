from chube.api_obj import *
from chube.util import *

import json

class StackscriptInput:
    """The inputs required by a StackScript."""
    def __init__(self, **kwargs):
        self._responses = kwargs
    def add_input(self, name, val):
        self._responses[name] = val
    def __str__(self):
        return json.dumps(self._responses)


class StackscriptCreator(APIObjectCreator):
    """Creates Stackscript objects via the API."""
    @RequiresParams("label", "distributions", "script")
    def create(self, **kwargs):
        """Creates a Stackscript object by calling the API, and returns it.

           `label`: The name of the new stackscript.
           `distributions`: A list of Distribution objects for which the stackscript is valid.
           `script` The content of the script.
           
           `description` (optional): A blurb describing the stackscript's purpose.
           `is_public` (optional): Whether the script should be published to the Linode
               stackscript repository. Default: False.
           `rev_note` (optional): A note about this particular revision of the stackscript."""
        label = kwargs["label"]
        distributions = kwargs["distributions"]
        script = kwargs["script"]

        description, is_public, rev_note = (u'', False, u'')
        if kwargs.has_key("description"): description = kwargs["description"]
        if kwargs.has_key("is_public"): is_public = kwargs["is_public"]
        if kwargs.has_key("rev_note"): rev_note = kwargs["rev_note"]

        rval = self._api_handler.stackscript_create(
            label=label,
            distributionidlist=u",".join(map(str, [dist.api_id for dist in distributions])),
            script=script,
            description=description,
            is_public=is_public,
            rev_note=rev_note
        )
        stackscript_id = rval[u"StackScriptID"]

        stackscript = self._apiobj_cls.find(api_id=stackscript_id)
        return stackscript


class StackscriptSaver(APIObjectSaver):
    """Saves Stackscript objects via the API."""
    def save(self, stackscript):
        """Saves the Stackscript.

           `stackscript`: A Stackscript instance."""
        return self._api_handler.stackscript_update(
            stackscriptid=stackscript.api_id,
            label=unicode(stackscript.label),
            description=unicode(stackscript.description),
            distributionidlist=u",".join(map(str, stackscript.distribution_ids)),
            ispublic=stackscript.is_public,
            rev_note=stackscript.rev_note,
            script=stackscript.script
        )


class StackscriptFinder(APIObjectFinder):
    """Fetches dicts from the API that correspond to Stackscripts."""
    def list_all(self):
        """Lists all relevant dicts from the API."""
        return self._api_handler.stackscript_list()

    def find_by_api_id(self, api_id):
        """Lists only the Stackscript dict with the given ID.
        
           We override the abstract's method here because we can tell the API
           to return this specific Stackscript, instead of getting all and
           looping through them."""
        rslt = self._api_handler.stackscript_list(stackscriptid=api_id)
        if len(rslt) == 0: raise KeyError("No Stackscript with ID %d" % (api_id))
        return rslt[0]


class StackscriptReader(APIObjectReader):
    """Responsible for converting dicts returned by the API into Stackscript instances."""
    def translate_key_DISTRIBUTIONIDLIST(self):
        return "distribution_ids"

    def translate_value_DISTRIBUTIONIDLIST(self, value):
        return map(int, value.split(","))


class Stackscript(APIObject):
    """A Stackscript."""
    creator_cls = StackscriptCreator
    finder_cls = StackscriptFinder
    reader_cls = StackscriptReader
    saver_cls = StackscriptSaver
