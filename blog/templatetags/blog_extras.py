from django import template
from ..views import PostList
from ..models import Post

register = template.Library()

@register.simple_tag
def oldest():
    """Returns the oldest post in the PostList view"""
    post = Post.objects.filter(status=1).order_by('created_on')
    return post

@register.filter(name='lastpost')
def lastpost(post_list):
    length = len(post_list)
    return post_list[length-1]

#register.tag('oldest', oldest)
