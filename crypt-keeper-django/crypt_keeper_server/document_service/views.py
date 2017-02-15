from django.views import generic
from document_description_store.models import DocumentDescription
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.decorators import method_decorator
from .forms import ShareForm
from .helper import get_group_for_document

# Create your views here.


class IndexView(generic.ListView):
    template_name = 'documents/list.html'
    context_object_name = 'document_list'
    paginate_by = 10

    def get_queryset(self):
        return DocumentDescription.objects.select_related('customer').order_by('-created_on')


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

    def get_context_data(self, **kwargs):
        context = super(DocumentDetailView, self).get_context_data(**kwargs)
        document = self.object
        group = get_group_for_document(document)
        if group:
            context['users'] = group.user_set.all()
        return context


class ShareView(generic.FormView):
    template_name = 'documents/share.html'
    form_class = ShareForm
    success_url = '/'

    def get_form(self, form_class=None):
        form = super(ShareView, self).get_form(form_class)
        form.user = self.request.user
        return form

    def form_valid(self, form):
        form.add_view_permission()
        document_id = form.cleaned_data.get('document_id')
        if document_id:
            self.success_url = reverse('detail', kwargs={'pk': document_id})
        return super(ShareView, self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.initial.update({
            'document_id': self.request.GET.get('document_id')
        })
        return super(ShareView, self).dispatch(*args, **kwargs)
