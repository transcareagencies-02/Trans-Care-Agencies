from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterForm(UserCreationForm):

    first_name = forms.CharField(required=True, max_length=150)
    last_name = forms.CharField(required=True, max_length=150)
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=True, max_length=20)
    county = forms.CharField(required=True, max_length=100)
    city = forms.CharField(required=True, max_length=100)
    postal_address = forms.CharField(required=False, max_length=255)
    company_name = forms.CharField(required=False, max_length=255)
    kra_pin = forms.CharField(required=False, max_length=50)
    customer_type = forms.ChoiceField(
        choices=User.CUSTOMER_TYPES,
        initial='individual'
    )
    profile_image = forms.ImageField(required=False)
    agreed_terms = forms.BooleanField(required=True)
    agreed_privacy = forms.BooleanField(required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "county",
            "city",
            "postal_address",
            "company_name",
            "kra_pin",
            "customer_type",
            "profile_image",
            "password1",
            "password2",
            "agreed_terms",
            "agreed_privacy",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "input input-bordered w-full",
            })

        self.fields["username"].widget.attrs.update({
            "placeholder": "Username"
        })
        self.fields["first_name"].widget.attrs.update({
            "placeholder": "First Name"
        })
        self.fields["last_name"].widget.attrs.update({
            "placeholder": "Last Name"
        })
        self.fields["email"].widget.attrs.update({
            "placeholder": "Email Address"
        })
        self.fields["phone"].widget.attrs.update({
            "placeholder": "Phone Number"
        })
        self.fields["county"].widget.attrs.update({
            "placeholder": "County"
        })
        self.fields["city"].widget.attrs.update({
            "placeholder": "Town/City"
        })
        self.fields["postal_address"].widget.attrs.update({
            "placeholder": "Postal Address"
        })
        self.fields["company_name"].widget.attrs.update({
            "placeholder": "Company Name"
        })
        self.fields["kra_pin"].widget.attrs.update({
            "placeholder": "KRA PIN"
        })
        self.fields["customer_type"].widget.attrs.update({
            "class": "select select-bordered w-full"
        })
        self.fields["profile_image"].widget.attrs.update({
            "class": "file-input w-full"
        })
        self.fields["password1"].widget.attrs.update({
            "placeholder": "Password"
        })
        self.fields["password2"].widget.attrs.update({
            "placeholder": "Confirm Password"
        })


class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'county',
            'city',
            'postal_address',
            'company_name',
            'kra_pin',
            'customer_type',
            'profile_image',
            'newsletter',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "input input-bordered w-full",
                "placeholder": field.label
            })

        if 'customer_type' in self.fields:
            self.fields['customer_type'].widget.attrs.update({
                "class": "select select-bordered w-full"
            })
        if 'profile_image' in self.fields:
            self.fields['profile_image'].widget.attrs.update({
                "class": "file-input w-full"
            })


class CustomPasswordChangeForm(PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["old_password"].widget.attrs.update({
            "class": "input input-bordered w-full",
            "placeholder": "Current Password"
        })

        self.fields["new_password1"].widget.attrs.update({
            "class": "input input-bordered w-full",
            "placeholder": "New Password"
        })

        self.fields["new_password2"].widget.attrs.update({
            "class": "input input-bordered w-full",
            "placeholder": "Confirm New Password"
        })