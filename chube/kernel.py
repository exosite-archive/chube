from chube.api_obj import *

class KernelFinder(APIObjectFinder):
    """Fetches dicts from the API that correspond to Linode kernels."""
    def list_all(self):
        """Lists all relevant dicts from the API."""
        return self._api_handler.avail_kernels()

class KernelReader(APIObjectReader):
    """Responsible for converting dicts returned by the API into Kernel instances."""
    # Inherited defaults are fine

class Kernel(APIObject):
    """A Linode kernel."""
    finder_cls = KernelFinder
    reader_cls = KernelReader
