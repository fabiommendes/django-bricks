class FakeRequest:
    """
    Simulate a basic Django request object interface.
    """

    def __init__(self):
        self.method = 'GET'
        self.GET = {}
        self.POST = {}
        self.FILE = {}
        self.keywords = {}
        self.funcargnames = ()


def request():
    """
    Return a fake WSGI request object.
    """

    return FakeRequest()