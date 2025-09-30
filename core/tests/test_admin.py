from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from core.models import Task
from core.profile import UserProfile


class AdminTest(TestCase):
    """Test cases for admin interface"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create superuser
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        # Get profile (created automatically by signal)
        self.superuser_profile = self.superuser.profile
        self.superuser_profile.role = 'admin'
        self.superuser_profile.save()
        
        # Create regular user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        # Get profile (created automatically by signal)
        self.user_profile = self.user.profile
        self.user_profile.role = 'developer'
        self.user_profile.save()
        
        # Create test task
        self.task = Task.objects.create(
            title='Test Task',
            description='Test description',
            created_by=self.user,
            assigned_to=self.user,
            status='pending',
            priority='high'
        )
    
    def test_admin_login(self):
        """Test admin login"""
        response = self.client.post(reverse('admin:login'), {
            'username': 'admin@example.com',
            'password': 'adminpass123'
        })
        self.assertRedirects(response, '/')
    
    def test_admin_dashboard(self):
        """Test admin dashboard access"""
        self.client.login(username='admin@example.com', password='adminpass123')
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Task Manager Pro Administration')
    
    def test_task_admin_list(self):
        """Test task admin list view"""
        self.client.login(username='admin@example.com', password='adminpass123')
        response = self.client.get(reverse('admin:core_task_changelist'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.task.title)
    
    def test_task_admin_detail(self):
        """Test task admin detail view"""
        self.client.login(username='admin@example.com', password='adminpass123')
        response = self.client.get(reverse('admin:core_task_change', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.task.title)
    
    def test_task_admin_create(self):
        """Test task admin create view"""
        self.client.login(username='admin@example.com', password='adminpass123')
        response = self.client.get(reverse('admin:core_task_add'))
        self.assertEqual(response.status_code, 200)
    
    def test_task_admin_edit(self):
        """Test task admin edit functionality"""
        self.client.login(username='admin@example.com', password='adminpass123')
        
        # Edit task
        response = self.client.post(reverse('admin:core_task_change', args=[self.task.id]), {
            'title': 'Updated Task',
            'description': 'Updated description',
            'status': 'in_progress',
            'priority': 'medium',
            'created_by': self.user.id,
            'assigned_to': self.user.id,
            'created_at_0': self.task.created_at.strftime('%Y-%m-%d'),
            'created_at_1': self.task.created_at.strftime('%H:%M:%S'),
            'updated_at_0': self.task.updated_at.strftime('%Y-%m-%d'),
            'updated_at_1': self.task.updated_at.strftime('%H:%M:%S'),
        })
        self.assertRedirects(response, reverse('admin:core_task_changelist'))
        
        # Verify task was updated
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Updated Task')
        self.assertEqual(self.task.status, 'in_progress')
    
    def test_userprofile_admin_list(self):
        """Test user profile admin list view"""
        self.client.login(username='admin@example.com', password='adminpass123')
        response = self.client.get(reverse('admin:core_userprofile_changelist'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test User')
    
    def test_userprofile_admin_detail(self):
        """Test user profile admin detail view"""
        self.client.login(username='admin@example.com', password='adminpass123')
        response = self.client.get(reverse('admin:core_userprofile_change', args=[self.user.profile.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test User')
    
    def test_userprofile_admin_create(self):
        """Test user profile admin create view"""
        self.client.login(username='admin@example.com', password='adminpass123')
        response = self.client.get(reverse('admin:core_userprofile_add'))
        self.assertEqual(response.status_code, 200)
    
    def test_admin_filters(self):
        """Test admin filters"""
        self.client.login(username='admin@example.com', password='adminpass123')
        
        # Test task status filter
        response = self.client.get(reverse('admin:core_task_changelist'), {'status': 'pending'})
        self.assertEqual(response.status_code, 200)
        
        # Test task priority filter
        response = self.client.get(reverse('admin:core_task_changelist'), {'priority': 'high'})
        self.assertEqual(response.status_code, 200)
        
        # Test user profile role filter
        response = self.client.get(reverse('admin:core_userprofile_changelist'), {'role': 'developer'})
        self.assertEqual(response.status_code, 200)
    
    def test_admin_search(self):
        """Test admin search functionality"""
        self.client.login(username='admin@example.com', password='adminpass123')
        
        # Test task search
        response = self.client.get(reverse('admin:core_task_changelist'), {'q': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.task.title)
        
        # Test user profile search
        response = self.client.get(reverse('admin:core_userprofile_changelist'), {'q': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test User')
    
    def test_admin_list_editable(self):
        """Test admin list editable functionality"""
        self.client.login(username='admin@example.com', password='adminpass123')
        
        # Test task list editable
        response = self.client.post(reverse('admin:core_task_changelist'), {
            'action': '',
            'selected_across': '0',
            'select': [self.task.id],
            'form-0-status': 'completed',
            'form-0-priority': 'low',
            'form-0-assigned_to': self.user.id,
            'form-0-id': self.task.id,
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '1',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            '_save': 'Save',
        })
        # The response should redirect back to the changelist
        self.assertRedirects(response, reverse('admin:core_task_changelist'))
        
        # Verify task was updated
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'completed')
        self.assertEqual(self.task.priority, 'low')
    
    def test_admin_badges(self):
        """Test admin badge display"""
        self.client.login(username='admin@example.com', password='adminpass123')
        response = self.client.get(reverse('admin:core_task_changelist'))
        self.assertEqual(response.status_code, 200)
        
        # Check that badges are rendered
        self.assertContains(response, 'field-status_badge')
        self.assertContains(response, 'field-priority_badge')
    
    def test_admin_overdue_indicator(self):
        """Test admin overdue indicator"""
        # Create overdue task
        past_date = timezone.now() - timedelta(days=1)
        overdue_task = Task.objects.create(
            title='Overdue Task',
            created_by=self.user,
            due_date=past_date,
            status='pending'
        )
        
        self.client.login(username='admin@example.com', password='adminpass123')
        response = self.client.get(reverse('admin:core_task_changelist'))
        self.assertEqual(response.status_code, 200)
        
        # Check that overdue indicator is shown
        self.assertContains(response, 'Overdue')
    
    def test_admin_completion_auto_update(self):
        """Test admin auto-update of completion date"""
        self.client.login(username='admin@example.com', password='adminpass123')
        
        # Change task status to completed
        response = self.client.post(reverse('admin:core_task_change', args=[self.task.id]), {
            'title': self.task.title,
            'description': self.task.description,
            'status': 'completed',
            'priority': self.task.priority,
            'created_by': self.user.id,
            'assigned_to': self.user.id,
            'created_at_0': self.task.created_at.strftime('%Y-%m-%d'),
            'created_at_1': self.task.created_at.strftime('%H:%M:%S'),
            'updated_at_0': self.task.updated_at.strftime('%Y-%m-%d'),
            'updated_at_1': self.task.updated_at.strftime('%H:%M:%S'),
        })
        self.assertRedirects(response, reverse('admin:core_task_changelist'))
        
        # Verify completion date was set
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'completed')
        self.assertIsNotNone(self.task.completed_at)
    
    def test_admin_permissions(self):
        """Test admin permissions"""
        # Test that regular user cannot access admin
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('admin:index'))
        expected_url = f"{reverse('admin:login')}?next={reverse('admin:index')}"
        self.assertRedirects(response, expected_url)
        
        # Test that superuser can access admin
        self.client.login(username='admin@example.com', password='adminpass123')
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)
