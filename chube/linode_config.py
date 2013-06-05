from chube.api_obj import *
from chube.util import *
from chube.job import Job


class LinodeConfigCreator(APIObjectCreator):
    """Creates LinodeConfig objects via the API."""
    def __init__(self, *args):
        """Initializes the LinodeConfigCreator."""
        super(self.__class__, self).__init__(*args)
        self._c = {"Job": Job}

    def inject_dep(self, inj_dict):
        """Injects dependencies (for testing).

           `inj_dict`: A dictionary of classes like {"RequiredClass": StubClass}."""
        self._c.update(inj_dict)

    @RequiresParams("linode_id", "label", "linode_config_type", "size")
    def create(self, **kwargs):
        """Creates a LinodeConfig object by calling the API, and returns it.

           `linode_id`: The LinodeID of the linode on which the linode_config will be created.
           `label`: The label of the linode_config.
           `linode_config_type`: LinodeConfig image type (at the time of this writing, "ext3", "swap", or "raw".
           `size`: LinodeConfig image size in MB."""
        linode_id = kwargs["linode_id"]
        label = kwargs["label"]
        linode_config_type = kwargs["disk_type"]
        size = kwargs["size"]

        rval = self._api_handler.linode_linode_config_create(
            linodeid=linode_id,
            label=label,
            type=linode_config_type,
            size=size
        )
        linode_config_id = rval[u"LinodeConfigID"]
        job_id = rval[u"JobID"]

        linode_config = self._apiobj_cls.find(api_id=disk_id)
        linode_config.creation_job = self._c["Job"].find(api_id=job_id)
        return linode_config


class LinodeConfigFinder(APIObjectFinder):
    """Fetches dicts from the API that correspond to LinodeConfigs."""
    def search_by_linode_id(self, linode_id):
        """Returns the linode_config dicts from the API that are associated with the given linode."""
        return self._api_handler.linode_config_list(linodeid=linode_id)

    def find_by_linode_config_id(self, linode_id, config_id):
        """Returns the dict for the single linode_config identified by the given parameters."""
        rslt = self._api_handler.linode_config_list(linodeid=linode_id, configid=config_id)
        if len(rslt) == 0:
            raise KeyError("No Linode config found with LinodeID %d and ConfigID %d" % (linode_id, config_id))
        return rslt[0]


class LinodeConfigReader(APIObjectReader):
    """Responsible for converting dicts returned by the API into LinodeConfig instances."""
    def translate_key_ConfigID(self):
        return "api_id"

    def translate_key_DiskList(self):
        return "disk_ids"
    def translate_value_DiskList(self, v):
        # Convert a string like u"1,2,3,,,,," to a list like [1,2,3,None,None,None,None,None]
        rslt = []
        strings = v.split(",")
        for s in strings:
            if s == "":
                rslt.append(None)
            else:
                rslt.append(int(s))
        return rslt

    def translate_key_isRescue(self): return "is_rescue"
    def translate_value_isRescue(self, v): return bool(v)


class LinodeConfig(APIObject):
    """A LinodeConfig."""
    creator_cls = LinodeConfigCreator
    finder_cls = LinodeConfigFinder
    reader_cls = LinodeConfigReader
    saver_cls = None

    @classmethod
    @RequiresParams("linode_id", "api_id")
    def find(cls, **kwargs):
        """Finds a specific LinodeConfig by querying the API.

           `linode_id` (required): The LinodeID of the Linode that owns the linode_config.
           `api_id` (required): The LinodeConfigID."""
        finder = cls.finder_cls(cls, chube.api.api_handler)
        linode_config_dict = finder.find_by_api_id(linode_id=kwargs["linode_id"], api_id=kwargs["api_id"])
        reader = cls.reader_cls(cls)
        return reader.read(linode_config_dict)

    @classmethod
    @RequiresParams("linode_id")
    def search(cls, **kwargs):
        """Lists LinodeConfigs by querying the API.

           `linode_id` (required): The LinodeID of the Linode whose linode_configs we should return."""
        finder = cls.finder_cls(cls, chube.api.api_handler)
        linode_config_dicts = finder.search_by_linode_id(linode_id=kwargs["linode_id"])
        reader = cls.finder_cls(cls, chube.api.api_handler)
        return map(reader.read, linode_config_dicts)
