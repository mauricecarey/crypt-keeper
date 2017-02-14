from django import forms
from guardian.shortcuts import assign_perm
from django.contrib.auth.models import User
from document_description_store.models import DocumentDescription


class ShareForm(forms.Form):
    name = forms.CharField(required=True)
    document_id = forms.IntegerField(required=True, widget=forms.HiddenInput)

    def clean(self):
        cleaned_data = super(ShareForm, self).clean()
        name = cleaned_data.get('name')
        document_id = cleaned_data.get('document_id')

        if document_id is None:
            self.add_error('document_id', 'document_id cannot be none.')
            raise forms.ValidationError(
                'Invalid value: %(value)s',
                code='invalid',
                params={'value': document_id}
            )

        if name is None:
            self.add_error('name', 'name cannot be none.')
            raise forms.ValidationError(
                'Invalid value: %(value)s',
                code='invalid',
                params={'value': name}
            )

        if User.objects.get(username=name) is None:
            self.add_error('name', 'must be valid username.')

        if DocumentDescription.objects.get(id=document_id) is None:
            self.add_error('document_id', 'must provide valid document_id')

    def add_view_permission(self):
        document_id = self.cleaned_data.get('document_id')
        name = self.cleaned_data.get('name')
        document = DocumentDescription.objects.get(id=document_id)
        user = User.objects.get(username=name)
        assign_perm('view_document_description', user, document)
