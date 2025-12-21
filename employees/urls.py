from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    # Employee URLs
    path('', views.employee_list, name='list'),
    path('add/', views.employee_add, name='add'),
    path('<int:pk>/', views.employee_detail, name='detail'),
    path('<int:pk>/edit/', views.employee_edit, name='edit'),
    path('<int:pk>/toggle-active/', views.employee_toggle_active, name='toggle_active'),
    
    # Group URLs
    path('groups/', views.group_list, name='group_list'),
    path('groups/add/', views.group_add, name='group_add'),
    path('groups/<int:pk>/', views.group_detail, name='group_detail'),
    path('groups/<int:pk>/edit/', views.group_edit, name='group_edit'),
    path('groups/<int:pk>/delete/', views.group_delete, name='group_delete'),
]