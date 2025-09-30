from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
from functools import wraps
from .models import Task
from .forms import TaskForm

def ensure_profile(view_func):
    """Decorator to ensure user has a profile"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            if not hasattr(request.user, 'profile'):
                from .profile import UserProfile
                UserProfile.objects.create(user=request.user, role='developer')
        return view_func(request, *args, **kwargs)
    return wrapper

def dashboard(request):
    """Main dashboard with task statistics and overview"""
    if not request.user.is_authenticated:
        # Redirect to login instead of showing demo
        return redirect('account_login')
    
    # Ensure user has profile
    if not hasattr(request.user, 'profile'):
        from .profile import UserProfile
        UserProfile.objects.create(user=request.user, role='developer')
    
    # User-specific dashboard
    user_tasks = Task.objects.filter(
        Q(created_by=request.user) | Q(assigned_to=request.user)
    ).distinct()
    
    stats = {
        'total_tasks': user_tasks.count(),
        'pending_tasks': user_tasks.filter(status='pending').count(),
        'in_progress_tasks': user_tasks.filter(status='in_progress').count(),
        'completed_tasks': user_tasks.filter(status='completed').count(),
        'overdue_tasks': user_tasks.filter(
            due_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        ).count(),
    }
    
    recent_tasks = user_tasks.order_by('-created_at')[:5]
    high_priority_tasks = user_tasks.filter(priority='urgent').order_by('-created_at')[:3]
    
    context = {
        'title': 'Dashboard',
        'description': 'Your task management overview',
        'is_demo': False,
        **stats,
        'recent_tasks': recent_tasks,
        'high_priority_tasks': high_priority_tasks,
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def task_list(request):
    """List all tasks with filtering and search"""
    # Base queryset - admins and managers can see all tasks
    if request.user.profile.can_view_all_tasks():
        tasks = Task.objects.all().order_by('-created_at')
    else:
        tasks = Task.objects.filter(
            Q(created_by=request.user) | Q(assigned_to=request.user)
        ).distinct().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        tasks = tasks.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    # Filter by priority
    priority_filter = request.GET.get('priority', '')
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    
    # Filter by assignment
    assignment_filter = request.GET.get('assignment', '')
    if assignment_filter == 'assigned_to_me':
        tasks = tasks.filter(assigned_to=request.user)
    elif assignment_filter == 'created_by_me':
        tasks = tasks.filter(created_by=request.user)
    
    # Pagination
    paginator = Paginator(tasks, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'All Tasks',
        'description': 'Manage your tasks efficiently',
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'assignment_filter': assignment_filter,
        'status_choices': Task.STATUS_CHOICES,
        'priority_choices': Task.PRIORITY_CHOICES,
    }
    return render(request, 'core/task_list.html', context)

@login_required
def task_detail(request, task_id):
    """Show detailed view of a single task"""
    task = get_object_or_404(Task, id=task_id)
    
    # Check if user has permission to view this task
    if not (request.user == task.created_by or request.user == task.assigned_to or request.user.is_superuser):
        messages.error(request, 'You do not have permission to view this task.')
        return redirect('core:task_list')
    
    context = {
        'title': task.title,
        'description': 'Task details and management',
        'task': task,
    }
    return render(request, 'core/task_detail.html', context)

@login_required
def task_create(request):
    """Create a new task"""
    # Ensure user has profile
    if not hasattr(request.user, 'profile'):
        from .profile import UserProfile
        UserProfile.objects.create(user=request.user, role='manager')  # Make them manager so they can create tasks
    
    # Check if user can manage tasks
    if not request.user.profile.can_manage_tasks():
        messages.error(request, 'You do not have permission to create tasks.')
        return redirect('core:task_list')
    
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            messages.success(request, f'Task "{task.title}" created successfully!')
            return redirect('core:task_detail', task_id=task.id)
        else:
            messages.error(request, 'There was an error creating the task. Please check the form.')
    else:
        form = TaskForm()
    
    context = {
        'title': 'Create New Task',
        'description': 'Add a new task to your workflow',
        'form': form,
    }
    return render(request, 'core/task_form.html', context)

@login_required
def task_edit(request, task_id):
    """Edit an existing task"""
    task = get_object_or_404(Task, id=task_id)
    
    # Check if user has permission to edit this task
    if not (request.user == task.created_by or request.user == task.assigned_to or request.user.profile.can_manage_tasks()):
        messages.error(request, 'You do not have permission to edit this task.')
        return redirect('core:task_detail', task_id=task.id)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            
            # Update completed_at if status changed to completed
            if task.status == 'completed' and not task.completed_at:
                task.completed_at = timezone.now()
                task.save()
            
            messages.success(request, f'Task "{task.title}" updated successfully!')
            return redirect('core:task_detail', task_id=task.id)
        else:
            messages.error(request, 'There was an error updating the task. Please check the form.')
    else:
        form = TaskForm(instance=task)
    
    context = {
        'title': f'Edit Task: {task.title}',
        'description': 'Update task information',
        'form': form,
        'task': task,
    }
    return render(request, 'core/task_form.html', context)

@login_required
def task_delete(request, task_id):
    """Delete a task"""
    task = get_object_or_404(Task, id=task_id)
    
    # Check if user has permission to delete this task
    if not (request.user == task.created_by or request.user.is_superuser):
        messages.error(request, 'You do not have permission to delete this task.')
        return redirect('core:task_detail', task_id=task.id)
    
    if request.method == 'POST':
        task_title = task.title
        task.delete()
        messages.success(request, f'Task "{task_title}" deleted successfully!')
        return redirect('core:task_list')
    
    context = {
        'title': f'Delete Task: {task.title}',
        'description': 'Confirm task deletion',
        'task': task,
    }
    return render(request, 'core/task_confirm_delete.html', context)

@login_required
def task_complete(request, task_id):
    """Mark a task as completed"""
    task = get_object_or_404(Task, id=task_id)
    
    # Check if user has permission to complete this task
    if not (request.user == task.created_by or request.user == task.assigned_to or request.user.is_superuser):
        messages.error(request, 'You do not have permission to complete this task.')
        return redirect('core:task_detail', task_id=task.id)
    
    if task.status != 'completed':
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.save()
        messages.success(request, f'Task "{task.title}" marked as completed!')
    else:
        messages.info(request, 'Task is already completed.')
    
    return redirect('core:task_detail', task_id=task.id)

@login_required
def my_tasks(request):
    """Show tasks assigned to the current user"""
    tasks = Task.objects.filter(assigned_to=request.user).order_by('-created_at')
    
    # Apply same filtering logic as task_list
    search_query = request.GET.get('search', '')
    if search_query:
        tasks = tasks.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    priority_filter = request.GET.get('priority', '')
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    
    # Pagination
    paginator = Paginator(tasks, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'My Tasks',
        'description': 'Tasks assigned to you',
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'status_choices': Task.STATUS_CHOICES,
        'priority_choices': Task.PRIORITY_CHOICES,
    }
    return render(request, 'core/task_list.html', context)
