from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from core.models import Task
from core.profile import UserProfile


class TaskModelTest(TestCase):
    """Test cases for Task model"""
    
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
    
    def test_task_creation(self):
        """Test basic task creation"""
        task = Task.objects.create(
            title='Test Task',
            description='This is a test task',
            created_by=self.user,
            assigned_to=self.user2,
            status='pending',
            priority='high'
        )
        
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.description, 'This is a test task')
        self.assertEqual(task.created_by, self.user)
        self.assertEqual(task.assigned_to, self.user2)
        self.assertEqual(task.status, 'pending')
        self.assertEqual(task.priority, 'high')
        self.assertIsNotNone(task.created_at)
        self.assertIsNotNone(task.updated_at)
    
    def test_task_str_representation(self):
        """Test string representation of task"""
        task = Task.objects.create(
            title='Test Task',
            created_by=self.user
        )
        self.assertEqual(str(task), 'Test Task')
    
    def test_task_is_overdue_property(self):
        """Test is_overdue property"""
        # Create overdue task
        past_date = timezone.now() - timedelta(days=1)
        overdue_task = Task.objects.create(
            title='Overdue Task',
            created_by=self.user,
            due_date=past_date,
            status='pending'
        )
        self.assertTrue(overdue_task.is_overdue)
        
        # Create future task
        future_date = timezone.now() + timedelta(days=1)
        future_task = Task.objects.create(
            title='Future Task',
            created_by=self.user,
            due_date=future_date,
            status='pending'
        )
        self.assertFalse(future_task.is_overdue)
        
        # Completed task should not be overdue
        completed_task = Task.objects.create(
            title='Completed Task',
            created_by=self.user,
            due_date=past_date,
            status='completed'
        )
        self.assertFalse(completed_task.is_overdue)
    
    def test_task_priority_colors(self):
        """Test priority color properties"""
        task_low = Task.objects.create(
            title='Low Priority',
            created_by=self.user,
            priority='low'
        )
        self.assertEqual(task_low.priority_color, '#28a745')
        
        task_urgent = Task.objects.create(
            title='Urgent Task',
            created_by=self.user,
            priority='urgent'
        )
        self.assertEqual(task_urgent.priority_color, '#dc3545')
    
    def test_task_status_colors(self):
        """Test status color properties"""
        task_pending = Task.objects.create(
            title='Pending Task',
            created_by=self.user,
            status='pending'
        )
        self.assertEqual(task_pending.status_color, '#6c757d')
        
        task_completed = Task.objects.create(
            title='Completed Task',
            created_by=self.user,
            status='completed'
        )
        self.assertEqual(task_completed.status_color, '#28a745')
    
    def test_task_tags_list(self):
        """Test tags list property"""
        task = Task.objects.create(
            title='Tagged Task',
            created_by=self.user,
            tags='urgent, frontend, bug'
        )
        tags_list = task.get_tags_list()
        self.assertEqual(len(tags_list), 3)
        self.assertIn('urgent', tags_list)
        self.assertIn('frontend', tags_list)
        self.assertIn('bug', tags_list)
        
        # Test empty tags
        task_no_tags = Task.objects.create(
            title='No Tags Task',
            created_by=self.user
        )
        self.assertEqual(task_no_tags.get_tags_list(), [])
    
    def test_task_ordering(self):
        """Test task ordering by created_at"""
        task1 = Task.objects.create(
            title='First Task',
            created_by=self.user
        )
        task2 = Task.objects.create(
            title='Second Task',
            created_by=self.user
        )
        
        tasks = Task.objects.all()
        self.assertEqual(tasks[0], task2)  # Most recent first
        self.assertEqual(tasks[1], task1)


class UserProfileModelTest(TestCase):
    """Test cases for UserProfile model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_profile_creation(self):
        """Test profile creation"""
        # Profile is created automatically by signal
        profile = self.user.profile
        profile.role = 'developer'
        profile.department = 'Engineering'
        profile.phone = '+1234567890'
        profile.bio = 'Test bio'
        profile.save()
        
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.role, 'developer')
        self.assertEqual(profile.department, 'Engineering')
        self.assertEqual(profile.phone, '+1234567890')
        self.assertEqual(profile.bio, 'Test bio')
        self.assertTrue(profile.is_active_member)
        self.assertEqual(profile.weekly_hours_available, 40)
    
    def test_profile_str_representation(self):
        """Test string representation of profile"""
        profile = self.user.profile
        profile.role = 'manager'
        profile.save()
        expected = f"{self.user.get_full_name() or self.user.username} - Project Manager"
        self.assertEqual(str(profile), expected)
    
    def test_profile_full_name_property(self):
        """Test full_name property"""
        profile = self.user.profile
        profile.role = 'developer'
        profile.save()
        self.assertEqual(profile.full_name, 'Test User')
    
    def test_profile_availability_percentage(self):
        """Test availability percentage calculation"""
        profile = self.user.profile
        profile.role = 'developer'
        profile.weekly_hours_available = 40
        profile.current_hours_allocated = 20
        profile.save()
        self.assertEqual(profile.availability_percentage, 50.0)
        
        # Test overloaded user
        profile.current_hours_allocated = 50
        profile.save()
        self.assertEqual(profile.availability_percentage, 100.0)
    
    def test_profile_role_colors(self):
        """Test role color properties"""
        admin_profile = self.user.profile
        admin_profile.role = 'admin'
        admin_profile.save()
        self.assertEqual(admin_profile.get_role_color(), '#dc3545')
        
        # Create another user for developer test
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        developer_profile = user2.profile
        developer_profile.role = 'developer'
        developer_profile.save()
        self.assertEqual(developer_profile.get_role_color(), '#198754')
    
    def test_profile_permissions(self):
        """Test permission methods"""
        # Admin permissions
        admin_profile = self.user.profile
        admin_profile.role = 'admin'
        admin_profile.save()
        self.assertTrue(admin_profile.can_manage_tasks())
        self.assertTrue(admin_profile.can_assign_tasks())
        self.assertTrue(admin_profile.can_view_all_tasks())
        
        # Manager permissions
        admin_profile.role = 'manager'
        admin_profile.save()
        self.assertTrue(admin_profile.can_manage_tasks())
        self.assertTrue(admin_profile.can_assign_tasks())
        self.assertTrue(admin_profile.can_view_all_tasks())
        
        # Developer permissions
        admin_profile.role = 'developer'
        admin_profile.save()
        self.assertFalse(admin_profile.can_manage_tasks())
        self.assertFalse(admin_profile.can_assign_tasks())
        self.assertFalse(admin_profile.can_view_all_tasks())
    
    def test_profile_auto_creation_signal(self):
        """Test automatic profile creation signal"""
        new_user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='testpass123'
        )
        
        # Profile should be created automatically
        self.assertTrue(hasattr(new_user, 'profile'))
        self.assertEqual(new_user.profile.role, 'developer')  # Default role
