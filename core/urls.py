from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Dashboard and main views
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Task management URLs
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/my/', views.my_tasks, name='my_tasks'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('tasks/<int:task_id>/edit/', views.task_edit, name='task_edit'),
    path('tasks/<int:task_id>/delete/', views.task_delete, name='task_delete'),
    path('tasks/<int:task_id>/complete/', views.task_complete, name='task_complete'),
]
