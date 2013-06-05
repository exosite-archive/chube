from chube.api_obj import *

class PlanFinder(APIObjectFinder):
    """Fetches dicts from the API that correspond to Linode payment plans."""
    def list_all(self):
        """Lists all relevant dicts from the API."""
        return self._api_handler.avail_linodeplans()

    def find_by_ram(self, ram):
        """Returns the first result found from the API that has the given amount of RAM.
        
           `ram`: An integer number of MB.
           
           Returns a raw dict from the API, nothing more. Raises KeyError if none is found."""
        plans = self.list_all()
        matches = [p_dict for p_dict in plans if p_dict[u"RAM"] == ram]
        if len(matches) == 0:
            raise KeyError("No such Linode plan with %dMB of RAM" % (ram,))
        return matches[0]


class PlanReader(APIObjectReader):
    """Responsible for converting dicts returned by the API into Plan instances."""
    # Inherited defaults are fine

class Plan(APIObject):
    """A Linode type (a payment plan)."""
    LINODE_RESERVED_PROPORTION = 0.02

    finder_cls = PlanFinder
    reader_cls = PlanReader
    creator_cls = None
    saver_cls = None

    @property
    def max_image_size(self):
        """Returns an estimate of the max image size for the plan.

           Linode reserves some space on the disk, so it's not exactly DISK * 1024."""
        disk_mb = self.disk * 1024
        return int(disk_mb * (1.0 - self.LINODE_RESERVED_PROPORTION))
