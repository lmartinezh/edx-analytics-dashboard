from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from opaque_keys.edx.keys import CourseKey

register = template.Library()


@register.simple_tag
def settings_value(name):
    """
    Retrieve a value from settings.

    If setting is not found, None is returned.
    """
    return getattr(settings, name)


@register.filter
def metric_percentage(value):
    # Translators: Simply move the percent symbol (%) to the correct location. Do NOT translate the word statistic.
    percent_stat = _('{statistic}%')
    percent = '0'

    if value:
        if value < 0.01:
            percent = '< 1'
        else:
            percent = '{0}'.format(round(value, 3) * 100)

    # pylint: disable=no-member
    return percent_stat.format(statistic=percent)


@register.tag(name='captureas')
def do_captureas(parser, token):
    """
    Capture contents of block into context.

    Source:
        https://djangosnippets.org/snippets/545/

    Example:
        {% captureas foo %}{{ foo.value }}-suffix{% endcaptureas %}
        {% if foo in bar %}{% endif %}
    """

    try:
        __, args = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("'captureas' node requires a variable name.")
    nodelist = parser.parse(('endcaptureas',))
    parser.delete_first_token()
    return CaptureasNode(nodelist, args)


class CaptureasNode(template.Node):
    def __init__(self, nodelist, varname):
        self.nodelist = nodelist
        self.varname = varname

    def render(self, context):
        output = mark_safe(self.nodelist.render(context).strip())
        context[self.varname] = output
        return ''


@register.inclusion_tag('summary_point.html')
def summary_point(value, label, subheading=None, tooltip=None):
    return {
        'value': value,
        'label': label,
        'subheading': subheading,
        'tooltip': tooltip
    }


@register.inclusion_tag('section_error.html')
def show_chart_error():
    return _get_base_error_context('chart')


@register.inclusion_tag('section_error.html')
def show_table_error():
    return _get_base_error_context('table')


@register.inclusion_tag('section_error.html')
def show_metrics_error():
    return _get_base_error_context('metrics')


def _get_base_error_context(content_type):
    return {
        'content_type': content_type,
        'load_error_message': settings.DOCUMENTATION_LOAD_ERROR_MESSAGE
    }


@register.filter
def format_course_key(course_key, separator=u'/'):
    if isinstance(course_key, basestring):
        course_key = CourseKey.from_string(course_key)

    return separator.join([course_key.org, course_key.course, course_key.run])
