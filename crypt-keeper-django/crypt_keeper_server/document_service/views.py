from django.views import generic
from document_description_store.models import DocumentDescription
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from .forms import ShareForm
from .helper import get_group_for_document

# Create your views here.


class HomeView(generic.TemplateView):
    template_name = 'documents/home.html'


class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'documents/list.html'
    context_object_name = 'document_list'
    paginate_by = 10

    def get_queryset(self):
        return DocumentDescription.objects.select_related('customer').order_by('-created_on')


class MyView(IndexView):
    def get_queryset(self):
        return DocumentDescription.objects.select_related('customer').filter(customer=self.request.user.id).order_by('-created_on')


class DocumentDetailView(LoginRequiredMixin, generic.DetailView):
    model = DocumentDescription
    template_name = 'documents/detail.html'
    context_object_name = 'document'

    def get_context_data(self, **kwargs):
        context = super(DocumentDetailView, self).get_context_data(**kwargs)
        document = self.object
        group = get_group_for_document(document)
        if group:
            context['users'] = group.user_set.all()
        return context


class ShareView(LoginRequiredMixin, generic.FormView):
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
        self.success_url = reverse('detail', kwargs={'pk': document_id})
        return super(ShareView, self).form_valid(form)

    def dispatch(self, *args, **kwargs):
        self.initial.update({
            'document_id': self.request.GET.get('document_id')
        })
        return super(ShareView, self).dispatch(*args, **kwargs)
