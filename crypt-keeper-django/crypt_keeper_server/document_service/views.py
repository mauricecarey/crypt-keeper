from django.shortcuts import render
from django.views import generic
from document_description_store.models import DocumentDescription
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# Create your views here.


class IndexView(generic.ListView):
    template_name = 'documents/home.html'
    context_object_name = 'document_list'

    def get_queryset(self):
        return DocumentDescription.objects.select_related('customer').order_by('-created_on')[:20]


class MyView(IndexView):

    def get_queryset(self):
        return DocumentDescription.objects.select_related('customer').filter(customer=self.request.user.id).order_by('-created_on')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MyView, self).dispatch(*args, **kwargs)


class DocumentDetailView(generic.DetailView):
    model = DocumentDescription
    template_name = 'documents/detail.html'
    context_object_name = 'document'
