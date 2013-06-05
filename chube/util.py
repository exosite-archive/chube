class RequiresParams:
    """Function decorator that requires the given named arguments to be provided.

       Use like so:

           @requires_params("datacenter", "plan", "payment_term")
           def create_linode(self, **kwargs):
               # This function can now assume that `kwargs` has those keys."""
    def __init__(self, *required_params):
        self._required_params = required_params

    def __call__(self, f):
        def with_reqs(*f_args, **f_kwargs):
            for param in self._required_params:
                if not f_kwargs.has_key(param):
                    raise RuntimeError("Missing required argument '%s' to function '%s'" %
                                       (param, f.__name__))
            return f(*f_args, **f_kwargs)
        return with_reqs
