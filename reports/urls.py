from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Main Reports
    path('daily-balance/', views.daily_balance, name='daily_balance'),
    path('revenue/', views.revenue_report, name='revenue'),
    path('inventory/', views.inventory_report, name='inventory'),
    path('sales/', views.sales_report, name='sales'),
    path('profit/', views.profit_report, name='profit'),
    path('vat/', views.vat_report, name='vat'),  # تقرير ضريبة القيمة المضافة
]