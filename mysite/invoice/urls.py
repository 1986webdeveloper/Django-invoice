from django.contrib import admin
from django.conf.urls import url
from invoice import views
from django.conf import settings 
from django.conf.urls.static import static 

urlpatterns = [ 
    url(r'^$', views.LoginView.as_view(), name='sign_in'),
    url(r'^new_user_registrion/' ,views.UserRegistrationView.as_view(),name='new_user_registrion'),
    url(r'^dashboard/create_invoice/' ,views.InvoiceCreateView.as_view(),name='create_invoice'),
    url(r'^invoices/' ,views.InvoiceListView.as_view(),name='my_invoices'),
    url(r'^send_mail/(?P<invoice_id>[0-9]+)/' ,views.SendMailView.as_view(),name='send_mail'),
    url(r'^delete_invoice/(?P<invoice_id>[0-9]+)' ,views.InvoiceDeleteView.as_view(),name='delete_invoice'),
    url(r'^download_invoice/(?P<invoice_id>[0-9]+)/' ,views.DownloadInvoiceView.as_view(),name='download_invoice'),
    url(r'^dashboard/invoice_detail/(?P<invoice_id>[0-9]+)/' ,views.InvoiceDetailView.as_view(),name='invoice_detail'),
    url(r'^logout/' ,views.LogoutView.as_view(),name='logout')
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
