from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from allauth.account.forms import SignupForm, LoginForm
from .models import Task
from .profile import UserProfile, ROLE_CHOICES

class TaskForm(forms.ModelForm):
    """Form for creating and editing tasks"""
    
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'status', 'priority', 
            'due_date', 'assigned_to', 'tags', 
            'estimated_hours', 'actual_hours'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter task title...',
                'maxlength': '200'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe the task in detail...',
                'rows': 4
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'due_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter tags separated by commas (e.g., urgent, frontend, bug)',
                'maxlength': '200'
            }),
            'estimated_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.25',
                'min': '0'
            }),
            'actual_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.25',
                'min': '0'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customize choices for status and priority
        self.fields['status'].choices = Task.STATUS_CHOICES
        self.fields['priority'].choices = Task.PRIORITY_CHOICES
        
        # Customize assigned_to field to show active users only
        self.fields['assigned_to'].queryset = User.objects.filter(is_active=True)
        self.fields['assigned_to'].empty_label = "Select a user (optional)"
        
        # Add help text
        self.fields['due_date'].help_text = "When should this task be completed?"
        self.fields['tags'].help_text = "Use tags to categorize and filter tasks easily"
        self.fields['estimated_hours'].help_text = "How many hours do you estimate this task will take?"
        self.fields['actual_hours'].help_text = "Track the actual time spent on this task"
    
    def clean_title(self):
        """Validate task title"""
        title = self.cleaned_data.get('title')
        if title and len(title.strip()) < 3:
            raise forms.ValidationError("Task title must be at least 3 characters long.")
        return title.strip()
    
    def clean_estimated_hours(self):
        """Validate estimated hours"""
        hours = self.cleaned_data.get('estimated_hours')
        if hours is not None and hours < 0:
            raise forms.ValidationError("Estimated hours cannot be negative.")
        return hours
    
    def clean_actual_hours(self):
        """Validate actual hours"""
        hours = self.cleaned_data.get('actual_hours')
        if hours is not None and hours < 0:
            raise forms.ValidationError("Actual hours cannot be negative.")
        return hours
    
    def clean_due_date(self):
        """Validate due date"""
        due_date = self.cleaned_data.get('due_date')
        if due_date and self.instance.created_at:
            # If editing an existing task
            if due_date < self.instance.created_at:
                raise forms.ValidationError("Due date cannot be earlier than task creation date.")
        return due_date

class TaskSearchForm(forms.Form):
    """Form for searching and filtering tasks"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by title, description, or tags...',
            'name': 'search'
        })
    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + list(Task.STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    priority = forms.ChoiceField(
        choices=[('', 'All Priorities')] + list(Task.PRIORITY_CHOICES),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    assignment = forms.ChoiceField(
        choices=[
            ('', 'All Tasks'),
            ('assigned_to_me', 'Assigned to Me'),
            ('created_by_me', 'Created by Me'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

class TaskQuickCreateForm(forms.ModelForm):
    """Simplified form for quick task creation"""
    
    class Meta:
        model = Task
        fields = ['title', 'priority', 'due_date', 'assigned_to']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Quick task title...',
                'maxlength': '200'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'due_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['priority'].choices = Task.PRIORITY_CHOICES
        self.fields['assigned_to'].queryset = User.objects.filter(is_active=True)
        self.fields['assigned_to'].empty_label = "Assign to (optional)"
    
    def clean_title(self):
        """Validate task title"""
        title = self.cleaned_data.get('title')
        if title and len(title.strip()) < 3:
            raise forms.ValidationError("Task title must be at least 3 characters long.")
        return title.strip()
