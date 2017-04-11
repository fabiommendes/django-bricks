import collections

from django.template.loader import render_to_string
from markupsafe import Markup

from bricks.helpers import escape, safe
from bricks.request import FakeRequest, request as _request
from bricks.mixins import Renderable
from bricks.utils import lazy_singledispatch, snake_case


@lazy_singledispatch
def render(obj, request=None, **kwargs):
    """
    Renders object as a safe HTML string.

    This function uses single dispatch to make it extensible for user defined
    types::

        @render.register(int)
        def _(x, **kwargs):
            if x == 42:
                return safe('the answer')
            else:
                return safe(x)

    A very common pattern is to render object from a template. This has
    specific support::

        render.register_template(UserProfile, 'myapp/user_profile.jinja2')

    By default, it populates the context dictionary with a snake_case version
    of the class name, in this case, ``{'user_profile': x}``. The user may pass
    a ``context`` keyword argument to include additional context data.

    If you want to personalize how this is done, it is possible to use
    register_template to register a context factory function. The function
    should receive the object, a request and kwargs::

        @render.register_template(UserProfile, 'myapp/user_profile.jinja2')
        def context(profile, request=None, context=None, **kwargs):
            context = context or {}
            context.update(kwargs, request=request, profile=profile)
            return context

    Notes:
        All implementations must receive the user-defined object as first
        argument and accept arbitrary keyword arguments.
    """

    raise TypeError('type not supported: %r' % obj.__class__.__name__)


@render.register(Markup)
def _(x, **kwargs):
    return x


@render.register(str)
def _(x, **kwargs):
    return escape(x)


@render.register(collections.Sequence)
def _(seq, **kwargs):
    return safe('\n'.join(render(x, **kwargs) for x in seq))


@render.register('django.db.models.Model')
def _(x, **kwargs):
    cls = x.__class__
    template_name = '%s/%s' % (cls._meta.app_label, cls._meta.model_name)
    template_name = [template_name + '.html', template_name + '.jinja2']
    register_template(cls, template_name=template_name)
    context = kwargs.setdefault('context', {})
    context.setdefault('object', x)
    return render(x, **kwargs)


@render.register(Renderable)
def _(x, request=None, **kwargs):
    return safe(x.render(request or _request(), **kwargs))


def register_template(cls, template_name=None, object_context_name=None,
                      template_extension=None, get_context=None):
    """
    Register the default template name for the given type.

    Args:
        cls:
            A type for single dispatch.
        template_name (str, list):
            The template name. If no template is given, it automatically selects
            '<base module>/<class name>.<ext>'.
        object_context_name (str):
            Name of the variable that holds the object in the context
            dictionary.
        get_context:
            A function with signature f(obj, request, **kwargs) that generates
            the context dictionary passed to the template.
    """

    get_context_func = get_context
    if template_name is None:
        name = snake_case(cls.__name__)
        name = '%s/%s' % (cls.__module__.partition('.')[0], name)
        template_name = ['%s.html' % name, '%s.jinja2' % name]
    if object_context_name is None:
        object_context_name = snake_case(cls.__name__)
    if get_context_func is None:
        def get_context_func(obj, **kwargs):
            request = kwargs.get('request') or FakeRequest()
            context = kwargs.get('context') or {}
            context[object_context_name] = obj
            context.setdefault('request', request)
            return context

    # Define implementation inside a closure
    def render_to_html(obj, request=None, **kwargs):
        request = request or FakeRequest()
        context = get_context_func(obj, request=request, **kwargs)
        return render._render_template(template_name, context=context,
                                       request=request)

    render.register(cls, render_to_html)

    # If get_context = None, function could have been used as a decorator.
    if get_context is None:
        def decorator(func):
            register_template(cls, template_name=template_name,
                              object_context_name=object_context_name,
                              template_extension=template_extension,
                              get_context=func)
            return func

        return decorator


render.register_template = register_template
render._render_template = render_to_string
