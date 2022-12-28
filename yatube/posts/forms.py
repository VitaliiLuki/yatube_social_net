from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    """Form for creation a new post"""
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        widget = {
            'name': 'choose file',
        } 


class CommentForm(forms.ModelForm):
    """Form for adding a comment to a post"""
    class Meta:
        model = Comment
        fields = ('text',)

