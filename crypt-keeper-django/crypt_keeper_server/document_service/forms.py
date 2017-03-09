from django import forms
from guardian.shortcuts import assign_perm
from django.core.exceptions import ObjectDoesNotExist
from document_description_store.models import DocumentDescription
from .helper import get_group_for_document, get_user_for_username
from django.conf import settings
from logging import getLogger, INFO

log = getLogger(__name__)
log.setLevel(settings.LOG_LEVEL)


class ShareForm(forms.Form):
    name = forms.CharField(required=True)
    document_id = forms.IntegerField(required=True, widget=forms.HiddenInput)
    user = None

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
            document = DocumentDescription.objects.get(pk=document_id)
            if document.customer != self.user:
                self.add_error('document_id', 'must be owned by logged in user.')
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
        if log.isEnabledFor(INFO):
            log.info('Adding permissions for {new_user} to access document id {document_id}.'.format(
                new_user=user,
                document_id=document_id,
            ))
