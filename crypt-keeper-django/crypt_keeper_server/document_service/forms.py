from django import forms
from guardian.shortcuts import assign_perm
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from document_description_store.models import DocumentDescription
from .helper import get_group_for_document, get_user_for_username


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

        if get_user_for_username(name) is None:
            self.add_error('name', 'must be valid username.')

        try:
            DocumentDescription.objects.get(pk=document_id)
        except ObjectDoesNotExist:
            self.add_error('document_id', 'must provide valid document_id')

    def add_view_permission(self):
        document_id = self.cleaned_data.get('document_id')
        name = self.cleaned_data.get('name')
        document = DocumentDescription.objects.get(id=document_id)
        user = get_user_for_username(name)
        group = get_group_for_document(document)
        if group and user:
            group.user_set.add(user)
            group.save()
        assign_perm('view_document_description', user, document)
