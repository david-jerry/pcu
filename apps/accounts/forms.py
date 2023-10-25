from django import forms
from .models import CustomUser, UserCardHistory, UserAccount

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'password']

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")
        return confirm_password
    
class TransferFunds(forms.ModelForm):
    class Meta:
        model = UserCardHistory
        fields = [
            "receiver_name",
            "receiver_account_number",
            "reason",
            "amount",
        ]
        
class AddAccountForm(forms.ModelForm):
    class Meta:
        model = UserAccount
        fields = [
            "currency",
            "pin",
            "account_type"
        ]