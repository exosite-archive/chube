from chube.util import *
from chube.api_obj import *


class LinodeCreator(APIObjectCreator):
    """Creates Linode objects via the API."""
    @RequiresParams("datacenter", "plan", "payment_term")
    def create(self, **kwargs):
        """Creates a Linode object by calling the API, and returns it.

           `datacenter`: A Datacenter object indicating where to create the Linode.
           `plan`: A Plan object indicating the payment plan of the Linode.
           `payment_term`: Subscription in terms of months. 1, 12, or 24."""
        datacenter = kwargs["datacenter"]
        plan = kwargs["plan"]
        payment_term = kwargs["payment_term"]

        rval = self._api_handler.linode_create(
            datacenterid=datacenter.api_id,
            planid=plan.api_id,
            paymentterm=payment_term
        )
        linode_id = rval[u"LinodeID"]

        linode = self._apiobj_cls.find(api_id=linode_id)
        return linode


class LinodeSaver(APIObjectSaver):
    """Saves Linode objects via the API."""
    def save(self, linode):
        """Saves the Linode.

           `linode`: A Linode instance."""
        return self._api_handler.linode_update(
            linodeid=linode.api_id,
            label=unicode(linode.label),
            lpm_displaygroup=unicode(linode.lpm_displaygroup),
            alert_cpu_enabled=linode.alert_cpu_enabled,
            alert_diskio_enabled=linode.alert_diskio_enabled,
            alert_bwin_enabled=linode.alert_bwin_enabled,
            alert_bwin_threshold=linode.alert_bwin_threshold,
            alert_bwout_enabled=linode.alert_bwout_enabled,
            alert_bwout_threshold=linode.alert_bwout_threshold,
            alert_bwquota_enabled=linode.alert_bwquota_enabled,
            alert_bwquota_threshold=linode.alert_bwquota_threshold,
            backupwindow=linode.backupwindow,
            backupweeklyday=linode.backupweeklyday,
            watchdog=linode.watchdog
        )


class LinodeFinder(APIObjectFinder):
    """Fetches dicts from the API that correspond to Linodes."""
    def list_all(self):
        """Lists all relevant dicts from the API."""
        return self._api_handler.linode_list()


class LinodeReader(APIObjectReader):
    """Responsible for converting dicts returned by the API into Linode instances."""
    # Inherited defaults are fine


class Linode(APIObject):
    """A Linode."""
    creator_cls = LinodeCreator
    finder_cls = LinodeFinder
    reader_cls = LinodeReader
    saver_cls = LinodeSaver
