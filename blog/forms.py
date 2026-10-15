from .models import Comment
from django import forms


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body', 'parent')
        widgets = {'body': forms.Textarea(attrs={'rows': 4}), 'parent': forms.HiddenInput}

    def __init__(self, *args, post, **kwargs):
        super().__init__(*args, **kwargs)
        # Only approved top-level comments on this post can be replied to, which keeps replies one level deep.
        self.fields['parent'].queryset = post.comments.filter(parent=None, active=True)
