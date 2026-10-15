from django.core.paginator import Paginator
from django.db.models import Prefetch
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
    a comment or reply POST returns that form (or its confirmation), and
    "Load more" (?page=N) returns the next page of comments."""
    post = get_object_or_404(Post, slug=slug, status=1)

    # Each reply form gets its own element ids (reply<parent>_name, ...) so many can share a page.
    parent_id = request.POST.get('parent', '') if request.method == 'POST' else ''
    parent_id = parent_id if parent_id.isdigit() else ''
    form = CommentForm(request.POST if request.method == 'POST' else None, post=post,
                       auto_id=f'reply{parent_id}_%s' if parent_id else 'id_%s')
    if request.method == 'POST' and form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()

    approved_replies = Prefetch('replies', queryset=Comment.objects.filter(active=True), to_attr='approved_replies')
    top_level = post.comments.filter(active=True, parent=None).prefetch_related(approved_replies)
    comments = Paginator(top_level, 10).get_page(request.GET.get('page'))
    for comment in comments:
        if parent_id == str(comment.pk):
            comment.reply_form = form  # a reply was just posted here: show its errors or confirmation in place
        else:
            comment.reply_form = CommentForm(post=post, initial={'parent': comment.pk}, auto_id=f'reply{comment.pk}_%s')

    context = {'post': post,
               'comments': comments,
               'comment_count': post.comments.filter(active=True).count(),
               'form': CommentForm(post=post) if parent_id else form}

    template_name = 'post_detail.html'
    if request.headers.get('HX-Request'):
        if request.method == 'POST':
            template_name, context['form'] = '_comment_form.html', form
        else:
            template_name = '_comments.html'
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

