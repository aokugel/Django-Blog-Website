# serializers.py
from rest_framework import serializers

from .models import Post, Comment

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id','title', 'slug','author','updated_on','content','created_on','status')

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id','post', 'name','email','body','created_on','active')

