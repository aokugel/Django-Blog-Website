import markdown as md
from django import template
from django.utils.safestring import mark_safe

from ..models import Post

register = template.Library()

@register.simple_tag
def about_post():
    """The oldest published post, which the nav's About link points to."""
    return Post.objects.filter(status=1).order_by('created_on').first()

@register.filter
def markdown(text):
    """Render a post's Markdown. Raw HTML passes through, so older HTML posts still work.
    Posts are only written by the site owner in the admin, so the output is trusted."""
    return mark_safe(md.markdown(text, extensions=['fenced_code', 'tables']))
