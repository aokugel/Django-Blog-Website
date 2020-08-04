from django.shortcuts import render, get_object_or_404
from django.views import generic
from .models import Post, Comment
from .forms import CommentForm

class PostList(generic.ListView):
    queryset = Post.objects.filter(status=1).order_by('-created_on')
    template_name = 'index.html'
    paginate_by = 3
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if Post.objects.filter(status=1).order_by('created_on'):
            context['last_post'] = Post.objects.filter(status=1).order_by('created_on')[0]
        return context

#class PostDetail(generic.DetailView):
    #model = Post
    #template_name = 'post_detail.html'

def post_detail(request, slug):
    template_name = 'post_detail.html'
    post = get_object_or_404(Post, slug=slug)
    comments = post.comments.filter(active=True)
    new_comment = None
    last_post = None
    if Post.objects.filter(status=1):
        last_post = Post.objects.filter(status=1).order_by('created_on')[0]
        print('So its correctly assigning the last_post variable')
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
                                           'last_post': last_post})
    

class ContactView(generic.ListView):
    template_name = 'contact.html'
    queryset = Post.objects.filter(status=1).order_by('-created_on')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if Post.objects.filter(status=1).order_by('created_on'):
            context['last_post'] = Post.objects.filter(status=1).order_by('created_on')[0]
        return context


