from datetime import datetime, timedelta
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email

GENDER_CHOICES = (
    ("", "Please select"),
    ("M", 'Men'),
    ("F", 'Woman'),
    ("O", 'Other'),
    ("N", 'Rather not Say')
)


class RegisterForm(forms.Form):
    firstname = forms.CharField(required=True, label="First name",
                                widget=forms.TextInput(attrs={"class": "form-control"}))
    lastname = forms.CharField(required=True, label="Last Name",
                               widget=forms.TextInput(attrs={"class": "form-control"}))
    user_email = forms.EmailField(required=True, label="E-mail", widget=forms.TextInput(
        attrs={"class": "form-control", "aria-describedby": "inputGroupPrepend"}))
    birthday = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', "class": "form-control"}), required=True, label="Birthday")
    gender = forms.ChoiceField(required=False, choices=GENDER_CHOICES,
                               widget=forms.Select(attrs={"class": "form-select"}), label="Gender")

    def clean(self):
        cd = self.cleaned_data
        username = cd.get('user_email')
        date = cd.get('birthday')

        if not cd.get("firstname"):
            self.add_error("firstname", "Missing first name.")

        if not cd.get("lastname"):
            self.add_error("lastname", "Missing first name.")

        if validate_email(username):
            self.add_error("user_email", "Please provide a valid e-mail")

        if User.objects.filter(username=username):
            self.add_error("user_email", "User is already in use. Please select another.")

        if not cd.get("gender"):
            self.add_error("gender", "Please select a Gender")

        time_between_insertion = datetime.now().date()
        if (time_between_insertion - date) // timedelta(days=365.2425) < 18:
            self.add_error("birthday", "You need to be +18")

        return self.cleaned_data


class PasswordForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}), label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}), label="Repeat Password")

    def clean(self):
        cd = self.cleaned_data
        password = cd.get("password1")
        password2 = cd.get("password2")

        try:
            validate_password(password)
        except forms.ValidationError as error:
            self.add_error('password1', error)

        if password != password2:
            self.add_error("password2", "Passwords are different please re-enter")

        return self.cleaned_data


class ResetForm(forms.Form):
    user_email = forms.EmailField(required=True, label="E-mail", widget=forms.TextInput(
        attrs={"class": "form-control", "aria-describedby": "inputGroupPrepend"}))

    def clean(self):
        cd = self.cleaned_data
        username = cd.get('user_email')
        if not User.objects.filter(username=username):
            self.add_error("user_email", "Please provide a valid e-mail")


class RechargeForm(forms.Form):
    coinsinput = forms.IntegerField(required=True, min_value=15, max_value=2000, widget=forms.TextInput(attrs={
        "class": "form-control", "aria-describedby": "inputGroup-sizing-default", 'type': 'number', 'min': 15}))

    def clean(self):
        cd = self.cleaned_data
        coin_input = cd.get("coinsinput")
        print(coin_input)
        if not str(coin_input).isdecimal():
            self.add_error("coinsinput", "Please provide a number!")

        if coin_input < 15:
            self.add_error("coinsinput", "Minimum Recharge: 15 BlockCoins")

        if coin_input > 2000:
            self.add_error("coinsinput", "Maximum Recharge: 2000 BlockCoins")
