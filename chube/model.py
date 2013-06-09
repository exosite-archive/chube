class DirectAttr:
    """A model attribute that comes straight from the API."""
    def __init__(self, local_name, api_name, local_type, api_type, update_as=None):
        """Initializes the DirectAttr instance.

           `local_name`: The name we'll use for the attribute locally (e.g. "label" or
               "requires_pvops")
           `api_name`: The used by the API for the attribute (e.g. u"LABEL" or u"REQUIRESPVOPS")
           `local_type`: The type of object we'll use locally for the attribute (e.g. `bool` or
               `FooObject`)
           `api_type`: The type of object the API expects for the attribute (e.g. `int` or
               `unicode`)
           `update_as`: The name of the API parameter to pass this value as when updating it.
               If `None`, then this attribute will be excluded from saves."""
        self.local_name = local_name
        self.api_name = api_name
        self.local_type = local_type
        self.api_type = api_type
        self.update_as = update_as

    def is_savable(self):
        return (self.update_as is not None)


class Model(object):
    direct_attrs = []

    @classmethod
    def from_api_dict(cls, api_dict):
        """Factory method that instantiates Model subclasses from API-returned dicts."""
        inst = cls()
        for attr in cls.direct_attrs:
            try:
                api_value = api_dict[attr.api_name]
            except KeyError:
                raise KeyError("API did not return required '%s' value for '%s' object" %
                               (attr.api_name, cls.__name__))
            setattr(inst, attr.local_name, attr.local_type(api_value))
        return inst
