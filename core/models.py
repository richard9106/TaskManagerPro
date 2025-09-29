from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .profile import UserProfile

class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Task Title")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Status")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name="Priority")
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Updated")
    due_date = models.DateTimeField(blank=True, null=True, verbose_name="Due Date")
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name="Completed At")
    
    # Assignments
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks', verbose_name="Created By")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks', verbose_name="Assigned To")
    
    # Additional fields
    tags = models.CharField(max_length=200, blank=True, verbose_name="Tags (comma-separated)")
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="Estimated Hours")
    actual_hours = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="Actual Hours")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
    
    def __str__(self):
        return self.title
    
    @property
    def is_overdue(self):
        if self.due_date and self.status != 'completed':
            return timezone.now() > self.due_date
        return False
    
    @property
    def priority_color(self):
        colors = {
            'low': '#28a745',
            'medium': '#ffc107',
            'high': '#ff9800',
            'urgent': '#dc3545',
        }
        return colors.get(self.priority, '#6c757d')
    
    @property
    def status_color(self):
        colors = {
            'pending': '#6c757d',
            'in_progress': '#007bff',
            'completed': '#28a745',
            'cancelled': '#dc3545',
        }
        return colors.get(self.status, '#6c757d')
    
    def get_tags_list(self):
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
