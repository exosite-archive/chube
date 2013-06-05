import chube.api

class APIObjectCreator(object):
    """Abstract for a class that creates a new API object."""
    def __init__(self, apiobj_cls, api_handler):
        self._apiobj_cls = apiobj_cls
        self._api_handler = api_handler


class APIObjectSaver(object):
    """Abstract for a class that updates an API object (when you use save())."""
    def __init__(self, apiobj_cls, api_handler):
        self._apiobj_cls = apiobj_cls
        self._api_handler = api_handler


class APIObjectFinder(object):
    """Abstract for a class that finds raw dicts with given parameters from the API.
    
       Classes of this type are NOT responsible for converting these dicts to APIObjects."""

    def __init__(self, apiobj_cls, api_handler):
        self._apiobj_cls = apiobj_cls
        self._api_handler = api_handler

    def find_by_api_id(self, api_id):
        """Returns the API dict with the given value for its API ID.
        
           For example, if the subclass is Plan, we'll search for the u"PLANID" key."""
        id_key = unicode(self._apiobj_cls.__name__.upper() + "ID")
        dicts = self.list_all()
        matches = [d for d in dicts if d[id_key] == api_id]
        if len(matches) == 0:
            raise KeyError("No %s object with API ID '%d'" % (self._apiobj_cls.__name__, api_id))
        return matches[0]

    def find_by_label(self, label):
        """Returns the API dict with the given value for the u"LABEL" key."""
        dicts = self.list_all()
        matches = [d for d in dicts if d[u"LABEL"] == label]
        if len(matches) == 0:
            raise KeyError("No object with label '%s'" % (label))
        return matches[0]

    def find_by_label_starts(self, label_prefix, ignore_case=False):
        """Returns the API dict whose u"LABEL" value starts with the given prefix.

           `ignore_case`: Whether the match should be case-insensitive."""
        dicts = self.list_all()
        for d in dicts:
            d_label = d[u"LABEL"]
            if ignore_case:
                label_prefix = label_prefix.lower()
                d_label = d_label.lower()
            if d_label.startswith(label_prefix):
                return d
        raise KeyError("No object with label beginning '%s'" % (label_prefix))


class APIObjectReader(object):
    """Abstract for a class that converts API-returned dicts into API object instances."""
    def __init__(self, apiobj_cls):
        """Initializes the APIObjectReader subclass.

           `apiobj_cls`: The class of the APIObject we'll be generating, e.g. `Plan`."""
        self._apiobj_cls = apiobj_cls

    def _translate_key(self, key):
        """Converts the given API dict key to a Python-appropriate attr name.
        
           `key`: A key from an API-returned dict, e.g. `PLANID` or `ISPVOPS`.
           
           Here's a handy table of how this conversion works, under the assumption
           that apiobj_cls is `Disk`:
               
               Dict Key             Attribute Name
               LABEL                label
               LINODEID             linode_id
               DISKID               api_id
               ISREADONLY           is_readonly
               REQUIRESPVOPSKERNEL  requires_pvopskernel
               
           These rules can be overridden by adding methods to the subclass named
           `translate_key_KEYNAME`."""
        cls_name = self._apiobj_cls.__name__
        if hasattr(self, "translate_key_" + key):
            return getattr(self, "translate_key_" + key)()
        if key == cls_name.upper() + u"ID":
            key = "api_id"

        if key.startswith(u"IS"):
            if key[2] != "_": key = key[:2] + "_" + key[2:]
        if key.startswith(u"REQUIRES"):
            if key[8] != "_": key = key[:8] + "_" + key[8:]
        if key.startswith(u"TOTAL"):
            if key[5] != "_": key = key[:5] + "_" + key[5:]

        if key.endswith(u"ID"):
            if key[-3] != "_": key = key[:-2] + "_" + key[-2:]
        if key.endswith(u"ENABLED"):
            if key[-8] != "_": key = key[:-7] + "_" + key[-7:]

        return key.lower()

    def _translate_value(self, key, value):
        """Translates a value to the appropriate Python type.

           `key`: The key from the API dict.
           `value': The value in the API dict.
               
           The default rules can be overridden by adding methods to the subclass
           named `translate_key_KEYNAME`."""
        if hasattr(self, "translate_value_" + key):
            return getattr(self, "translate_value_" + key)(value)
        if key.startswith(u"IS"):
            return bool(value)
        if key.startswith(u"REQUIRES"):
            return bool(value)
        if key.endswith(u"ENABLED"):
            return bool(value)
        return value

    def read(self, api_dict, target=None):
        """Populates the given API object instance with the data read from the API-returned dict.

           `apiobj_cls`: The APIObject-descended class of which we're building an instance (e.g.
               `Plan` or `Linode`).
           `api_dict`: A dict of the type returned by the API.
           `target` (optional): An object of the appropriate class to modify instead of creating
               a new object."""
        if target is None:
            apiobj = self._apiobj_cls()
        else:
            apiobj = target

        for k, v in api_dict.items():
            attr_name = self._translate_key(k)
            attr_val = self._translate_value(k, v)
            setattr(apiobj, attr_name, attr_val)
        return apiobj


