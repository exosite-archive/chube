from chube.api_obj import *

class DistributionFinder(APIObjectFinder):
    """Fetches dicts from the API that correspond to Linode distributions."""
    def list_all(self):
        """Lists all relevant dicts from the API."""
        return self._api_handler.avail_distributions()

class DistributionReader(APIObjectReader):
    """Responsible for converting dicts returned by the API into Distribution instances."""
    # Inherited defaults are fine

class Distribution(APIObject):
    """A Linode distribution."""
    finder_cls = DistributionFinder
    reader_cls = DistributionReader
