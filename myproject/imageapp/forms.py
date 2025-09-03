from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
import re
from .models import CustomUser, UploadedImage


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        error_messages={
            "required": "Email is required",
            "invalid": "Enter a valid email address"
        }
    )
    name = forms.CharField(
        required=True,
        error_messages={"required": "Name is required"}
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'name', 'password1', 'password2')

    def clean_password1(self):
        password = self.cleaned_data.get("password1")

        # Check minimum length
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")

        # Check uppercase
        if not re.search(r"[A-Z]", password):
            raise ValidationError("Password must contain at least one uppercase letter.")

        # Check lowercase
        if not re.search(r"[a-z]", password):
            raise ValidationError("Password must contain at least one lowercase letter.")

        # Check digit
        if not re.search(r"[0-9]", password):
            raise ValidationError("Password must contain at least one digit.")

        # Check special character
        if not re.search(r"[@$!%*?&#]", password):
            raise ValidationError("Password must contain at least one special character (@, $, !, %, *, ?, &, #).")

        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.name = self.cleaned_data['name']
        # Set username as email prefix
        user.username = self.cleaned_data['email'].split('@')[0]
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(
        error_messages={
            "required": "Email is required",
            "invalid": "Enter a valid email address"
        }
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        error_messages={"required": "Password is required"}
    )


class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedImage
        fields = ['image']
