from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

ROLE_CHOICES = [
    ('admin', 'Administrator'),
    ('manager', 'Project Manager'),
    ('developer', 'Developer'),
    ('tester', 'Tester'),
    ('designer', 'Designer'),
    ('intern', 'Intern'),
    ('consultant', 'Consultant'),
]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='developer')
    bio = models.TextField(blank=True, null=True, max_length=500)
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    join_date = models.DateField(auto_now_add=True)
    is_active_member = models.BooleanField(default=True)
    
    # Hour tracking
    weekly_hours_available = models.PositiveIntegerField(default=40)
    current_hours_allocated = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.get_role_display()}"
    
    @property
    def availability_percentage(self):
        """Calculate how busy the user is based on allocated hours"""
        if self.weekly_hours_available <= 0:
            return 0
        return min(100, (self.current_hours_allocated / self.weekly_hours_available) * 100)
    
    @property
    def full_name(self):
        """Get user's full name"""
        return self.user.get_full_name() or self.user.username
    
    def can_manage_tasks(self):
        """Check if user can manage (create/edit/delete) tasks"""
        return self.role in ['admin', 'manager']
    
    def can_assign_tasks(self):
        """Check if user can assign tasks to others"""
        return self.role in ['admin', 'manager']
    
    def can_view_all_tasks(self):
        """Check if user can view all tasks regardless of assignment"""
        return self.role in ['admin', 'manager']
    
    def get_role_color(self):
        """Get color associated with user role"""
        colors = {
            'admin': '#dc3545',      # Red
            'manager': '#0d6efd',    # Blue
            'developer': '#198754',  # Green
            'tester': '#fd7e14',     # Orange
            'designer': '#6f42c1',  # Purple
            'intern': '#6c757d',     # Gray
            'consultant': '#16c1ae', # Teal
        }
        return colors.get(self.role, '#6c757d')

# Signal to create user profile automatically
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        UserProfile.objects.create(user=instance)
