class Stub:
    pass

class StubClass:
    def __init__(self):
        self._stub = Stub()

    def __call__(self, *args, **kwargs):
        return self._stub
