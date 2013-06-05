from chube.api_obj import *

class DatacenterFinder(APIObjectFinder):
    """Fetches dicts from the API that correspond to Linode datacenters."""
    def list_all(self):
        """Lists all relevant dicts from the API."""
        return self._api_handler.avail_datacenters()

    def find_by_location(self, location_prefix):
        """Returns the API dict whose u"LOCATION" value starts with the given prefix (case-insensitive)."""
        dicts = self.list_all()
        location_prefix = location_prefix.lower()
        for d in dicts:
            d_location = d[u"LOCATION"].lower()
            if d_location.startswith(location_prefix):
                return d
        raise KeyError("No datacenter with location beginning '%s'" % (location_prefix))

class DatacenterReader(APIObjectReader):
    """Responsible for converting dicts returned by the API into Datacenter instances."""
    # Inherited defaults are fine

class Datacenter(APIObject):
    """A Linode datacenter."""
    finder_cls = DatacenterFinder
    reader_cls = DatacenterReader
