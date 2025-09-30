from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from core.models import Task
from core.profile import UserProfile


class TaskViewsTest(TestCase):
    """Test cases for task views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create users
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        # Get profiles (created automatically by signal)
        self.manager_profile = self.user.profile
        self.manager_profile.role = 'manager'
        self.manager_profile.save()
        
        self.developer_profile = self.user2.profile
        self.developer_profile.role = 'developer'
        self.developer_profile.save()
        
        # Create test tasks
        self.task = Task.objects.create(
            title='Test Task',
            description='Test description',
            created_by=self.user,
            assigned_to=self.user2,
            status='pending',
            priority='high'
        )
    
    def test_dashboard_redirects_unauthenticated(self):
        """Test that dashboard redirects unauthenticated users to login"""
        response = self.client.get(reverse('core:dashboard'))
        self.assertRedirects(response, reverse('account_login'))
    
    def test_dashboard_authenticated_user(self):
        """Test dashboard for authenticated user"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')
    
    def test_task_list_redirects_unauthenticated(self):
        """Test that task list redirects unauthenticated users"""
        response = self.client.get(reverse('core:task_list'))
        self.assertRedirects(response, '/accounts/login/?next=%2Ftasks%2F')
    
    def test_task_list_authenticated_user(self):
        """Test task list for authenticated user"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('core:task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'All Tasks')
        self.assertContains(response, self.task.title)
    
    def test_task_create_permission_manager(self):
        """Test that managers can create tasks"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('core:task_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create New Task')
    
    def test_task_create_permission_developer(self):
        """Test that developers cannot create tasks"""
        self.client.login(email='test2@example.com', password='testpass123')
        response = self.client.get(reverse('core:task_create'))
        self.assertRedirects(response, reverse('core:task_list'))
    
    def test_task_create_post(self):
        """Test task creation via POST"""
        self.client.login(email='test@example.com', password='testpass123')
        
        task_data = {
            'title': 'New Test Task',
            'description': 'New test description',
            'status': 'pending',
            'priority': 'medium',
            'assigned_to': self.user2.id
        }
        
        response = self.client.post(reverse('core:task_create'), task_data)
        self.assertRedirects(response, reverse('core:task_detail', args=[2]))
        
        # Verify task was created
        new_task = Task.objects.get(id=2)
        self.assertEqual(new_task.title, 'New Test Task')
        self.assertEqual(new_task.created_by, self.user)
    
    def test_task_detail_view(self):
        """Test task detail view"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('core:task_detail', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.task.title)
        self.assertContains(response, self.task.description)
    
    def test_task_detail_permission(self):
        """Test that users can only view their own tasks or assigned tasks"""
        # Create a third user
        user3 = User.objects.create_user(
            username='testuser3',
            email='test3@example.com',
            password='testpass123'
        )
        user3.profile.role = 'developer'
        user3.profile.save()
        
        # Create a task by user3
        task3 = Task.objects.create(
            title='Private Task',
            created_by=user3
        )
        
        # user2 should not be able to view task3
        self.client.login(email='test2@example.com', password='testpass123')
        response = self.client.get(reverse('core:task_detail', args=[task3.id]))
        self.assertRedirects(response, reverse('core:task_list'))
    
    def test_task_edit_permission(self):
        """Test task edit permissions"""
        # Manager can edit
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('core:task_edit', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)
        
        # Developer can edit (assigned user)
        self.client.login(email='test2@example.com', password='testpass123')
        response = self.client.get(reverse('core:task_edit', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)
    
    def test_task_complete(self):
        """Test task completion"""
        self.client.login(email='test2@example.com', password='testpass123')
        response = self.client.get(reverse('core:task_complete', args=[self.task.id]))
        self.assertRedirects(response, reverse('core:task_detail', args=[self.task.id]))
        
        # Verify task was marked as completed
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'completed')
        self.assertIsNotNone(self.task.completed_at)
    
    def test_task_delete_permission(self):
        """Test task delete permissions"""
        # Manager can delete
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('core:task_delete', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)
        
        # Developer cannot delete
        self.client.login(email='test2@example.com', password='testpass123')
        response = self.client.get(reverse('core:task_delete', args=[self.task.id]))
        self.assertRedirects(response, reverse('core:task_detail', args=[self.task.id]))
    
    def test_task_delete_post(self):
        """Test task deletion via POST"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.post(reverse('core:task_delete', args=[self.task.id]))
        self.assertRedirects(response, reverse('core:task_list'))
        
        # Verify task was deleted
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())
    
    def test_my_tasks_view(self):
        """Test my tasks view"""
        self.client.login(email='test2@example.com', password='testpass123')
        response = self.client.get(reverse('core:my_tasks'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Tasks')
        self.assertContains(response, self.task.title)
    
    def test_task_list_filtering(self):
        """Test task list filtering"""
        self.client.login(email='test@example.com', password='testpass123')
        
        # Test status filter
        response = self.client.get(reverse('core:task_list'), {'status': 'pending'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.task.title)
        
        # Test priority filter
        response = self.client.get(reverse('core:task_list'), {'priority': 'high'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.task.title)
        
        # Test search
        response = self.client.get(reverse('core:task_list'), {'search': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.task.title)


class AuthenticationViewsTest(TestCase):
    """Test cases for authentication views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user.profile.role = 'developer'
        self.user.profile.save()
    
    def test_login_view(self):
        """Test login view"""
        response = self.client.get(reverse('account_login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome Back')
    
    def test_signup_view(self):
        """Test signup view"""
        response = self.client.get(reverse('account_signup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Account')
    
    def test_login_post(self):
        """Test login via POST"""
        response = self.client.post(reverse('account_login'), {
            'login': 'test@example.com',
            'password': 'testpass123'
        })
        self.assertRedirects(response, '/')
    
    def test_signup_post(self):
        """Test signup via POST"""
        response = self.client.post(reverse('account_signup'), {
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'developer'
        })
        # Should redirect to login or dashboard
        self.assertIn(response.status_code, [200, 302])
        
        # Verify user was created
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())
    
    def test_logout(self):
        """Test logout"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('account_logout'))
        self.assertRedirects(response, reverse('account_login'))
