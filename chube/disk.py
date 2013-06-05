from chube.api_obj import *
from chube.util import *
from chube.job import Job


class DiskCreator(APIObjectCreator):
    """Creates Disk objects via the API."""
    def __init__(self, *args):
        """Initializes the DiskCreator."""
        super(self.__class__, self).__init__(*args)
        self._c = {"Job": Job}

    def inject_dep(self, inj_dict):
        """Injects dependencies (for testing).

           `inj_dict`: A dictionary of classes like {"RequiredClass": StubClass}."""
        self._c.update(inj_dict)

    @RequiresParams("linode_id", "label", "disk_type", "size")
    def create(self, **kwargs):
        """Creates a Disk object by calling the API, and returns it.

           `linode_id`: The LinodeID of the linode on which the disk will be created.
           `label`: The label of the disk.
           `disk_type`: Disk image type (at the time of this writing, "ext3", "swap", or "raw".
           `size`: Disk image size in MB."""
        linode_id = kwargs["linode_id"]
        label = kwargs["label"]
        disk_type = kwargs["disk_type"]
        size = kwargs["size"]

        rval = self._api_handler.linode_disk_create(
            linodeid=linode_id,
            label=label,
            type=disk_type,
            size=size
        )
        disk_id = rval[u"DiskID"]
        job_id = rval[u"JobID"]

        disk = self._apiobj_cls.find(api_id=disk_id)
        disk.creation_job = self._c["Job"].find(api_id=job_id)
        return disk


class DiskFinder(APIObjectFinder):
    """Fetches dicts from the API that correspond to Disks."""
    def search_by_linode_id(self, linode_id):
        """Returns the disk dicts from the API that are associated with the given linode."""
        return self._api_handler.linode_disk_list(linodeid=linode_id)

    def find_by_disk_id(self, linode_id, disk_id):
        """Returns the dict for the single disk identified by the given parameters."""
        rslt = self._api_handler.linode_disk_list(linodeid=linode_id, diskid=disk_id)
        if len(rslt) == 0:
            raise KeyError("No disk found with LinodeID %d and DiskID %d" % (linode_id, disk_id))
        return rslt[0]


class DiskReader(APIObjectReader):
    """Responsible for converting dicts returned by the API into Disk instances."""
    # Inherited defaults are fine


class Disk(APIObject):
    """A Disk."""
    creator_cls = DiskCreator
    finder_cls = DiskFinder
    reader_cls = DiskReader
    saver_cls = None

    @classmethod
    @RequiresParams("linode_id", "api_id")
    def find(cls, **kwargs):
        """Finds a specific Disk by querying the API.

           `linode_id` (required): The LinodeID of the Linode that owns the disk.
           `api_id` (required): The DiskID."""
        finder = cls.finder_cls(cls, chube.api.api_handler)
        disk_dict = finder.find_by_api_id(linode_id=kwargs["linode_id"], api_id=kwargs["api_id"])
        reader = cls.reader_cls(cls)
        return reader.read(disk_dict)


    
    @classmethod
    @RequiresParams("linode_id")
    def search(cls, **kwargs):
        """Lists Disks by querying the API.

           `linode_id` (required): The LinodeID of the Linode whose disks we should return."""
        finder = cls.finder_cls(cls, chube.api.api_handler)
        disk_dicts = finder.search_by_linode_id(linode_id=kwargs["linode_id"])
        reader = cls.finder_cls(cls, chube.api.api_handler)
        return map(reader.read, disk_dicts)
