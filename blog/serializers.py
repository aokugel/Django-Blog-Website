# serializers.py
from rest_framework import serializers

from .models import Post, Comment

class PostSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Post
        fields = ('title','author')

