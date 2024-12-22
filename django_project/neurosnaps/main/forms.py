from django import forms
from .models import MyImage
from .models import Feedback

class ImageForm(forms.ModelForm):
    class Meta:
        model = MyImage
        fields = ('title','image')


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'topic', 'message']