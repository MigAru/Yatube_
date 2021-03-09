from django.forms import ModelForm

from .models import Comment, Post, Group


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['group', 'text', 'image']


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ['title', 'slug', 'description']