class APIObject(object):
    """Abstract for an object generated from (or representing) API data."""
    creator_cls = None
    finder_cls = None
    reader_cls = None
    creator_cls = None

    @classmethod
    def create(cls, **kwargs):
        """Creates an object of the subclass's type by querying the API.
        
           Provide any named arguments required by the class's Creator. See the corresponding
           Creator's unit test for an example."""
        if cls.creator_cls is None:
            raise NotImplementedError("'%s' objects cannot be created via the API" % (cls.__name__))
        creator = cls.creator_cls(cls, chube.api.api_handler)
        return creator.create(**kwargs)

    @classmethod
    def search(cls, **kwargs):
        """Finds all objects of the subclass's type by querying the API."""
        finder = cls.finder_cls(cls, chube.api.api_handler)
        api_dicts = finder.list_all()
        reader = cls.reader_cls(cls)
        return [reader.read(api_dict) for api_dict in api_dicts]


    @classmethod
    def find(cls, **kwargs):
        """Finds an object of the subclass's type by querying the API.

           Provide one named argument. The corresponding `find_by_<keyname>`
           method of the specified `finder_cls` will be called to generate an
           instance of the appropriate APIObject subclass.

           See `PlanFinder.find_by_ram` for an example."""
        k, v = kwargs.items()[0]
        # Fetch raw dict from API
        finder = cls.finder_cls(cls, chube.api.api_handler)
        find_method = getattr(finder, "find_by_" + k)
        api_dict = find_method(v)
        # Convert that dict to an object
        reader = cls.reader_cls(cls)
        obj = reader.read(api_dict)
        return obj

    def update(self):
        """Loads attributes afresh from the API."""
        finder = self.finder_cls(self.__class__, chube.api.api_handler)
        api_dict = finder.find_by_api_id(linode_id=self.linode_id, api_id=self.api_id)
        reader = self.reader_cls(self.__class__)
        reader.read(api_dict, target=self)

    def save(self):
        """Saves all attributes to the API."""
        if self.saver_cls is None:
            raise NotImplementedError("'%s' objects cannot be saved to the API" % (cls.__name__))
        saver = self.saver_cls(self.__class__, chube.api.api_handler)
        saver.save(self)

    def __repr__(self):
        """Represents the object to the user for interactive use."""
        clsname = self.__class__.__name__
        if hasattr(self, "label"):
            return "<%s label='%s'>" % (clsname, self.label)
        elif hasattr(self, "location"):
            return "<%s location='%s'>" % (clsname, self.location)
        elif hasattr(self, "api_id"):
            return "<%s api_id=%d>" % (clsname, self.api_id)
        return "<clsname object>" % (clsname,)
