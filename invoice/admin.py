from django.contrib import admin

# Register your models here.
from invoice.models import Invoice,InvoiceLine

admin.site.register(Invoice)
admin.site.register(InvoiceLine)