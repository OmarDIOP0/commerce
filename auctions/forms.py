from django import forms
from .models import Comment

class BidForm(forms.Form):
    amount = forms.DecimalField(min_value=0.01,label=False,widget=forms.TextInput(attrs={'placeholder':'Enter your bid Amount'}))

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']