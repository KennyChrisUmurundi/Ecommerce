from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICES = (

('S','Stripe'),
('P','PayPal'),
)
class CheckoutForm(forms.Form):

    street_address = forms.CharField(widget=forms.TextInput(attrs={
    "placeholder":"123 strt rd",
    "class":"form-control",
    }))

    apartment_adress = forms.CharField(required=False,widget=forms.TextInput(attrs={
    "placeholder":"building block",
    'class':'form-control',
    }))

    country = CountryField(blank_label='(select country)').formfield(widget=CountrySelectWidget(attrs={
    'class':'custom-select d-block w-100'
    }))

    zips = forms.CharField(widget=forms.TextInput(attrs={

    'class':'form-control',}))

    same_billing_address = forms.BooleanField(required=False)
    save_info = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(widget=forms.RadioSelect,choices=PAYMENT_CHOICES)

# class SellItem(forms.Form):
#
#     vendor = forms.ForeignKey(User,on_delete=models.CASCADE)
