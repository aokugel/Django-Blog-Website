from .models import Post

def pull_last_post():
    if Post.objects.filter(status=1):
        return Post.objects.filter(status=1).order_by('created_on')[0]