from decimal import Decimal

from .api import api_handler
from .model import *
from .util import RequiresParams

class Plan(Model):
    direct_attrs = [
        DirectAttr("api_id", u"PLANID", int, int),
        DirectAttr("disk", u"DISK", int, int),
        DirectAttr("ram", u"RAM", int, int),
        DirectAttr("label", u"LABEL", unicode, unicode),
        DirectAttr("price", u"PRICE", Decimal, Decimal),
        DirectAttr("xfer", u"XFER", int, int),
    ]

    @classmethod
    def list(cls):
        return [cls.from_api_dict(d) for d in api_handler.avail_linodeplans()]

    def __repr__(self):
        return "<Plan label='%s'>" % self.label
