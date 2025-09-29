from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.utils.timezone import now
from .models import Task
from .profile import UserProfile

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'status', 'priority', 'status_badge', 'priority_badge', 'created_by', 
        'assigned_to', 'due_date_formatted', 'is_overdue_indicator'
    ]
    list_filter = ['status', 'priority', 'created_at', 'due_date', 'assigned_to']
    search_fields = ['title', 'description', 'tags']
    list_editable = ['status', 'priority', 'assigned_to']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'status', 'priority')
        }),
        ('Assignment', {
            'fields': ('created_by', 'assigned_to')
        }),
        ('Dates', {
            'fields': ('due_date', 'created_at', 'updated_at', 'completed_at')
        }),
        ('Additional Information', {
            'fields': ('tags', 'estimated_hours', 'actual_hours'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'pending': '#6c757d',
            'in_progress': '#007bff',
            'completed': '#28a745',
            'cancelled': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; text-transform: uppercase;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def priority_badge(self, obj):
        colors = {
            'low': '#28a745',
            'medium': '#ffc107',
            'high': '#ff9800',
            'urgent': '#dc3545',
        }
        color = colors.get(obj.priority, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; text-transform: uppercase;">{}</span>',
            color, obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'
    
    def due_date_formatted(self, obj):
        if obj.due_date:
            if obj.is_overdue:
                return format_html(
                    '<span style="color: #dc3545; font-weight: bold;">{}</span>',
                    obj.due_date.strftime('%m/%d/%Y %H:%M')
                )
            else:
                return obj.due_date.strftime('%m/%d/%Y %H:%M')
        return '-'
    due_date_formatted.short_description = 'Due Date'
    
    def is_overdue_indicator(self, obj):
        if obj.is_overdue:
            return format_html('<i class="fas fa-exclamation-triangle" style="color: #dc3545;"></i> Overdue')
        return ''
    is_overdue_indicator.short_description = 'Alert'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by', 'assigned_to')
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new task
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
        
        # Update completed_at if status changed to completed
        if obj.status == 'completed' and not obj.completed_at:
            obj.completed_at = now()
            obj.save(update_fields=['completed_at'])

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'role_badge', 'department', 'phone', 'is_active_member',
        'weekly_hours_available', 'availability_indicator'
    ]
    list_filter = ['role', 'department', 'is_active_member', 'join_date']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'department']
    list_editable = ['is_active_member', 'weekly_hours_available']
    readonly_fields = ['join_date']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'role', 'department')
        }),
        ('Contact Information', {
            'fields': ('phone', 'bio')
        }),
        ('Work Settings', {
            'fields': ('weekly_hours_available', 'current_hours_allocated', 'is_active_member')
        }),
        ('Profile', {
            'fields': ('avatar', 'join_date')
        }),
    )
    
    def role_badge(self, obj):
        color = obj.get_role_color()
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; text-transform: uppercase;">{}</span>',
            color, obj.get_role_display()
        )
    role_badge.short_description = 'Role'
    
    def availability_indicator(self, obj):
        percentage = obj.availability_percentage
        if percentage >= 100:
            return format_html('<span class="badge bg-danger">Overloaded</span>')
        elif percentage >= 80:
            return format_html('<span class="badge bg-warning">Busy</span>')
        elif percentage >= 50:
            return format_html('<span class="badge bg-info">Available</span>')
        else:
            return format_html('<span class="badge bg-success">Free</span>')
    availability_indicator.short_description = 'Availability'
