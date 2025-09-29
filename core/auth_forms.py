from django import forms
from django.contrib.auth.models import User
from allauth.account.forms import SignupForm, LoginForm
from .profile import UserProfile, ROLE_CHOICES

class CustomSignupForm(SignupForm):
    """Custom signup form with role selection"""
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        })
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    department = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Department (optional)'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone number (optional)'
        })
    )
    
    def save(self, request):
        user = super().save(request)
        
        # Update user's first name and last name
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        
        # Create or update user profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.role = self.cleaned_data['role']
        profile.department = self.cleaned_data.get('department', '')
        profile.phone = self.cleaned_data.get('phone', '')
        profile.save()
        
        return user

class CustomLoginForm(LoginForm):
    """Custom login form with corporate styling"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].widget = forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email'
        })
        self.fields['password'].widget = forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password'
        })
        # Only try to modify remember field if it exists
        if 'remember' in self.fields:
            self.fields['remember'].widget = forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })

class ProfileEditForm(forms.ModelForm):
    """Form for editing user profile"""
    
    class Meta:
        model = UserProfile
        fields = ['role', 'bio', 'phone', 'department', 'weekly_hours_available', 'is_active_member']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself...'
            }),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'weekly_hours_available': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100'
            }),
            'is_active_member': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            # Update user information
            profile.user.first_name = self.cleaned_data['first_name']
            profile.user.last_name = self.cleaned_data['last_name']
            profile.user.email = self.cleaned_data['email']
            profile.user.save()
            
            profile.save()
        return profile
