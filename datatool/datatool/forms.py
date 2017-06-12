from django import forms

# Django generated form with a file field.
class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file'
    )
