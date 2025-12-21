from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, F, Q
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal
import json

from sales.models import Sale, SaleItem, Payment
from stock.models import Product, Category, StockMovement
from customers.models import Customer


@login_required
def dashboard(request):
    """لوحة التحكم الرئيسية للتقارير"""
    
    # الفترة الافتراضية (آخر 30 يوم)
    today = timezone.now().date()
    date_from = today - timedelta(days=30)
    date_to = today
    
    # إحصائيات سريعة
    total_sales = Sale.objects.filter(
        order_date__date__range=[date_from, date_to]
    ).aggregate(
        count=Count('id'),
        total=Sum('total_amount'),
        paid=Sum('paid_amount')
    )
    
    total_products = Product.objects.filter(is_active=True).count()
    low_stock_products = Product.objects.filter(
        is_active=True,
        quantity__lte=F('min_quantity')
    ).count()
    
    total_customers = Customer.objects.count()
    new_customers = Customer.objects.filter(
        created_at__date__range=[date_from, date_to]
    ).count()
    
    # بيانات الرسوم البيانية
    # المبيعات اليومية (آخر 7 أيام)
    daily_sales = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        sales = Sale.objects.filter(order_date__date=date).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        daily_sales.append({
            'date': date.strftime('%Y-%m-%d'),
            'date_ar': date.strftime('%d/%m'),
            'amount': float(sales)
        })
    
    # أفضل المنتجات مبيعاً
    top_products = SaleItem.objects.filter(
        sale__order_date__date__range=[date_from, date_to],
        product__isnull=False
    ).values(
        'product__item_name'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_amount=Sum(F('quantity') * F('unit_price'))
    ).order_by('-total_quantity')[:5]
    
    # التصنيفات الأكثر مبيعاً
    top_categories = SaleItem.objects.filter(
        sale__order_date__date__range=[date_from, date_to],
        product__isnull=False
    ).values(
        'product__category__name'
    ).annotate(
        total_amount=Sum(F('quantity') * F('unit_price'))
    ).order_by('-total_amount')[:5]
    
    # حالات الطلبات
    order_status = Sale.objects.filter(
        order_date__date__range=[date_from, date_to]
    ).values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    context = {
        'date_from': date_from,
        'date_to': date_to,
        'total_sales_count': total_sales['count'] or 0,
        'total_sales_amount': total_sales['total'] or 0,
        'total_paid': total_sales['paid'] or 0,
        'total_remaining': (total_sales['total'] or 0) - (total_sales['paid'] or 0),
        'total_products': total_products,
        'low_stock_products': low_stock_products,
        'total_customers': total_customers,
        'new_customers': new_customers,
        'daily_sales': json.dumps(daily_sales),
        'top_products': list(top_products),
        'top_categories': list(top_categories),
        'order_status': list(order_status),
    }
    
    return render(request, 'reports/dashboard.html', context)


@login_required
def daily_balance(request):
    """تقرير الموازنة اليومية"""
    
    # التاريخ المطلوب
    report_date = request.GET.get('date')
    if report_date:
        report_date = datetime.strptime(report_date, '%Y-%m-%d').date()
    else:
        report_date = timezone.now().date()
    
    # المبيعات
    sales = Sale.objects.filter(order_date__date=report_date)
    total_sales = sales.aggregate(
        count=Count('id'),
        total=Sum('total_amount'),
        paid=Sum('paid_amount')
    )
    
    # الدفعات
    payments = Payment.objects.filter(payment_date__date=report_date)
    total_payments = payments.aggregate(total=Sum('amount'))['total'] or 0
    
    # المشتريات (من حركات المخزون)
    purchases = StockMovement.objects.filter(
        created_at__date=report_date,
        movement_type='in'
    ).count()
    
    # المرتجعات
    returns = StockMovement.objects.filter(
        created_at__date=report_date,
        movement_type='return'
    ).count()
    
    # حالات الدفع
    payment_methods = Payment.objects.filter(
        payment_date__date=report_date
    ).values('payment_method').annotate(
        total=Sum('amount')
    ).order_by('payment_method')
    
    # المبيعات بالساعة
    hourly_sales = []
    for hour in range(24):
        sales_count = Sale.objects.filter(
            order_date__date=report_date,
            order_date__hour=hour
        ).count()
        if sales_count > 0:
            hourly_sales.append({
                'hour': f"{hour:02d}:00",
                'count': sales_count
            })
    
    context = {
        'report_date': report_date,
        'total_sales_count': total_sales['count'] or 0,
        'total_sales_amount': total_sales['total'] or 0,
        'total_paid': total_sales['paid'] or 0,
        'total_remaining': (total_sales['total'] or 0) - (total_sales['paid'] or 0),
        'total_payments': total_payments,
        'purchases_count': purchases,
        'returns_count': returns,
        'payment_methods': list(payment_methods),
        'hourly_sales': json.dumps(hourly_sales),
        'sales_list': sales[:20],  # آخر 20 فاتورة
    }
    
    return render(request, 'reports/daily_balance.html', context)


