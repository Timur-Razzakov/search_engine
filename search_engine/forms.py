from django import forms

from .fields import MultipleFileField


class FileUploadForm(forms.Form):
    files = MultipleFileField(label='Select files', required=False)


class SearchForm(forms.Form):
    barcode = forms.CharField(label='Введите штрих-код', max_length=100)
