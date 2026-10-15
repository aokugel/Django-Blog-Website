from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.utils.cache import patch_vary_headers
from django.views import generic
from .models import Post, Comment, Author
from .forms import CommentForm
from rest_framework import viewsets
from .serializers import PostSerializer, CommentSerializer

class PostList(generic.ListView):
    queryset = Post.objects.filter(status=1).order_by('-created_on')
    template_name = 'index.html'
    paginate_by = 4

def post_detail(request, slug):
    """The post page. HTMX requests get just the part of the page they update:
    a comment POST returns the comment form (or the confirmation), and
    "Load more" (?page=N) returns the next page of comments."""
    post = get_object_or_404(Post, slug=slug, status=1)
    comment_form = CommentForm(request.POST if request.method == 'POST' else None)
    new_comment = None
    if request.method == 'POST' and comment_form.is_valid():
        new_comment = comment_form.save(commit=False)
        new_comment.post = post
        new_comment.save()

    context = {'post': post,
               'comments': Paginator(post.comments.filter(active=True), 10).get_page(request.GET.get('page')),
               'new_comment': new_comment,
               'comment_form': comment_form}

    template_name = 'post_detail.html'
    if request.headers.get('HX-Request'):
        template_name = '_comment_form.html' if request.method == 'POST' else '_comments.html'
    response = render(request, template_name, context)
    # The same URL returns a full page or a fragment, so caches must key on this header.
    patch_vary_headers(response, ['HX-Request'])
    return response

class ContactView(generic.ListView):
    queryset = Author.objects.order_by('name')
    template_name = 'contact.html'


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(status=1).order_by('-created_on')
    serializer_class = PostSerializer

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('post')
    serializer_class = CommentSerializer

