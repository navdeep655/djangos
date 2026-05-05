from django import forms
from django.contrib.auth.models import User

class SignupForm(forms.ModelForm):
    password1=forms.CharField(label="Password",widget=forms.PasswordInput(attrs={"placeholder":"Enter Paswword"}))
    password2=forms.CharField(label="Confirm Password",widget=forms.PasswordInput(attrs={"placeholder":"Confirm Paswword"}))

    username=forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Enter Username"}))
    email=forms.EmailField(widget=forms.EmailInput(attrs={"placeholder":"enter Email"}))

    class Meta:
        model=User
        fields=["username","email"]

    def clean_password2(self):
        p1=self.cleaned_data.get('password1')
        p2=self.cleaned_data.get('password2')
        if p1!=p2:
            raise forms.ValidationError("password do not match")
        return p2
    
    def clean_username(self):
        username=self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("username already exists")
        return username