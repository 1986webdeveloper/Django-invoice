from invoice.models import Invoice,InvoiceLine
from django import forms  
from django.forms.models import inlineformset_factory


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = '__all__'

class InvoiceLineForm(forms.ModelForm):    

    item_name = forms.CharField(max_length=100)
    item_description = forms.CharField()
    quantity = forms.IntegerField()
    price = forms.DecimalField()
    line_total = forms.DecimalField()

    class Meta:
        model = InvoiceLine
        exclude = ('id', 'item_name')
        # fields = ('item_name','item_description','quantity','price','line_total')
        # labels = {
        #     'item_name': 'Item Name',
        #     'item_description': 'Item description',
        #     'quantity':'Quantity',
        #     'price':'Price',
        #     'line_total':'Total'
        # }

InvoiceLineFormSet = inlineformset_factory(Invoice, InvoiceLine,form=InvoiceLineForm,extra=1,can_delete = False)
