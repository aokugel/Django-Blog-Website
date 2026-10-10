from django import template
from ..models import Post

register = template.Library()

@register.simple_tag
def about_post():
    """The oldest published post, which the nav's About link points to."""
    return Post.objects.filter(status=1).order_by('created_on').first()
