from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import models
from datetime import timedelta
from customers.models import Customer
from stock.models import Product
from sales.models import Sale
# في core/views.py أو main/views.py
# استبدل دالة dashboard بهذا الكود المحسّن

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from sales.models import Sale, Payment
from customers.models import Customer
from stock.models import Product
from reports.models import Report


@login_required
def dashboard(request):
    """لوحة التحكم الرئيسية مع إحصائيات يومية"""
    
    # تاريخ اليوم
    today = timezone.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    # ==========================================
    # الإحصائيات اليومية
    # ==========================================
    
    # المبيعات اليومية
    today_sales = Sale.objects.filter(
        order_date__range=(today_start, today_end)
    ).exclude(status='cancelled')
    
    daily_stats = {
        # عدد الفواتير اليوم
        'invoices_count': today_sales.count(),
        
        # إجمالي المبيعات اليوم
        'total_sales': today_sales.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0'),
        
        # المبالغ المدفوعة اليوم
        'total_paid': today_sales.aggregate(
            total=Sum('paid_amount')
        )['total'] or Decimal('0'),
        
        # المبالغ المتبقية اليوم
        'total_remaining': (today_sales.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')) - (today_sales.aggregate(
            total=Sum('paid_amount')
        )['total'] or Decimal('0')),
        
        # عدد العملاء الجدد اليوم
        'new_customers': Customer.objects.filter(
            created_at__range=(today_start, today_end)
        ).count(),
        
        # عدد الفواتير المدفوعة بالكامل
        'paid_invoices': today_sales.filter(
            paid_amount__gte=models.F('total_amount')
        ).count(),
        
        # عدد الفواتير المعلقة
        'pending_invoices': today_sales.filter(
            paid_amount__lt=models.F('total_amount')
        ).count(),
    }
    
    # ==========================================
    # الفواتير الجارية (غير المكتملة)
    # ==========================================
    
    current_invoices = Sale.objects.filter(
        status__in=['created', 'lab', 'ready', 'received']
    ).select_related('customer').order_by('-order_date')[:20]
    
    # إحصائيات حسب الحالة
    status_counts = {}
    for status_code, status_name in Sale.STATUS_CHOICES:
        if status_code != 'completed':  # استبعاد المكتملة
            status_counts[status_code] = Sale.objects.filter(
                status=status_code
            ).count()
    
    # ==========================================
    # إحصائيات إضافية
    # ==========================================
    
    # المنتجات منخفضة المخزون
    low_stock_products = Product.objects.filter(
        quantity__lte=models.F('min_quantity'),
        quantity__gt=0,
        is_active=True
    ).count()
    
    # المنتجات النافذة
    out_of_stock_products = Product.objects.filter(
        quantity=0,
        is_active=True
    ).count()
    
    # ==========================================
    # السياق (Context)
    # ==========================================
    
    context = {
        'daily_stats': daily_stats,
        'current_invoices': current_invoices,
        'status_counts': status_counts,
        'low_stock_products': low_stock_products,
        'out_of_stock_products': out_of_stock_products,
        'today': today,
    }
    
    return render(request, 'dashboard.html', context)