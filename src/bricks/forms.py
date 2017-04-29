import django.forms.utils
from django import forms

from bricks.components.utils import ifset
from .components import html5_tags
from .html5 import tr, td, th, li, ul, p, br, html


def form_row(label, input, errors=None, help_text=None, class_=None,
             type='table', **kwargs):
    """
    Return a normal row of a form element based on form type.

    Each row display a label for the form element and the corresponding input
    type.
    """
    if type == 'table':
        return \
            tr(class_=class_, **kwargs)[
                th(label),
                td()[
                    errors, input, ifset(help_text, br), help_text,
                ]
            ]
    elif type in ('ul', 'p'):
        tag = getattr(html5_tags, type)
        return \
            tag(class_=class_, **kwargs)[
                errors, label, input, help_text
            ]
    else:
        raise ValueError('invalid form type: %r' % type)


def form_error_row(error, type='table'):
    """
    Display a error row.

    These are used for "global" errors as opposed to errors related to some
    specific field.
    """

    if type == 'table':
        return tr(td(error, colspan=2))
    elif type == 'ul':
        return li(error)
    elif type == 'p':
        return p(error)
    else:
        raise ValueError('invalid form type: %r' % type)


class ErrorList(forms.utils.ErrorList):
    """
    A list of errors that knows hot to render itsef.
    """

    def as_ul(self):
        if not self.data:
            return html('')
        return \
            ul(class_=self.error_class)[
                [li(e) for e in self]
            ]


class Form(forms.Form):
    """
    Like Django forms, but return HTML tag elements.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('error_class', ErrorList)
        super().__init__(*args, **kwargs)

    def _form(self, type):
        hidden = []

        with Container() as result:
            # Insert non-field errors at the top of the form
            result << form_error_row(self.non_field_errors())

            # Iterate over all fields
            for name, field in self.fields.items():
                if field.is_hidden:
                    hidden.append(field)
                    continue

                result << form_row(
                    field.label,
                    self[name],
                    class_=self[name].css_classes() or None,
                    errors=self.error_class(self[name].errors),
                    help_text=field.help_text
                )

            # Add all hidden fields in the last hidden row
            if hidden:
                result << form_row('', hidden,
                                   class_='hidden',
                                   style='display: none')
        return result

    def as_table(self):
        """
        Returns this form rendered as HTML <tr>s.
        """
        return self._form(type='table')

    def as_ul(self):
        """
        Returns this form rendered as HTML <li>s -- excluding the <ul></ul>.
        """
        return self._form(type='ul')

    def as_p(self):
        """
        Returns this form rendered as HTML <p>s.
        """
        return self._form(type='ul')
