#   Copyright 2017 Maurice Carey
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#

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
