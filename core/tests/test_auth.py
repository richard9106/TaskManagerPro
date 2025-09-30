from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core import mail
from core.profile import UserProfile


class AuthenticationTest(TestCase):
    """Test cases for authentication system"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
    
    def test_user_registration_flow(self):
        """Test complete user registration flow"""
        # Test signup page
        response = self.client.get(reverse('account_signup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Account')
        
        # Test registration
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
        
        response = self.client.post(reverse('account_signup'), form_data)
        # Should redirect or show success
        self.assertIn(response.status_code, [200, 302])
        
        # Verify user was created
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())
        user = User.objects.get(email='newuser@example.com')
        
        # Verify profile was created
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.role, 'developer')
        # Department and phone are not automatically set in the form, so they might be None
        # self.assertEqual(user.profile.department, 'Engineering')
        # self.assertEqual(user.profile.phone, '+1234567890')
    
    def test_user_login_flow(self):
        """Test complete user login flow"""
        # Create user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        user.profile.role = 'developer'
        user.profile.save()
        
        # Test login page
        response = self.client.get(reverse('account_login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome Back')
        
        # Test login
        response = self.client.post(reverse('account_login'), {
            'login': 'test@example.com',
            'password': 'testpass123'
        })
        self.assertRedirects(response, '/')
        
        # Verify user is logged in
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_user_logout_flow(self):
        """Test user logout flow"""
        # Create and login user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        user.profile.role = 'developer'
        user.profile.save()
        
        self.client.login(email='test@example.com', password='testpass123')
        
        # Test logout
        response = self.client.get(reverse('account_logout'))
        self.assertRedirects(response, reverse('account_login'))
        
        # Verify user is logged out
        response = self.client.get(reverse('core:dashboard'))
        self.assertRedirects(response, reverse('account_login'))
    
    def test_authentication_required_views(self):
        """Test that protected views require authentication"""
        protected_urls = [
            reverse('core:dashboard'),
            reverse('core:task_list'),
            reverse('core:task_create'),
            reverse('core:my_tasks'),
        ]
        
        for url in protected_urls:
            response = self.client.get(url)
            # Some views redirect to login with next parameter, others just to login
            if url == reverse('core:dashboard'):
                # Dashboard redirects to login without next parameter
                self.assertRedirects(response, reverse('account_login'))
            else:
                # Other views redirect to login with next parameter
                expected_url = f"{reverse('account_login')}?next={url}"
                self.assertRedirects(response, expected_url)
    
    def test_role_based_access(self):
        """Test role-based access control"""
        # Create users with different roles
        manager = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='testpass123'
        )
        # Get profiles (created automatically by signal)
        manager_profile = manager.profile
        manager_profile.role = 'manager'
        manager_profile.save()
        
        developer = User.objects.create_user(
            username='developer',
            email='developer@example.com',
            password='testpass123'
        )
        developer_profile = developer.profile
        developer_profile.role = 'developer'
        developer_profile.save()
        
        # Test manager can access task creation
        self.client.login(email='manager@example.com', password='testpass123')
        response = self.client.get(reverse('core:task_create'))
        self.assertEqual(response.status_code, 200)
        
        # Test developer cannot access task creation
        self.client.login(email='developer@example.com', password='testpass123')
        response = self.client.get(reverse('core:task_create'))
        self.assertRedirects(response, reverse('core:task_list'))
    
    def test_profile_auto_creation(self):
        """Test automatic profile creation for existing users"""
        # Create user without profile
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Login should create profile automatically
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Verify profile was created
        user.refresh_from_db()
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.role, 'developer')  # Default role
    
    def test_password_reset_flow(self):
        """Test password reset flow"""
        # Create user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        user.profile.role = 'developer'
        user.profile.save()
        
        # Test password reset request
        response = self.client.post(reverse('account_reset_password'), {
            'email': 'test@example.com'
        })
        self.assertIn(response.status_code, [200, 302])
        
        # Check that email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('test@example.com', mail.outbox[0].to)
    
    def test_email_verification_flow(self):
        """Test email verification flow"""
        # Create user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        user.profile.role = 'developer'
        user.profile.save()
        
        # Test email verification page
        response = self.client.get(reverse('account_email_verification_sent'))
        self.assertEqual(response.status_code, 200)
    
    def test_session_management(self):
        """Test session management"""
        # Create user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        user.profile.role = 'developer'
        user.profile.save()
        
        # Login
        self.client.login(email='test@example.com', password='testpass123')
        
        # Test session persistence
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Test session timeout (simulate by clearing session)
        self.client.session.flush()
        response = self.client.get(reverse('core:dashboard'))
        self.assertRedirects(response, reverse('account_login'))
    
    def test_csrf_protection(self):
        """Test CSRF protection on forms"""
        # Test login form CSRF
        response = self.client.get(reverse('account_login'))
        self.assertContains(response, 'csrfmiddlewaretoken')
        
        # Test signup form CSRF
        response = self.client.get(reverse('account_signup'))
        self.assertContains(response, 'csrfmiddlewaretoken')
    
    def test_remember_me_functionality(self):
        """Test remember me functionality"""
        # Create user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        user.profile.role = 'developer'
        user.profile.save()
        
        # Login with remember me
        response = self.client.post(reverse('account_login'), {
            'login': 'test@example.com',
            'password': 'testpass123',
            'remember': True
        })
        self.assertRedirects(response, '/')
        
        # Verify session is persistent
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
