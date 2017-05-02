from functools import wraps

import bricks.html5 as t
from bricks.contrib.bem import bem_modifiers, bem_with_modifiers
from bricks.helpers import join_classes

MDL_REQUIRES = ('mdl',)


def factory(tag, cls, help=''):
    """
    Creates a function that simply decorates a standard element with a
    corresponding material design lite class.
    """

    def elem(*args, class_=None, **kwargs):
        return tag(*args, class_=join_classes(cls, class_), **kwargs)

    return elem


# Decorators
def mdl_shadow(func):
    """
    Transforms function to accept a shadow attribute.

    The attribute receives a number in the list [2, 3, 4, 6, 8, or 16] and
    adds the corresponding mdl-shadow--2dp class.
    """

    valid_shadows = [2, 3, 4, 6, 8, 16]

    @wraps(func)
    def decorated(*args, class_=None, shadow=None, **kwargs):
        if shadow:
            if not shadow in valid_shadows:
                raise ValueError('shadow must be in %s' % valid_shadows)
            class_ = join_classes(class_, 'mdl-shadow--%sdp' % shadow)
        if 'children' in kwargs:
            args = kwargs.pop('children'), + args

        result =  func(*args, class_=class_, **kwargs)
        result.requires = MDL_REQUIRES
        return result

    return decorated


# ------------------------------------------------------------------------------
# Simple elements

icon = factory(t.i, 'material-icons', 'An MDL icon element')
div = mdl_shadow(t.div)
span = mdl_shadow(t.span)


# ------------------------------------------------------------------------------
# Complex elements

@mdl_shadow
def badge(children=None, badge=None, class_=None,
          no_background=False, overlap=False,
          href=None, tag=None, icon=None,
          **kwargs):
    """
    A MDL badge element.

    The Material Design Lite (MDL) badge component is an onscreen notification
    element. A badge consists of a small circle, typically containing a number
    or other characters, that appears in proximity to another object. A badge
    can be both a notifier that there are additional items associated with an
    object and an indicator of how many items there are.

    Args:
        content:
            Text content.
        badge:
            Text on the badge.
        no_background, overlap:
            Badge modifiers.
        icon:
            If True, creates an icon badge.
        href:
            If given, the default tag is chosen to be an <a>. This produces an
            anchor badge, which is a common use case.
        tag:
            The tag used to create the main badge element. This defaults to
            html5.span, if not set. Some modifiers also affects the default tag.

    Examples:
        >>> badge('foo', '42').render()
        <span class="mdl-badge" data-badge="42">foo</span>

    See also:
        https://getmdl.io/components/index.html#badges-section
    """

    # Define class from the given properties
    classes = bem_with_modifiers(
        'mdl-badge',
        no_background=no_background,
        overlap=overlap,
    )
    class_ = join_classes(icon and 'material-icons', classes, class_)

    # Choose proper button tag
    button_tag = tag or (t.a if href else t.span)

    if href:
        kwargs['href'] = href

    return \
        button_tag(class_=class_, data_badge=(badge or ' '), **kwargs)[
            children,
        ]


@mdl_shadow
def button(children=None, class_=None,
           fab=False, colored=False, raised=False, accent=False, primary=False,
           icon=False, ripple=False, tag=t.button,
           **kwargs):
    """
    A MDL button.

    The Material Design Lite (MDL) button component is an enhanced version of
    the standard HTML <button> element. A button consists of text and/or an
    image that clearly communicates what action will occur when the user clicks
    or touches it. The MDL button component provides various types of buttons,
    and allows you to add both display and click effects.

    Args:
        fab, icon, raised, colored, primary, accent, ripple:
            Enable the corresponding mdl styling.
        disabled:
            Disable button
        tag:
            The tag element used to create button (defauts to html5.button)

    Examples:
        >>> button('Next').render()
        <button class="mdl-button mdl-js-button">Next</button>

    See also:
        https://getmdl.io/components/index.html#buttons-section
    """

    # Define class from the given properties
    classes = ['mdl-button', 'mdl-js-button']
    classes += bem_modifiers(
        'mdl-button',
        fab=fab, raised=raised, icon=icon,
        colored=colored, accent=accent, primary=primary,
        mdl_js_ripple_effect=ripple and 'mdl-js-ripple-effect',
    )
    class_ = join_classes(classes, class_)

    # Return button element
    return \
        tag(class_=class_, **kwargs)[
            children
        ]


