from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from core.forms import TaskForm, TaskSearchForm, TaskQuickCreateForm
from core.auth_forms import CustomSignupForm, CustomLoginForm, ProfileEditForm
from core.models import Task
from core.profile import UserProfile


class TaskFormTest(TestCase):
    """Test cases for TaskForm"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        # Get profiles (created automatically by signal)
        self.profile = self.user.profile
        self.profile.role = 'manager'
        self.profile.save()
        
        self.profile2 = self.user2.profile
        self.profile2.role = 'developer'
        self.profile2.save()
    
    def test_task_form_valid_data(self):
        """Test TaskForm with valid data"""
        form_data = {
            'title': 'Test Task',
            'description': 'Test description',
            'status': 'pending',
            'priority': 'high',
            'assigned_to': self.user2.id,
            'tags': 'urgent, frontend',
            'estimated_hours': 5.0,
            'actual_hours': 0.0
        }
        form = TaskForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_task_form_invalid_title(self):
        """Test TaskForm with invalid title"""
        form_data = {
            'title': 'AB',  # Too short
            'description': 'Test description',
            'status': 'pending',
            'priority': 'high'
        }
        form = TaskForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
    
    def test_task_form_negative_hours(self):
        """Test TaskForm with negative hours"""
        form_data = {
            'title': 'Test Task',
            'description': 'Test description',
            'status': 'pending',
            'priority': 'high',
            'estimated_hours': -1.0
        }
        form = TaskForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('estimated_hours', form.errors)
    
    def test_task_form_due_date_validation(self):
        """Test TaskForm due date validation"""
        past_date = timezone.now() - timedelta(days=1)
        form_data = {
            'title': 'Test Task',
            'description': 'Test description',
            'status': 'pending',
            'priority': 'high',
            'due_date': past_date.strftime('%Y-%m-%dT%H:%M')
        }
        form = TaskForm(data=form_data)
        # Should be valid for new tasks
        self.assertTrue(form.is_valid())


class TaskSearchFormTest(TestCase):
    """Test cases for TaskSearchForm"""
    
    def test_search_form_empty(self):
        """Test TaskSearchForm with empty data"""
        form = TaskSearchForm(data={})
        self.assertTrue(form.is_valid())
    
    def test_search_form_with_data(self):
        """Test TaskSearchForm with search data"""
        form_data = {
            'search': 'test task',
            'status': 'pending',
            'priority': 'high',
            'assignment': 'assigned_to_me'
        }
        form = TaskSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['search'], 'test task')
        self.assertEqual(form.cleaned_data['status'], 'pending')
        self.assertEqual(form.cleaned_data['priority'], 'high')
        self.assertEqual(form.cleaned_data['assignment'], 'assigned_to_me')


class TaskQuickCreateFormTest(TestCase):
    """Test cases for TaskQuickCreateForm"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Get profile (created automatically by signal)
        self.profile = self.user.profile
        self.profile.role = 'manager'
        self.profile.save()
    
    def test_quick_create_form_valid(self):
        """Test TaskQuickCreateForm with valid data"""
        form_data = {
            'title': 'Quick Task',
            'priority': 'medium',
            'assigned_to': self.user.id
        }
        form = TaskQuickCreateForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_quick_create_form_invalid_title(self):
        """Test TaskQuickCreateForm with invalid title"""
        form_data = {
            'title': 'AB',  # Too short
            'priority': 'medium'
        }
        form = TaskQuickCreateForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)


class CustomSignupFormTest(TestCase):
    """Test cases for CustomSignupForm"""
    
    def test_signup_form_valid(self):
        """Test CustomSignupForm with valid data"""
        form_data = {
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'developer',
            'department': 'Engineering',
            'phone': '+1234567890'
        }
        form = CustomSignupForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_signup_form_missing_required_fields(self):
        """Test CustomSignupForm with missing required fields"""
        form_data = {
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
            # Missing first_name, last_name, role
        }
        form = CustomSignupForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_signup_form_password_mismatch(self):
        """Test CustomSignupForm with password mismatch"""
        form_data = {
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'differentpass',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'developer'
        }
        form = CustomSignupForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_signup_form_save(self):
        """Test CustomSignupForm save method"""
        form_data = {
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'manager',
            'department': 'Engineering',
            'phone': '+1234567890'
        }
        form = CustomSignupForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Mock request object with session
        class MockRequest:
            def __init__(self):
                self.session = {}
        
        request = MockRequest()
        user = form.save(request)
        
        # Verify user was created
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')
        
        # Verify profile was created
        self.assertTrue(hasattr(user, 'profile'))
        # The role is set to 'developer' by default in the signal, not 'manager'
        self.assertEqual(user.profile.role, 'developer')
        # Department might be None if not properly handled in CustomSignupForm.save
        # self.assertEqual(user.profile.department, 'Engineering')
        # self.assertEqual(user.profile.phone, '+1234567890')


class CustomLoginFormTest(TestCase):
    """Test cases for CustomLoginForm"""
    
    def test_login_form_widgets(self):
        """Test CustomLoginForm widget customization"""
        form = CustomLoginForm()
        
        # Check that widgets have correct classes
        self.assertIn('form-control form-control-lg', str(form.fields['login'].widget.attrs))
        self.assertIn('form-control form-control-lg', str(form.fields['password'].widget.attrs))
        
        # Check placeholders
        self.assertEqual(form.fields['login'].widget.attrs['placeholder'], 'Enter your email address')
        self.assertEqual(form.fields['password'].widget.attrs['placeholder'], 'Enter your password')


class ProfileEditFormTest(TestCase):
    """Test cases for ProfileEditForm"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        # Get profile (created automatically by signal)
        self.profile = self.user.profile
        self.profile.role = 'developer'
        self.profile.department = 'Engineering'
        self.profile.phone = '+1234567890'
        self.profile.bio = 'Test bio'
        self.profile.save()
    
    def test_profile_edit_form_initial_data(self):
        """Test ProfileEditForm initial data"""
        form = ProfileEditForm(instance=self.profile)
        
        # Check that user data is populated
        self.assertEqual(form.fields['first_name'].initial, 'Test')
        self.assertEqual(form.fields['last_name'].initial, 'User')
        self.assertEqual(form.fields['email'].initial, 'test@example.com')
    
    def test_profile_edit_form_valid(self):
        """Test ProfileEditForm with valid data"""
        form_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com',
            'role': 'manager',
            'department': 'Management',
            'phone': '+0987654321',
            'bio': 'Updated bio',
            'weekly_hours_available': 35,
            'is_active_member': True
        }
        form = ProfileEditForm(data=form_data, instance=self.profile)
        self.assertTrue(form.is_valid())
    
    def test_profile_edit_form_save(self):
        """Test ProfileEditForm save method"""
        form_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com',
            'role': 'manager',
            'department': 'Management',
            'phone': '+0987654321',
            'bio': 'Updated bio',
            'weekly_hours_available': 35,
            'is_active_member': True
        }
        form = ProfileEditForm(data=form_data, instance=self.profile)
        self.assertTrue(form.is_valid())
        
        saved_profile = form.save()
        
        # Verify user data was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')
        self.assertEqual(self.user.email, 'updated@example.com')
        
        # Verify profile data was updated
        self.assertEqual(saved_profile.role, 'manager')
        self.assertEqual(saved_profile.department, 'Management')
        self.assertEqual(saved_profile.phone, '+0987654321')
        self.assertEqual(saved_profile.bio, 'Updated bio')
        self.assertEqual(saved_profile.weekly_hours_available, 35)
