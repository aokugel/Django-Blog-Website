import time

from django import forms
from django.core import signing

from .models import Comment

SPAM_ERROR = "This comment couldn't be posted. Please try again."


class CommentForm(forms.ModelForm):
    # Spam traps: bots fill in every field and submit instantly; people do neither.
    # `website` is hidden by CSS (see input.css), and `ts` is a signed render time.
    website = forms.CharField(required=False, label='Leave this empty',
                              widget=forms.TextInput(attrs={'tabindex': '-1', 'autocomplete': 'off'}))
    ts = forms.CharField(required=False, widget=forms.HiddenInput)
    MIN_SECONDS = 3

    class Meta:
        model = Comment
        fields = ('name', 'email', 'body', 'parent')
        widgets = {'body': forms.Textarea(attrs={'rows': 4}), 'parent': forms.HiddenInput}

    def __init__(self, *args, post, **kwargs):
        super().__init__(*args, **kwargs)
        # Only approved top-level comments on this post can be replied to, which keeps replies one level deep.
        self.fields['parent'].queryset = post.comments.filter(parent=None, active=True)
        self.fields['ts'].initial = signing.dumps(int(time.time()))

    def clean(self):
        cleaned_data = super().clean()
        try:
            rendered_at = signing.loads(cleaned_data.get('ts') or '')
        except signing.BadSignature:
            rendered_at = None
        if cleaned_data.get('website') or rendered_at is None or time.time() - rendered_at < self.MIN_SECONDS:
            raise forms.ValidationError(SPAM_ERROR)
        return cleaned_data
