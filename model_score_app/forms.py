from django import forms
from .models import FileScore

class ModelUploadForm(forms.ModelForm):
    class Meta:
        model = FileScore
        fields = ('model_file',)

