import time

import chube.api
from chube.api_obj import *
from chube.util import *


class JobFinder(APIObjectFinder):
    """Fetches dicts from the API that correspond to Jobs."""
    def search_by_linode_id(self, linode_id):
        """Returns the job dicts from the API that are associated with the given linode."""
        return self._api_handler.linode_job_list(linodeid=linode_id)

    def find_by_api_id(self, linode_id, api_id):
        """Returns the dict for the single job identified by the given parameters."""
        rslt = self._api_handler.linode_job_list(linodeid=linode_id, jobid=api_id)
        if len(rslt) == 0:
            raise KeyError("No job found with LinodeID %d and JobID %d" % (linode_id, api_id))
        return rslt[0]

class JobReader(APIObjectReader):
    """Turns Job dictionaries from the API into Job objects."""
    # Inherited defaults are fine


class Job(APIObject):
    """A Job in the API."""
    creator_cls = None
    finder_cls = JobFinder
    reader_cls = JobReader
    saver_cls = None

    @classmethod
    @RequiresParams("linode_id", "api_id")
    def find(cls, **kwargs):
        """Finds a specific Job by querying the API.

           `linode_id` (required): The LinodeID of the Linode that owns the disk.
           `api_id` (required): The JobID."""
        finder = cls.finder_cls(cls, chube.api.api_handler)
        job_dict = finder.find_by_api_id(linode_id=kwargs["linode_id"], api_id=kwargs["api_id"])
        reader = cls.reader_cls(cls)
        return reader.read(job_dict)


    def is_done(self):
        """Determines whether the job has completed successfully."""
        return (self.host_success == 1)

    def is_failed(self):
        """Determines whether the job has failed."""
        return (self.host_success == 0)

    def wait(self, timeout=120, check_interval=5):
        """Returns when the job is finished.

           `timeout`: Number of seconds to wait before giving up.
           `check_interval`: How often to check, in seconds.

           Raises a `RuntimeError` if the timeout is reached. Raises a `ValueError`
           if the job fails."""
        t = 0
        while t <= timeout:
            # We use `while` instead of `for t in range(...)` because we want to be able
            # to use a floating-point `check_interval`.
            self.update()
            if self.is_failed():
                raise ValueError("Job '%s' on Linode %d failed" % (self.label, self.linode_id))
            if self.is_done():
                return
            time.sleep(check_interval)
            t += check_interval
        raise RuntimeError("Job '%s' on Linode %d took longer than %d seconds to complete; aborting." % (self.label, self.linode_id, timeout))
