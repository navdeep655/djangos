from django import forms
def check_gmail(value):
    if not value.endswith("@gmail.com"):
        raise forms.ValidationError("Only Gmail allowed!")

class StudentForm(forms.Form):
    name=forms.CharField(max_length=50,label="Name",required=True,initial="Enter Your Name")
    age=forms.IntegerField(min_value=18,max_value=30,label="Age",initial="Enter your age")
    email=forms.EmailField(required=True,label="E-mail",initial="test@gmail.com",validators=[check_gmail])
    address = forms.CharField(widget=forms.Textarea)
    #password = forms.CharField(widget=forms.PasswordInput())
