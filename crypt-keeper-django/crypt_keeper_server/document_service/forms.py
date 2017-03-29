from logging import getLogger

from django import forms
from django.core.exceptions import ObjectDoesNotExist

from document_description_store.models import DocumentDescription
from .helper import add_permission_for_document, validate_username, get_document_for_document_id

log = getLogger('crypt-keeper.' + __name__)


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

        if not validate_username(name):
            self.add_error('name', 'must be valid username.')

        document = get_document_for_document_id(document_id)
        if document is None:
            self.add_error('document_id', 'must provide valid document_id')
        elif document.customer != self.user:
            self.add_error('document_id', 'must be owned by logged in user.')

    def add_view_permission(self):
        document_id = self.cleaned_data.get('document_id')
        name = self.cleaned_data.get('name')
        document = get_document_for_document_id(document_id)
        add_permission_for_document(document, name)
