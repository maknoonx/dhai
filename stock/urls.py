from django.urls import path
from . import views

app_name = 'stock'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Products
    path('products/', views.products_list, name='products'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    
    # Import Products
    path('products/import/', views.import_products, name='import_products'),
    path('products/import/process/', views.import_products_process, name='import_products_process'),
    path('products/import/template/', views.download_template, name='download_template'),
    
    # Categories
    path('categories/', views.categories_list, name='categories'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # Suppliers
    path('suppliers/', views.suppliers_list, name='suppliers'),
    path('suppliers/add/', views.supplier_add, name='supplier_add'),
    path('suppliers/<int:pk>/edit/', views.supplier_edit, name='supplier_edit'),
    path('suppliers/<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),
    path('suppliers/<int:pk>/details/', views.supplier_detail_json, name='supplier_detail_json'),
    
    # Laboratory
path('laboratory/', views.laboratory, name='laboratory'),
path('laboratory/add/', views.laboratory_add, name='laboratory_add'),
path('laboratory/<int:pk>/edit/', views.laboratory_edit, name='laboratory_edit'),
path('laboratory/<int:pk>/delete/', views.laboratory_delete, name='laboratory_delete'),
path('laboratory/<int:pk>/details/', views.laboratory_detail_json, name='laboratory_detail_json'),


]


