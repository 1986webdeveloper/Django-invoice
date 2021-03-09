from django.db import models
from django.contrib.auth.models import User


class Invoice(models.Model):
    invoice_logo = models.ImageField(upload_to='images/invoice_img', null=True, blank=True)
    invoice_num = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey(User, related_name="users", on_delete=models.CASCADE, null=True, blank=True)
    invoice_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    invoice_from = models.CharField(max_length=100, blank=True, null=True)
    notes = models.CharField(max_length=100, blank=True, null=True)
    payment_terms = models.CharField(max_length=100, blank=True, null=True)
    terms_and_conditions = models.CharField(max_length=100, blank=True, null=True)
    billing_address = models.CharField(max_length=200, blank=True, null=True)
    shipping_address = models.CharField(max_length=200, blank=True, null=True)
    total = models.DecimalField(max_digits=20, decimal_places=3, blank=True, null=True)
    discount = models.DecimalField(max_digits=20, decimal_places=3, blank=True, null=True)
    shipping_charge = models.DecimalField(max_digits=20, decimal_places=3, blank=True, null=True)
    tax = models.DecimalField(max_digits=20, decimal_places=3, blank=True, null=True)
    balance_due = models.DecimalField(max_digits=20, decimal_places=3, blank=True, null=True)
    subtotal = models.DecimalField(max_digits=20, decimal_places=3, blank=True, null=True)
    amount_paid = models.DecimalField(max_digits=20, decimal_places=3, blank=True, null=True)


class InvoiceLine(models.Model):
    invoice = models.ForeignKey('Invoice', null=True, blank=True, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=150, blank=True, null=True)
    item_description = models.CharField(max_length=200, blank=True, null=True)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=20, decimal_places=3, blank=True, null=True)
    line_total = models.DecimalField(max_digits=20, decimal_places=3, blank=True, null=True)