@mdl_shadow
def progress(class_=None, tag=t.div, indeterminate=False, **kwargs):
    """
    A MDL progress bar.

    The Material Design Lite (MDL) progress component is a visual indicator of
    background activity in a web page or application. A progress indicator
    consists of a (typically) horizontal bar containing some animation that
    conveys a sense of motion. While some progress devices indicate an
    approximate or specific percentage of completion, the MDL progress component
    simply communicates the fact that an activity is ongoing and is not yet
    complete.

    Args:
        indeterminate:
            An indeterminate tag progress animates the progress indicator
            back and forward.
        tag:
            The tag class used to create element (defaults to html5.div)

    Examples:
        >>> progress(id='foo').render()
        <div id="foo" class="mdl-progress mdl-js-progress"></div>

    See also:
        https://getmdl.io/components/index.html#loading-section
    """

    # Define class from the given properties
    classes = bem_with_modifiers('mdl-progress', indeterminate=indeterminate)
    class_ = join_classes(classes, 'mdl-js-progress', class_)

    # TODO: register requires
    return tag(class_=class_, **kwargs)


@mdl_shadow
def spinner(class_=None, tag=t.div, active=True, single_color=False, **kwargs):
    """
    A MDL spinner.

    The Material Design Lite (MDL) spinner component is an enhanced replacement
    for the classic "wait cursor" (which varies significantly among hardware and
    software versions) and indicates that there is an ongoing process, the
    results of which are not yet available. A spinner consists of an open circle
    that changes colors as it animates in a clockwise direction, and clearly
    communicates that a process has been started but not completed.

    Args:
        active:
            Activate spinner.
        single_color:
            If True, does not change color after each iteration.
        tag:
            The tag class used to create element (defaults to html5.div)

    Examples:
        >>> spinner(active=False).render()
        <div class="mdl-spinner mdl-js-spinner"></div>

    See also:
        https://getmdl.io/components/index.html#loading-section
    """

    # Define class from the given properties
    classes = bem_with_modifiers('mdl-progress', single_color=single_color)
    class_ = \
        join_classes(classes, 'mdl-js-spinner', class_, active and 'is_active')

    return tag(class_=class_, **kwargs)


@mdl_shadow
def slider(class_=None, min=0, max=100, value=0, **kwargs):
    """
    A MDL slider input element.

    The Material Design Lite (MDL) slider component is an enhanced version of
    the new HTML5 <input type="range"> element. A slider consists of a
    horizontal line upon which sits a small, movable disc (the thumb) and,
    typically, text that clearly communicates a value that will be set when the
    user moves it.

    Args:
        min, max, value:
            Defines the range and the current value for the slider. An optional
            ``step`` argument defines the minimum step size for changing values.
        single_color:
            If True, does not change color after each iteration.
        tag:
            The tag class used to create element (defaults to html5.div)

    See also:
        https://getmdl.io/components/index.html#sliders-section
    """

    class_ = join_classes('mdl-slider', 'mdl-js-slider', class_)
    return t.input(class_=class_, type='range',
                   min=min, max=max, value=value, **kwargs)


@mdl_shadow
def tooltip(children=None, class_=None, **kwargs):
    """
    A MDL tooltip.

    The Material Design Lite (MDL) tooltip component is an enhanced version of
    the standard HTML tooltip as produced by the title attribute. A tooltip
    consists of text and/or an image that clearly communicates additional
    information about an element when the user hovers over or, in a touch-based
    UI, touches the element. The MDL tooltip component is pre-styled (colors,
    fonts, and other settings are contained in material.min.css) to provide a
    vivid, attractive visual element that displays related but typically
    non-essential content, e.g., a definition, clarification, or brief
    instruction.

    Args:
        min, max, value:
            Defines the range and the current value for the slider. An optional
            ``step`` argument defines the minimum step size for changing values.
        single_color:
            If True, does not change color after each iteration.
        tag:
            The tag class used to create element (defaults to html5.div)

    Example:
        >>> div('Darth Vader', id='vader')
        >>> tooltip('The Sith Lord', for_='vader')

    See also:
        https://getmdl.io/components/index.html#tooltips-section
    """

    class_ = join_classes('mdl-tooltip', class_)
    return t.span(children, class_=class_, **kwargs)


# ------------------------------------------------------------------------------
# Not implemented

def card(*args, **kwargs):
    raise NotImplementedError


def chip(*args, **kwargs):
    raise NotImplementedError


def dialog(*args, **kwargs):
    raise NotImplementedError


def layout(*args, **kwargs):
    raise NotImplementedError


def grid(*args, **kwargs):
    raise NotImplementedError


def tabs(*args, **kwargs):
    raise NotImplementedError


def footer(*args, **kwargs):
    raise NotImplementedError


def list(*args, **kwargs):
    raise NotImplementedError


def menu(*args, **kwargs):
    raise NotImplementedError


def snackbar(*args, **kwargs):
    raise NotImplementedError


def checkbox(*args, **kwargs):
    raise NotImplementedError


def radio(*args, **kwargs):
    raise NotImplementedError


def icon_toggle(*args, **kwargs):
    raise NotImplementedError


def switch(*args, **kwargs):
    raise NotImplementedError


def table(*args, **kwargs):
    raise NotImplementedError


def text_field(*args, **kwargs):
    raise NotImplementedError
