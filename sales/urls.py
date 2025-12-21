from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    # قائمة الفواتير
    path('', views.sale_list, name='list'),
    
    # إضافة وتعديل
    path('add/', views.sale_add, name='add'),
    path('<int:pk>/edit/', views.sale_edit, name='edit'),
    path('<int:pk>/delete/', views.sale_delete, name='delete'),
    
    # عرض وطباعة
    path('<int:pk>/', views.sale_detail, name='detail'),
    path('<int:pk>/print/', views.sale_print, name='print'),
    
    # الدفعات
    path('<int:pk>/payment/add/', views.add_payment, name='add_payment'),
    
    # إشعارات دائن ومدين
    path('<int:pk>/credit-note/', views.credit_note, name='credit_note'),
    path('<int:pk>/debit-note/', views.debit_note, name='debit_note'),
    
    # API
    path('api/product/<int:pk>/', views.get_product_info, name='get_product_info'),

    path('<int:invoice_id>/print-eye-exam/', views.print_eye_exam, name='print_eye_exam'),
]