@login_required
def revenue_report(request):
    """تقرير الإيرادات العام"""
    
    # الفترة
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from and date_to:
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    else:
        date_to = timezone.now().date()
        date_from = date_to - timedelta(days=30)
    
    # إجمالي الإيرادات
    sales = Sale.objects.filter(order_date__date__range=[date_from, date_to])
    
    total_revenue = sales.aggregate(
        count=Count('id'),
        subtotal=Sum('subtotal'),
        discount=Sum('discount'),
        tax=Sum('tax'),
        total=Sum('total_amount'),
        paid=Sum('paid_amount')
    )
    
    # الإيرادات الشهرية
    monthly_revenue = []
    current_date = date_from
    while current_date <= date_to:
        month_end = min(
            datetime(current_date.year, current_date.month + 1, 1).date() - timedelta(days=1) 
            if current_date.month < 12 
            else datetime(current_date.year, 12, 31).date(),
            date_to
        )
        
        month_sales = Sale.objects.filter(
            order_date__date__range=[current_date, month_end]
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        monthly_revenue.append({
            'month': current_date.strftime('%Y-%m'),
            'month_ar': current_date.strftime('%B %Y'),
            'amount': float(month_sales)
        })
        
        # الانتقال للشهر التالي
        if current_date.month == 12:
            current_date = datetime(current_date.year + 1, 1, 1).date()
        else:
            current_date = datetime(current_date.year, current_date.month + 1, 1).date()
        
        if current_date > date_to:
            break
    
    # الإيرادات حسب طريقة الدفع
    payment_methods = Payment.objects.filter(
        payment_date__date__range=[date_from, date_to]
    ).values('payment_method').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # الإيرادات حسب التصنيف
    category_revenue = SaleItem.objects.filter(
        sale__order_date__date__range=[date_from, date_to],
        product__isnull=False
    ).values(
        'product__category__name'
    ).annotate(
        total=Sum(F('quantity') * F('unit_price'))
    ).order_by('-total')[:10]
    
    context = {
        'date_from': date_from,
        'date_to': date_to,
        'total_sales_count': total_revenue['count'] or 0,
        'total_subtotal': total_revenue['subtotal'] or 0,
        'total_discount': total_revenue['discount'] or 0,
        'total_tax': total_revenue['tax'] or 0,
        'total_revenue': total_revenue['total'] or 0,
        'total_paid': total_revenue['paid'] or 0,
        'total_remaining': (total_revenue['total'] or 0) - (total_revenue['paid'] or 0),
        'monthly_revenue': json.dumps(monthly_revenue),
        'payment_methods': list(payment_methods),
        'category_revenue': list(category_revenue),
    }
    
    return render(request, 'reports/revenue_report.html', context)


@login_required
def inventory_report(request):
    """تقرير المخزون"""
    
    # الفلترة
    category_id = request.GET.get('category')
    stock_status = request.GET.get('stock_status')
    
    products = Product.objects.filter(is_active=True).select_related('category', 'supplier')
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    if stock_status == 'out':
        products = products.filter(quantity=0)
    elif stock_status == 'low':
        products = products.filter(quantity__gt=0, quantity__lte=F('min_quantity'))
    elif stock_status == 'available':
        products = products.filter(quantity__gt=F('min_quantity'))
    
    # الإحصائيات
    total_products = products.count()
    out_of_stock = products.filter(quantity=0).count()
    low_stock = products.filter(quantity__gt=0, quantity__lte=F('min_quantity')).count()
    
    total_inventory_value = products.aggregate(
        cost_value=Sum(F('quantity') * F('cost_price')),
        selling_value=Sum(F('quantity') * F('selling_price'))
    )
    
    # المخزون حسب التصنيف
    category_stock = Category.objects.filter(
        is_active=True,
        products__is_active=True
    ).annotate(
        product_count=Count('products'),
        total_quantity=Sum('products__quantity'),
        total_value=Sum(F('products__quantity') * F('products__selling_price'))
    ).order_by('-total_value')
    
    # أكثر المنتجات قيمة
    top_value_products = products.annotate(
        total_value=F('quantity') * F('selling_price')
    ).order_by('-total_value')[:10]
    
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'products': products.order_by('category__name', 'item_name'),
        'categories': categories,
        'selected_category': category_id,
        'stock_status': stock_status,
        'total_products': total_products,
        'out_of_stock': out_of_stock,
        'low_stock': low_stock,
        'total_cost_value': total_inventory_value['cost_value'] or 0,
        'total_selling_value': total_inventory_value['selling_value'] or 0,
        'expected_profit': (total_inventory_value['selling_value'] or 0) - (total_inventory_value['cost_value'] or 0),
        'category_stock': category_stock,
        'top_value_products': top_value_products,
    }
    
    return render(request, 'reports/inventory_report.html', context)


