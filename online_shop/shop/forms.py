from django import forms
from .models import Comment

class CommentCreateForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={'cols': 50, 'rows': 3}))

    class Meta:
        model = Comment
        fields = ['username', 'text']
