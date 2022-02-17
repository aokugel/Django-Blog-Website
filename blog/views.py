from django.shortcuts import render, get_object_or_404
from django.views import generic
from .models import Post, Comment
from .forms import CommentForm
from rest_framework import viewsets
from .serializers import PostSerializer, CommentSerializer
from .utils import pull_last_post
import requests
import os

class PostList(generic.ListView):
    queryset = Post.objects.filter(status=1).order_by('-created_on')
    template_name = 'index.html'
    paginate_by = 4
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['last_post'] = pull_last_post()
        return context

def post_detail(request, slug):
    template_name = 'post_detail.html'
    post = get_object_or_404(Post, slug=slug)
    comments = post.comments.filter(active=True)
    new_comment = None
    # Comment posted
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():

            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            # Save the comment to the database
            new_comment.save()
    else:
        comment_form = CommentForm()

    return render(request, template_name, {'post': post,
                                           'comments': comments,
                                           'new_comment': new_comment,
                                           'comment_form': comment_form,
                                           'last_post': pull_last_post()})    

class ContactView(generic.ListView):
    template_name = 'contact.html'
    queryset = Post.objects.filter(status=1).order_by('-created_on')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["last_post"] = pull_last_post()
        return context

def covid_details(request):
    template_name = 'covid.html'
    api_key = os.environ.get('API_KEY')
    json_response = requests.get("https://api.covidactnow.org/v2/country/US.timeseries.json?apiKey={}".format(api_key)).json()
    context = {
        "dataset": json_response['actualsTimeseries'][30::-1],
        "last_post": pull_last_post()
    }
    return render(request, template_name, context)  


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.order_by('-created_on')
    serializer_class = PostSerializer

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('post')
    serializer_class = CommentSerializer

