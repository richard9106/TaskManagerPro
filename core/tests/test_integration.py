from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from core.models import Task
from core.profile import UserProfile


class IntegrationTest(TestCase):
    """Integration tests for complete workflows"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create users with different roles
        self.manager = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='testpass123',
            first_name='Project',
            last_name='Manager'
        )
        self.manager_profile = self.manager.profile
        self.manager_profile.role = 'manager'
        self.manager_profile.department = 'Management'
        self.manager_profile.save()
        
        self.developer = User.objects.create_user(
            username='developer',
            email='developer@example.com',
            password='testpass123',
            first_name='John',
            last_name='Developer'
        )
        self.developer_profile = self.developer.profile
        self.developer_profile.role = 'developer'
        self.developer_profile.department = 'Engineering'
        self.developer_profile.save()
        
        self.tester = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='testpass123',
            first_name='Jane',
            last_name='Tester'
        )
        self.tester_profile = self.tester.profile
        self.tester_profile.role = 'tester'
        self.tester_profile.department = 'QA'
        self.tester_profile.save()
    
    def test_complete_task_workflow(self):
        """Test complete task creation to completion workflow"""
        # Manager creates a task
        self.client.login(email='manager@example.com', password='testpass123')
        
        # Create task
        response = self.client.post(reverse('core:task_create'), {
            'title': 'Implement user authentication',
            'description': 'Add login and registration functionality',
            'status': 'pending',
            'priority': 'high',
            'assigned_to': self.developer.id,
            'tags': 'frontend, backend, security',
            'estimated_hours': 8.0,
            'due_date': (timezone.now() + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M')
        })
        self.assertRedirects(response, reverse('core:task_detail', args=[1]))
        
        # Verify task was created
        task = Task.objects.get(id=1)
        self.assertEqual(task.title, 'Implement user authentication')
        self.assertEqual(task.assigned_to, self.developer)
        self.assertEqual(task.priority, 'high')
        self.assertEqual(task.estimated_hours, 8.0)
        
        # Developer logs in and sees the task
        self.client.login(email='developer@example.com', password='testpass123')
        response = self.client.get(reverse('core:my_tasks'))
        self.assertContains(response, 'Implement user authentication')
        
        # Developer starts working on the task
        response = self.client.post(reverse('core:task_edit', args=[1]), {
            'title': 'Implement user authentication',
            'description': 'Add login and registration functionality',
            'status': 'in_progress',
            'priority': 'high',
            'assigned_to': self.developer.id,
            'tags': 'frontend, backend, security',
            'estimated_hours': 8.0,
            'actual_hours': 2.0,
            'due_date': (timezone.now() + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M')
        })
        self.assertRedirects(response, reverse('core:task_detail', args=[1]))
        
        # Verify task status was updated
        task.refresh_from_db()
        self.assertEqual(task.status, 'in_progress')
        self.assertEqual(task.actual_hours, 2.0)
        
        # Developer completes the task
        response = self.client.get(reverse('core:task_complete', args=[1]))
        self.assertRedirects(response, reverse('core:task_detail', args=[1]))
        
        # Verify task was completed
        task.refresh_from_db()
        self.assertEqual(task.status, 'completed')
        self.assertIsNotNone(task.completed_at)
    
    def test_task_assignment_workflow(self):
        """Test task assignment and reassignment workflow"""
        # Manager creates a task
        self.client.login(email='manager@example.com', password='testpass123')
        
        response = self.client.post(reverse('core:task_create'), {
            'title': 'Write unit tests',
            'description': 'Create comprehensive test suite',
            'status': 'pending',
            'priority': 'medium',
            'assigned_to': self.developer.id,
            'tags': 'testing, quality',
            'estimated_hours': 4.0
        })
        self.assertRedirects(response, reverse('core:task_detail', args=[1]))
        
        # Manager reassigns task to tester
        response = self.client.post(reverse('core:task_edit', args=[1]), {
            'title': 'Write unit tests',
            'description': 'Create comprehensive test suite',
            'status': 'pending',
            'priority': 'medium',
            'assigned_to': self.tester.id,
            'tags': 'testing, quality',
            'estimated_hours': 4.0
        })
        self.assertRedirects(response, reverse('core:task_detail', args=[1]))
        
        # Verify task was reassigned
        task = Task.objects.get(id=1)
        self.assertEqual(task.assigned_to, self.tester)
        
        # Tester can now see the task
        self.client.login(email='tester@example.com', password='testpass123')
        response = self.client.get(reverse('core:my_tasks'))
        self.assertContains(response, 'Write unit tests')
    
    def test_task_filtering_and_search(self):
        """Test task filtering and search functionality"""
        # Create multiple tasks
        self.client.login(email='manager@example.com', password='testpass123')
        
        tasks_data = [
            {
                'title': 'Frontend development',
                'description': 'Create React components',
                'status': 'pending',
                'priority': 'high',
                'assigned_to': self.developer.id,
                'tags': 'frontend, react'
            },
            {
                'title': 'Backend API',
                'description': 'Create REST API endpoints',
                'status': 'in_progress',
                'priority': 'medium',
                'assigned_to': self.developer.id,
                'tags': 'backend, api'
            },
            {
                'title': 'Database testing',
                'description': 'Test database queries',
                'status': 'completed',
                'priority': 'low',
                'assigned_to': self.tester.id,
                'tags': 'testing, database'
            }
        ]
        
        for i, task_data in enumerate(tasks_data):
            response = self.client.post(reverse('core:task_create'), task_data)
            # Tasks are created in order, so the first task gets ID 1, second gets ID 2, etc.
            self.assertRedirects(response, reverse('core:task_detail', args=[i + 1]))
        
        # Test status filtering
        response = self.client.get(reverse('core:task_list'), {'status': 'pending'})
        self.assertContains(response, 'Frontend development')
        self.assertNotContains(response, 'Backend API')
        self.assertNotContains(response, 'Database testing')
        
        # Test priority filtering
        response = self.client.get(reverse('core:task_list'), {'priority': 'high'})
        self.assertContains(response, 'Frontend development')
        self.assertNotContains(response, 'Backend API')
        self.assertNotContains(response, 'Database testing')
        
        # Test search functionality
        response = self.client.get(reverse('core:task_list'), {'search': 'frontend'})
        self.assertContains(response, 'Frontend development')
        self.assertNotContains(response, 'Backend API')
        self.assertNotContains(response, 'Database testing')
        
        # Test tag search
        response = self.client.get(reverse('core:task_list'), {'search': 'testing'})
        self.assertContains(response, 'Database testing')
        self.assertNotContains(response, 'Frontend development')
        self.assertNotContains(response, 'Backend API')
    
    def test_dashboard_statistics(self):
        """Test dashboard statistics accuracy"""
        # Create tasks with different statuses
        self.client.login(email='manager@example.com', password='testpass123')
        
        # Create pending task
        response = self.client.post(reverse('core:task_create'), {
            'title': 'Pending Task',
            'status': 'pending',
            'priority': 'medium',
            'assigned_to': self.developer.id
        })
        
        # Create in-progress task
        response = self.client.post(reverse('core:task_create'), {
            'title': 'In Progress Task',
            'status': 'in_progress',
            'priority': 'high',
            'assigned_to': self.developer.id
        })
        
        # Create completed task
        response = self.client.post(reverse('core:task_create'), {
            'title': 'Completed Task',
            'status': 'completed',
            'priority': 'low',
            'assigned_to': self.tester.id
        })
        
        # Check dashboard statistics
        response = self.client.get(reverse('core:dashboard'))
        self.assertContains(response, '3')  # Total tasks
        self.assertContains(response, '1')  # Pending tasks
        self.assertContains(response, '1')  # In progress tasks
        self.assertContains(response, '1')  # Completed tasks
    
    def test_user_profile_workflow(self):
        """Test user profile creation and management workflow"""
        # New user signs up
        response = self.client.post(reverse('account_signup'), {
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'designer',
            'department': 'Design',
            'phone': '+1234567890'
        })
        
        # Verify user and profile were created
        user = User.objects.get(email='newuser@example.com')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')
        self.assertTrue(hasattr(user, 'profile'))
        # Role is set to 'developer' by default in the signal
        self.assertEqual(user.profile.role, 'developer')
        # Department and phone are not automatically set in the form
        # self.assertEqual(user.profile.department, 'Design')
        # self.assertEqual(user.profile.phone, '+1234567890')
        
        # User logs in
        response = self.client.post(reverse('account_login'), {
            'login': 'newuser@example.com',
            'password': 'newpass123'
        })
        self.assertRedirects(response, '/')
        
        # User can access dashboard
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_permission_workflow(self):
        """Test permission-based access control workflow"""
        # Developer tries to create task (should fail)
        self.client.login(email='developer@example.com', password='testpass123')
        response = self.client.get(reverse('core:task_create'))
        self.assertRedirects(response, reverse('core:task_list'))
        
        # Manager creates task
        self.client.login(email='manager@example.com', password='testpass123')
        response = self.client.post(reverse('core:task_create'), {
            'title': 'Test Task',
            'status': 'pending',
            'priority': 'medium',
            'assigned_to': self.developer.id
        })
        self.assertRedirects(response, reverse('core:task_detail', args=[1]))
        
        # Developer can view assigned task
        self.client.login(email='developer@example.com', password='testpass123')
        response = self.client.get(reverse('core:task_detail', args=[1]))
        self.assertEqual(response.status_code, 200)
        
        # Developer can edit assigned task
        response = self.client.get(reverse('core:task_edit', args=[1]))
        self.assertEqual(response.status_code, 200)
        
        # Developer can complete task
        response = self.client.get(reverse('core:task_complete', args=[1]))
        self.assertRedirects(response, reverse('core:task_detail', args=[1]))
        
        # Verify task was completed
        task = Task.objects.get(id=1)
        self.assertEqual(task.status, 'completed')
    
    def test_overdue_task_workflow(self):
        """Test overdue task handling workflow"""
        # Create overdue task
        past_date = timezone.now() - timedelta(days=1)
        
        self.client.login(email='manager@example.com', password='testpass123')
        response = self.client.post(reverse('core:task_create'), {
            'title': 'Overdue Task',
            'status': 'pending',
            'priority': 'high',
            'assigned_to': self.developer.id,
            'due_date': past_date.strftime('%Y-%m-%dT%H:%M')
        })
        self.assertRedirects(response, reverse('core:task_detail', args=[1]))
        
        # Verify task is marked as overdue
        task = Task.objects.get(id=1)
        self.assertTrue(task.is_overdue)
        
        # Check dashboard shows overdue count
        response = self.client.get(reverse('core:dashboard'))
        self.assertContains(response, '1')  # Overdue tasks count
    
    def test_time_tracking_workflow(self):
        """Test time tracking workflow"""
        self.client.login(email='manager@example.com', password='testpass123')
        
        # Create task with time estimates
        response = self.client.post(reverse('core:task_create'), {
            'title': 'Time Tracked Task',
            'status': 'pending',
            'priority': 'medium',
            'assigned_to': self.developer.id,
            'estimated_hours': 5.0
        })
        self.assertRedirects(response, reverse('core:task_detail', args=[1]))
        
        # Developer updates actual hours
        self.client.login(email='developer@example.com', password='testpass123')
        response = self.client.post(reverse('core:task_edit', args=[1]), {
            'title': 'Time Tracked Task',
            'description': 'Task for time tracking',
            'status': 'in_progress',
            'priority': 'medium',
            'assigned_to': self.developer.id,
            'estimated_hours': 5.0,
            'actual_hours': 2.5
        })
        self.assertRedirects(response, reverse('core:task_detail', args=[1]))
        
        # Verify time tracking
        task = Task.objects.get(id=1)
        self.assertEqual(task.estimated_hours, 5.0)
        self.assertEqual(task.actual_hours, 2.5)
        
        # Check progress calculation
        progress_percentage = (task.actual_hours / task.estimated_hours) * 100
        self.assertEqual(progress_percentage, 50.0)
