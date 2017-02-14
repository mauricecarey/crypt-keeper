from django.views import generic
from document_description_store.models import DocumentDescription
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import ShareForm

# Create your views here.


class IndexView(generic.ListView):
    template_name = 'documents/list.html'
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

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DocumentDetailView, self).dispatch(*args, **kwargs)


class ShareView(generic.FormView):
    template_name = 'documents/share.html'
    form_class = ShareForm
    success_url = '/'

    def form_valid(self, form):
        form.add_view_permission()
        return super(ShareView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ShareView, self).get_context_data(**kwargs)
        document_id = self.request.REQUEST.get('document_id')
        form = kwargs.get('form')
        if form:
            form.fields.get('document_id').initial = document_id
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ShareView, self).dispatch(*args, **kwargs)
