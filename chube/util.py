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

def keywords_only(f):
    """Function decorator that makes the function accept only keyword params.

       All this does right now is make sure the error message is clearer when
       you try to pass a non-keyword param."""
    def f_new(*f_args, **f_kwargs):
        if len(f_args) > 1:
            raise ValueError("This method accepts only keyword arguments. See `help({0})`".format((f.__name__)))
        return f(*f_args, **f_kwargs)
    return f_new