@login_required
def sales_report(request):
    """تقرير المبيعات التفصيلي"""
    
    # الفترة
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from and date_to:
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    else:
        date_to = timezone.now().date()
        date_from = date_to - timedelta(days=7)
    
    sales = Sale.objects.filter(
        order_date__date__range=[date_from, date_to]
    ).select_related('customer')
    
    # الإحصائيات
    stats = sales.aggregate(
        count=Count('id'),
        total=Sum('total_amount'),
        avg=Avg('total_amount'),
        paid=Sum('paid_amount')
    )
    
    # أفضل المنتجات
    top_products = SaleItem.objects.filter(
        sale__order_date__date__range=[date_from, date_to],
        product__isnull=False
    ).values(
        'product__item_name',
        'product__barcode'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_amount=Sum(F('quantity') * F('unit_price'))
    ).order_by('-total_quantity')[:10]
    
    # أفضل العملاء
    top_customers = Sale.objects.filter(
        order_date__date__range=[date_from, date_to]
    ).values(
        'customer__name',
        'customer__customer_id'
    ).annotate(
        total_orders=Count('id'),
        total_amount=Sum('total_amount')
    ).order_by('-total_amount')[:10]
    
    context = {
        'date_from': date_from,
        'date_to': date_to,
        'sales': sales.order_by('-order_date')[:100],
        'total_count': stats['count'] or 0,
        'total_amount': stats['total'] or 0,
        'average_amount': stats['avg'] or 0,
        'total_paid': stats['paid'] or 0,
        'top_products': list(top_products),
        'top_customers': list(top_customers),
    }
    
    return render(request, 'reports/sales_report.html', context)


