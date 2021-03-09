import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as log_out_user
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.core.mail import EmailMessage
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, ListView
from weasyprint import HTML

from invoice.forms import InvoiceForm, InvoiceLineFormSet
from invoice.models import Invoice, InvoiceLine


class InvoiceListView(ListView):

    """
    Invoice list view
    """

    template_name = "invoice/invoices.html"
    paginate_by = 10

    def get_queryset(self):
        return Invoice.objects.filter(user_id=int(self.request.user.id)).order_by("-id")


class InvoiceCreateView(FormView):

    """
    Invoice create view
    """

    form_class = InvoiceForm
    template_name = "invoice/invoice.html"

    def get_context_data(self, **kwargs):
        context = super(InvoiceCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context["invoice_form"] = InvoiceForm(self.request.POST, self.request.FILES)
            context["invoiceline_form"] = InvoiceLineFormSet(self.request.POST)
        else:
            context["invoice_form"] = InvoiceForm()
            context["invoiceline_form"] = InvoiceLineFormSet()
        return context

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        invoice_form = context["invoice_form"]
        invoice_line_formset = InvoiceLineFormSet(self.request.POST)

        if invoice_form.is_valid() and invoice_line_formset.is_valid():
            invoice_obj = invoice_form.save(commit=False)
            invoice_obj.user = self.request.user
            invoice_obj.save()

            for form in invoice_line_formset:
                invoice_line_obj = form.save(commit=False)
                invoice_line_obj.invoice_id = invoice_obj.id
                invoice_line_obj.save()

            make_invoice_file(self.request, invoice_obj.id)
            return HttpResponseRedirect("/invoices/")


class InvoiceDetailView(View):

    """
    Invoice detail view
    """

    def get(self, request, *args, **kwargs):
        invoice_id = int(self.kwargs["invoice_id"])
        invoice_data = Invoice.objects.filter(id=int(invoice_id)).first()
        invoice_line_data = InvoiceLine.objects.filter(invoice_id=int(invoice_id))
        return render(
            request,
            "invoice/invoice_detail.html",
            {
                "invoice_data": invoice_data,
                "invoice_line_data": invoice_line_data,
                "base_url": request.build_absolute_uri(invoice_data.invoice_logo.url),
            },
        )


class SendMailView(View):

    """
    Send mail with invoice attachment
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(SendMailView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        invoice_id = int(self.kwargs["invoice_id"])
        invoice_data = (
            Invoice.objects.filter(id=invoice_id).values("invoice_num").first()
        )
        file_name = "INV" + invoice_data["invoice_num"]
        mail = EmailMessage(
            "Thank you for invoicing with us!",
            "A new invoice has been created on your account. You may find a PDF of your invoice attached.",
            settings.EMAIL_HOST_USER,
            [self.request.user],
        )
        file_path = os.path.join(settings.MEDIA_ROOT, "invoice_pdf", file_name)
        if os.path.exists(file_path):
            fs = FileSystemStorage(file_path)
            with fs.open(file_path) as pdf:
                mail.attach(file_name, pdf.read())
        mail.send()
        messages.success(self.request, "Mail sent")
        return HttpResponseRedirect("/invoices/")


class DownloadInvoiceView(View):

    """
    Download invoice view
    """

    def get(self, request, *args, **kwargs):
        invoice_id = int(self.kwargs["invoice_id"])
        invoice_data = (
            Invoice.objects.filter(id=invoice_id).values("invoice_num").first()
        )
        file_name = "INV" + invoice_data["invoice_num"]
        file_path = os.path.join(settings.MEDIA_ROOT, "invoice_pdf", file_name)

        if os.path.exists(file_path):
            fs = FileSystemStorage(file_path)
            with fs.open(file_path) as pdf:
                response = HttpResponse(pdf, content_type="application/pdf")
                response["Content-Disposition"] = 'attachment; filename= "{}"'.format(
                    file_name
                )
                return response


class InvoiceDeleteView(View):

    """
    Delete invoice and involiceline releted to invoice from db
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(InvoiceDeleteView, self).dispatch(request, *args, **kwargs)

    @transaction.atomic
    def get(self, request, *args, **kwargs):
        invoice_id = int(self.kwargs["invoice_id"])
        InvoiceLine.objects.filter(invoice_id=invoice_id).delete()
        invoice_data = Invoice.objects.filter(id=invoice_id).first()
        file_path = os.path.join(
            settings.MEDIA_ROOT, "invoice_pdf", "INV" + invoice_data.invoice_num
        )

        if os.path.exists(file_path):
            os.remove(file_path)

        invoice_data.delete()
        messages.success(self.request, "Invoice removed sucessfully")
        return HttpResponseRedirect("/invoices/")


def make_invoice_file(request, invoice_id):

    """
    when user create Invoice so we can generate invoice pdf in media location
    """
    invoice_data = Invoice.objects.filter(id=int(invoice_id)).first()
    invoice_line_data = InvoiceLine.objects.filter(invoice_id=int(invoice_id))
    file_path = os.path.join(settings.MEDIA_ROOT, "invoice_pdf")
    html_string = render_to_string(
        "invoice/download_invoice.html",
        {
            "invoice_data": invoice_data,
            "invoice_line_data": invoice_line_data,
            "base_url": request.build_absolute_uri(invoice_data.invoice_logo.url),
        },
    )
    html = HTML(string=html_string)
    final_path = file_path + "/" + ("INV" + invoice_data.invoice_num)
    html.write_pdf(target=final_path)
    return "sucesss"


class LoginView(View):

    """
    User login view
    """

    def get(self, request):
        return render(request, "invoice/login.html")

    def post(self, request):
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                print(user, "user")
                login(request, user)
                return HttpResponseRedirect("/invoices")
        else:
            messages.error(request, "Invalid username or password")
            return render(request, "invoice/login.html")


class LogoutView(View):

    """
    Logout view
    """

    def get(self, request):
        log_out_user(self.request)
        return HttpResponseRedirect("/")


class UserRegistrationView(View):

    """
    New user registration view
    """

    def get(self, request):
        return render(request, "invoice/registration.html")

    def post(self, request):
        username = request.POST["username"]
        password = make_password(request.POST["password"])
        first_name = request.POST["first_name"]

        if (User.objects.filter(username=username).count()) >= 1:
            messages.error(request, "Username is already exits.")
            return render(request, "invoice/registration.html")

        user = User.objects.create(
            username=username, password=password, first_name=first_name
        )
        login(request, user)
        return HttpResponseRedirect("/invoices/")
