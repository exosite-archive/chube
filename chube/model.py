class DirectAttr:
    """A model attribute that comes straight from the API."""
    def __init__(self, local_name, api_name, local_type, api_type,
                 update_as=None, update_only_if_type=None,
                 may_be_absent=False, default=None):
        """Initializes the DirectAttr instance.

           `local_name`: The name we'll use for the attribute locally (e.g. "label" or
               "requires_pvops")
           `api_name`: The used in API responses for the attribute (e.g. u"LABEL" or
               u"REQUIRESPVOPS")
           `local_type`: The type of object we'll use locally for the attribute (e.g. `bool` or
               `FooObject`)
           `api_type`: The type of object the API expects for the attribute (e.g. `int` or
               `unicode`)
           `update_as`: The name of the API parameter to pass this value as when updating it.
               If `None`, then this attribute will be excluded from saves.
           `update_only_if_type`: Only include this parameter in a `save` call if its value is
               of the specified type. This is useful for attributes like Record.weight, where
               the API may return `u''` if the value is undefined but we can only save integers.
           `may_be_absent`: Allows this attribute to be absent from API responses. When this
               DirectAttr is absent from an API response, it will be assigned the value
               passed as `default`.
           `default`: Default value for this DirectAttr when `may_be_absent` is True and the
               attribute is absent from the API response."""
        self.local_name = local_name
        self.api_name = api_name
        self.local_type = local_type
        self.api_type = api_type
        self.update_as = update_as
        self.update_only_if_type = update_only_if_type
        self.may_be_absent = may_be_absent
        self.default = default

    def __repr__(self):
        return "<DirectAttr local_name='%s'>" % (self.local_name,)

    def is_savable(self, val):
        """Determines whether the attribute is savable in its current state.

           `val`: The locally-stored value for the attribute."""
        if self.update_as is None: return False
        if self.update_only_if_type is not None and type(val) is not self.update_only_if_type: return False
        return True


class Model(object):
    direct_attrs = []

    @classmethod
    def from_api_dict(cls, api_dict):
        """Factory method that instantiates Model subclasses from API-returned dicts."""
        inst = cls()

        for attr in cls.direct_attrs:
            if api_dict.has_key(attr.api_name):
                api_value = api_dict[attr.api_name]
            elif attr.may_be_absent:
                api_value = attr.default
            else:
                raise KeyError("API did not return required '%s' value for '%s' object" %
                               (attr.api_name, cls.__name__))
            setattr(inst, attr.local_name, attr.local_type(api_value))

        return inst


    def api_update_params(self):
        """Returns a dict that can be used as the arguments to a `*_update` API call."""
        api_params = {}
        for attr in self.direct_attrs:
            attr_value = getattr(self, attr.local_name)
            if not attr.is_savable(attr_value): continue
            api_params[attr.update_as] = attr.api_type(attr_value)

        return api_params
