from .api import api_handler
from .model import *
from .util import keywords_only

class Kernel(Model):
    direct_attrs = [
        DirectAttr("api_id", u"KERNELID", int, int),
        DirectAttr("label", u"LABEL", unicode, unicode),
        DirectAttr("is_xen", u"ISXEN", bool, int),
        DirectAttr("is_pvops", u"ISPVOPS", bool, int)
    ]

    @classmethod
    @keywords_only
    def search(cls, **kwargs):
        """Returns the list of all Kernel instances that match the given criteria.

           The special paramater `label_begins` allows you to case-insensitively
           match the beginning of the label string. For example,
           `Kernel.search(label_begins='Latest 64 bit')`."""
        a = [cls.from_api_dict(d) for d in api_handler.avail_kernels()]
        if kwargs.has_key("label_begins"):
            a = [kernel for kernel in a if
                 kernel.label.lower().startswith(kwargs["label_begins"].lower())]
            del kwargs["label_begins"]
        for k, v in kwargs.items():
            a = [kernel for kernel in a if getattr(kernel, k) == v]
        return a

    @classmethod
    @keywords_only
    def find(cls, **kwargs):
        """Returns a single Kernel instance that matches the given criteria.

           For example, `Kernel.find(api_id=83)`.

           Raises an exception if there is not exactly one Kernel matching the criteria."""
        a = cls.search(**kwargs)
        if len(a) < 1: raise RuntimeError("No Kernel found with the given criteria (%s)" % (kwargs,))
        if len(a) > 1: raise RuntimeError("More than one Kernel found with the given criteria (%s)" % (kwargs,))
        return a[0]

    def refresh(self):
        """Refreshes the kernel with a new API call."""
        new_inst = Kernel.find(api_id=self.api_id)
        for attr in self.direct_attrs:
            setattr(self, attr.local_name, getattr(new_inst, attr.local_name))
        del new_inst

    def __repr__(self):
        return "<Kernel label='%s'>" % self.label


class KernelTest:
    """Suite of integration tests to run when `chube test Kernel` is called."""
    @classmethod
    def run(cls):
        import random

        print "~~~ Listing all kernels"
        print
        kernels = Kernel.search()
        print "~~~ %d kernels listed" % (len(kernels),)
        print

        sample_kernel = random.sample(kernels, 1)[0]

        kernel_id = sample_kernel.api_id
        print "~~~ Fetching kernel '%s' by kernel ID" % (sample_kernel.label)
        print
        kernel = Kernel.find(api_id=kernel_id)
        print "api_id = %d" % (kernel.api_id,)
        print "label = '%s'" % (kernel.label,)
        print "is_xen = %s" % (kernel.is_xen,)
        print
        assert kernel.label == sample_kernel.label

        print "~~~ Refreshing the kernel '%s'" % (kernel.label)
        print
        kernel.refresh()
        assert kernel.label == sample_kernel.label

        print "~~~ Tests passed!"
