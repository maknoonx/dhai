from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    # Customer list and management
    path('', views.customers_list, name='list'),
    path('add/', views.customer_add, name='add'),
    path('<int:pk>/edit/', views.customer_edit, name='edit'),
    path('<int:pk>/delete/', views.customer_delete, name='delete'),
    path('<int:pk>/profile/', views.customer_profile, name='profile'),
    
    # Notification settings
    path('<int:pk>/notifications/update/', views.customer_notifications_update, name='notifications_update'),
    path('<int:customer_pk>/notification/send/', views.notification_send, name='notification_send'),
    
    # Eye exams
    path('<int:customer_pk>/eye-exam/add/', views.eye_exam_add, name='eye_exam_add'),
    path('eye-exam/<int:pk>/edit/', views.eye_exam_edit, name='eye_exam_edit'),
]