@login_required
def profit_report(request):
    """تقرير الأرباح"""
    
    # الفترة
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from and date_to:
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    else:
        date_to = timezone.now().date()
        date_from = date_to - timedelta(days=30)
    
    # حساب الأرباح من المنتجات المباعة
    sale_items = SaleItem.objects.filter(
        sale__order_date__date__range=[date_from, date_to],
        product__isnull=False
    ).select_related('product')
    
    total_revenue = Decimal(0)
    total_cost = Decimal(0)
    
    for item in sale_items:
        revenue = item.quantity * item.unit_price
        cost = item.quantity * item.product.cost_price
        total_revenue += revenue
        total_cost += cost
    
    total_profit = total_revenue - total_cost
    profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    # الأرباح حسب المنتج
    product_profits = []
    for item in sale_items:
        product_profits.append({
            'product_name': item.product.item_name,
            'quantity': item.quantity,
            'revenue': float(item.quantity * item.unit_price),
            'cost': float(item.quantity * item.product.cost_price),
            'profit': float(item.quantity * (item.unit_price - item.product.cost_price))
        })
    
    # ترتيب حسب الربح
    product_profits.sort(key=lambda x: x['profit'], reverse=True)
    
    context = {
        'date_from': date_from,
        'date_to': date_to,
        'total_revenue': total_revenue,
        'total_cost': total_cost,
        'total_profit': total_profit,
        'profit_margin': profit_margin,
        'product_profits': product_profits[:20],
    }
    
    return render(request, 'reports/profit_report.html', context)


# استبدل دالة vat_report في reports/views.py بهذه النسخة المُصححة

@login_required
def vat_report(request):
    """تقرير ضريبة القيمة المضافة"""
    
    # الفترة
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from and date_to:
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    else:
        # الشهر الحالي
        today = timezone.now().date()
        date_from = datetime(today.year, today.month, 1).date()
        if today.month == 12:
            date_to = datetime(today.year, 12, 31).date()
        else:
            date_to = datetime(today.year, today.month + 1, 1).date() - timedelta(days=1)
    
    # المبيعات الخاضعة للضريبة
    sales = Sale.objects.filter(
        order_date__date__range=[date_from, date_to]
    )
    
    # إحصائيات الضريبة
    vat_stats = sales.aggregate(
        total_sales_count=Count('id'),
        total_subtotal=Sum('subtotal'),
        total_discount=Sum('discount'),
        total_taxable=Sum(F('subtotal') - F('discount')),
        total_tax=Sum('tax'),
        total_with_tax=Sum('total_amount')
    )
    
    # تصفير القيم None
    for key in vat_stats:
        if vat_stats[key] is None:
            vat_stats[key] = 0
    
    # المبيعات اليومية
    daily_vat = []
    current_date = date_from
    while current_date <= date_to:
        day_sales = sales.filter(order_date__date=current_date)
        day_stats = day_sales.aggregate(
            subtotal=Sum('subtotal'),
            tax=Sum('tax'),
            total=Sum('total_amount')
        )
        
        if day_stats['total']:
            daily_vat.append({
                'date_str': current_date.strftime('%Y-%m-%d'),  # ✅ تحويل إلى string
                'date_ar': current_date.strftime('%d/%m'),
                'sales_count': day_sales.count(),
                'subtotal': float(day_stats['subtotal'] or 0),
                'tax': float(day_stats['tax'] or 0),
                'total': float(day_stats['total'] or 0)
            })
        
        current_date += timedelta(days=1)
    
    # الضريبة حسب طريقة الدفع
    vat_by_payment = sales.values('payment_method').annotate(
        total_tax=Sum('tax'),
        total_amount=Sum('total_amount')
    ).order_by('-total_tax')
    
    # تفاصيل الفواتير
    sales_details = sales.select_related('customer').order_by('-order_date')[:100]
    
    # معدل الضريبة
    vat_rate = Decimal('0.15')  # 15%
    
    context = {
        'date_from': date_from,
        'date_to': date_to,
        'vat_rate': vat_rate * 100,  # 15
        'total_sales_count': vat_stats['total_sales_count'],
        'total_subtotal': vat_stats['total_subtotal'],
        'total_discount': vat_stats['total_discount'],
        'total_taxable': vat_stats['total_taxable'],
        'total_tax': vat_stats['total_tax'],
        'total_with_tax': vat_stats['total_with_tax'],
        'daily_vat': json.dumps(daily_vat),  # ✅ الآن آمن للتحويل
        'vat_by_payment': list(vat_by_payment),
        'sales_details': sales_details,
    }
    
    return render(request, 'reports/vat_report.html', context)