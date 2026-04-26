from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Product, ContactMessage, UserProfile


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'First name'}))
    last_name  = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Last name'}))
    email      = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email address'}))

    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'username':  'Choose a username',
            'password1': 'Create password',
            'password2': 'Confirm password',
        }
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input'
            if name in placeholders:
                field.widget.attrs['placeholder'] = placeholders[name]


class ProductForm(forms.ModelForm):
    class Meta:
        model  = Product
        fields = ['name', 'category', 'description', 'price', 'stock', 'image', 'is_available']
        widgets = {
            'name':        forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Product name'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Describe the product…'}),
            'price':       forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0.00', 'step': '0.01', 'min': '0'}),
            'stock':       forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Quantity in stock', 'min': '0'}),
            'category':    forms.Select(attrs={'class': 'form-input'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'image':       forms.ClearableFileInput(attrs={'class': 'form-file', 'accept': 'image/*'}),
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model  = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name':    forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Your full name'}),
            'email':   forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'your@email.com'}),
            'subject': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'How can we help?'}),
            'message': forms.Textarea(attrs={'class': 'form-input', 'rows': 5, 'placeholder': 'Write your message here…'}),
        }

# new form for user profile
class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First name'}))
    last_name  = forms.CharField(max_length=100, required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last name'}))
    email      = forms.EmailField(required=False,
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email address'}))

    class Meta:
        model  = UserProfile
        fields = ['avatar', 'phone', 'address', 'city', 'country', 'bio']
        widgets = {
            'avatar':  forms.ClearableFileInput(attrs={'class': 'form-file', 'accept': 'image/*', 'id': 'id_avatar'}),
            'phone':   forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+1 234 567 8900'}),
            'address': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Street address'}),
            'city':    forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'City'}),
            'country': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Country'}),
            'bio':     forms.Textarea(attrs={'class': 'form-input', 'rows': 3,
                                            'placeholder': 'Tell us a little about yourself…'}),
        }