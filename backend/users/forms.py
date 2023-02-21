from django.contrib.auth import get_user_model
from django.contrib.auth import forms as auth_forms
from django import forms
from django.core.exceptions import ValidationError

User = get_user_model()


class MyRegistrationForm(auth_forms.UserCreationForm):
    error_messages = {
        'required': 'This field is required.',
    }
    username = None
    email = forms.EmailField(
        label='Your email',
        max_length=254,
        error_messages=error_messages,
    )
    first_name = forms.CharField(
        required=False,
        label='First name',
        error_messages=error_messages
    )

    def clean_email(self):
        new_email = self.cleaned_data.get('email').lower()
        existing = User.objects.filter(email=new_email)

        if existing:
            raise ValidationError(f'User with this email address already exists.')
        return new_email

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name').title()
        return first_name

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('Пароли не совпадают')
        return password2

    def save(self, commit=True):
        user = User.objects.create(
            email=self.cleaned_data['email'],
            username=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            password=self.cleaned_data['password2'],
        )
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

    class Meta(auth_forms.UserCreationForm.Meta):
        model = User
        fields = (
            'email',
            'first_name',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Your email',
        })
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Your name',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm the password',
        })


class MyAuthenticationForm(auth_forms.AuthenticationForm):
    username = auth_forms.UsernameField(widget=forms.TextInput(attrs={
        'autofocus': True
    }))

    error_messages = {
        'invalid_login': 'Invalid login data entered.',
    }

    class Meta:
        model = User
        fields = ['email', 'password']

    def __init__(self, request=None, *args, **kwargs):
        super(MyAuthenticationForm, self).__init__(request, *args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter email',
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control text-dark',
            'placeholder': 'Enter password',
        })
