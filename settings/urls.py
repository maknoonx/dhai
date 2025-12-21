from django.urls import path
from . import views

app_name = 'settings'

urlpatterns = [
    path('', views.settings_index, name='index'),
    path('company/update/', views.update_company_settings, name='update_company'),
    path('payment/add/', views.add_payment_method, name='add_payment'),
    path('payment/<int:pk>/edit/', views.edit_payment_method, name='edit_payment'),
    path('payment/<int:pk>/delete/', views.delete_payment_method, name='delete_payment'),
    path('attachment/add/', views.add_attachment, name='add_attachment'),
    path('attachment/<int:pk>/edit/', views.edit_attachment, name='edit_attachment'),
    path('attachment/<int:pk>/delete/', views.delete_attachment, name='delete_attachment'),
]