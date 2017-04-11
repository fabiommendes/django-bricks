import abc

from bricks.request import FakeRequest


class Renderable(abc.ABC):
    """
    Objects that have a render method.
    """

    def __str__(self):
        return str(self.__html__())

    def __html__(self):
        return self.render(FakeRequest())

    @classmethod
    def __subclasshook__(cls, subclass):
        if hasattr(subclass, 'render') and hasattr(subclass, '__html__'):
            return True
        return False

    @abc.abstractmethod
    def render(self, request, **kwargs):
        raise NotImplementedError