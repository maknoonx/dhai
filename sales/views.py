from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count, F
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from decimal import Decimal
import json

from .models import Sale, SaleItem, Payment
from customers.models import Customer
from stock.models import Product, Laboratory
from settings.models import CompanySettings


@login_required
def sale_list(request):
    """عرض قائمة المبيعات"""
    
    # الفلترة
    search_query = request.GET.get('search', '')
    status = request.GET.get('status', '')
    payment_status = request.GET.get('payment_status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    sales = Sale.objects.select_related('customer').all()
    
    # البحث بالعميل أو رقم الطلب
    if search_query:
        sales = sales.filter(
            Q(order_number__icontains=search_query) |
            Q(customer__name__icontains=search_query) |
            Q(customer__phone__icontains=search_query) |
            Q(customer__customer_id__icontains=search_query)
        )
    
    # فلترة حسب حالة الطلب
    if status:
        sales = sales.filter(status=status)
    
    # فلترة حسب حالة الدفع
    if payment_status:
        if payment_status == 'unpaid':
            sales = sales.filter(paid_amount=0)
        elif payment_status == 'partial':
            sales = sales.filter(paid_amount__gt=0, paid_amount__lt=F('total_amount'))
        elif payment_status == 'paid':
            sales = sales.filter(paid_amount__gte=F('total_amount'))
    
    # فلترة حسب التاريخ
    if date_from:
        sales = sales.filter(order_date__gte=date_from)
    if date_to:
        sales = sales.filter(order_date__lte=date_to)
    
    sales = sales.order_by('-order_date')
    
    # الإحصائيات
    total_sales = sales.count()
    total_amount = sales.aggregate(total=Sum('total_amount'))['total'] or 0
    total_paid = sales.aggregate(total=Sum('paid_amount'))['total'] or 0
    total_remaining = total_amount - total_paid
    
    # حالات الطلبات - تحويل إلى قاموس
    status_counts = {}
    for s in Sale.STATUS_CHOICES:
        status_counts[s[0]] = sales.filter(status=s[0]).count()
    
    context = {
        'sales': sales,
        'search_query': search_query,
        'status': status,
        'payment_status': payment_status,
        'date_from': date_from,
        'date_to': date_to,
        'total_sales': total_sales,
        'total_amount': total_amount,
        'total_paid': total_paid,
        'total_remaining': total_remaining,
        'status_counts': status_counts,
        'status_choices': Sale.STATUS_CHOICES,
    }
    
    return render(request, 'sales/sale_list.html', context)


@login_required
def sale_add(request):
    """إضافة فاتورة جديدة"""
    
    if request.method == 'POST':
        try:
            # بيانات الفاتورة
            customer_id = request.POST.get('customer_id')
            delivery_date = request.POST.get('delivery_date') or None
            notes = request.POST.get('notes', '')
            prescription_notes = request.POST.get('prescription_notes', '')
            payment_method = request.POST.get('payment_method', 'cash')
            paid_amount = Decimal(request.POST.get('paid_amount', 0))
            discount = Decimal(request.POST.get('discount', 0))
            laboratory_id = request.POST.get('laboratory_id') or None
            
            # التحقق من العميل
            customer = get_object_or_404(Customer, pk=customer_id)
            
            # توليد رقم الطلب
            last_sale = Sale.objects.order_by('-id').first()
            if last_sale and last_sale.order_number:
                try:
                    last_number = int(last_sale.order_number.split('-')[1])
                    new_number = last_number + 1
                except:
                    new_number = 1
            else:
                new_number = 1
            order_number = f'INV-{new_number:05d}'
            
            # إنشاء الفاتورة
            sale = Sale.objects.create(
                order_number=order_number,
                customer=customer,
                delivery_date=delivery_date,
                notes=notes,
                prescription_notes=prescription_notes,
                payment_method=payment_method,
                paid_amount=0,  # سيتم التحديث لاحقاً
                discount=discount,
                created_by=request.user.username if request.user.is_authenticated else 'System'
            )
            
            # إضافة المعمل إن وجد
            if laboratory_id:
                sale.laboratory_id = laboratory_id
            
            # المنتجات
            products_data = json.loads(request.POST.get('products', '[]'))
            subtotal = Decimal(0)
            
            for item in products_data:
                product = Product.objects.get(pk=item['product_id'])
                quantity = int(item['quantity'])
                unit_price = Decimal(item['unit_price'])
                
                # إنشاء عنصر الفاتورة
                sale_item = SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    prescription_right=item.get('prescription_right', ''),
                    prescription_left=item.get('prescription_left', '')
                )
                
                subtotal += sale_item.total_price
                
                # تحديث المخزون
                product.quantity -= quantity
                product.save()
            
            # الخدمات الإضافية
            services_data = json.loads(request.POST.get('services', '[]'))
            for service in services_data:
                service_name = service['name']
                service_price = Decimal(service['price'])
                
                # إنشاء عنصر خدمة
                SaleItem.objects.create(
                    sale=sale,
                    product=None,  # الخدمات ليس لها منتج
                    quantity=1,
                    unit_price=service_price,
                    service_name=service_name
                )
                
                subtotal += service_price
            
            # حساب الضريبة (15%)
            tax = subtotal * Decimal('0.15')
            
            # تحديث الفاتورة
            sale.subtotal = subtotal
            sale.tax = tax
            sale.paid_amount = paid_amount
            sale.save()
            
            # إضافة الدفعة إن وجدت
            if paid_amount > 0:
                Payment.objects.create(
                    sale=sale,
                    amount=paid_amount,
                    payment_method=payment_method,
                    notes=f'دفعة أولية عند إنشاء الفاتورة',
                    created_by=request.user.username if request.user.is_authenticated else 'System'
                )
            
            messages.success(request, f'تم إنشاء الفاتورة {order_number} بنجاح')
            return redirect('sales:detail', pk=sale.pk)
            
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
            return redirect('sales:add')
    
    # GET request
    customers = Customer.objects.all().order_by('name')
    products = Product.objects.filter(is_active=True).select_related('category')
    laboratories = Laboratory.objects.filter(is_active=True)
    
    context = {
        'customers': customers,
        'products': products,
        'laboratories': laboratories,
        'payment_methods': Sale.PAYMENT_METHODS,
    }
    
    return render(request, 'sales/sale_add.html', context)


@login_required
def sale_detail(request, pk):
    """عرض تفاصيل الفاتورة"""
    
    sale = get_object_or_404(Sale.objects.select_related('customer', 'laboratory'), pk=pk)
    items = sale.items.select_related('product').all()
    payments = sale.payments.all().order_by('-payment_date')
    
    context = {
        'sale': sale,
        'items': items,
        'payments': payments,
        'remaining_amount': sale.get_remaining_amount(),
        'is_paid': sale.is_paid(),
        'company_settings': CompanySettings.get_settings(),
    }
    
    return render(request, 'sales/sale_detail.html', context)


@login_required
def sale_edit(request, pk):
    """تعديل الفاتورة"""
    
    sale = get_object_or_404(Sale, pk=pk)
    
    if request.method == 'POST':
        try:
            sale.status = request.POST.get('status')
            sale.delivery_date = request.POST.get('delivery_date') or None
            sale.notes = request.POST.get('notes', '')
            sale.prescription_notes = request.POST.get('prescription_notes', '')
            laboratory_id = request.POST.get('laboratory_id') or None
            
            if laboratory_id:
                sale.laboratory_id = laboratory_id
            else:
                sale.laboratory = None
            
            # تحديث تاريخ الإكمال إذا تم التسليم
            if sale.status in ['received', 'completed'] and not sale.completed_date:
                sale.completed_date = timezone.now()
            
            sale.updated_by = request.user.username if request.user.is_authenticated else 'System'
            sale.save()
            
            messages.success(request, 'تم تحديث الفاتورة بنجاح')
            return redirect('sales:detail', pk=sale.pk)
            
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
    
    laboratories = Laboratory.objects.filter(is_active=True)
    
    context = {
        'sale': sale,
        'status_choices': Sale.STATUS_CHOICES,
        'laboratories': laboratories,
    }
    
    return render(request, 'sales/sale_edit.html', context)


@login_required
def sale_delete(request, pk):
    """حذف الفاتورة"""
    
    sale = get_object_or_404(Sale, pk=pk)
    
    if request.method == 'POST':
        # إرجاع المنتجات للمخزون
        for item in sale.items.all():
            if item.product:
                item.product.quantity += item.quantity
                item.product.save()
        
        order_number = sale.order_number
        sale.delete()
        
        messages.success(request, f'تم حذف الفاتورة {order_number} بنجاح')
        return redirect('sales:list')
    
    return redirect('sales:detail', pk=pk)


@login_required
def sale_print(request, pk):
    """طباعة الفاتورة"""
    
    sale = get_object_or_404(Sale.objects.select_related('customer', 'laboratory'), pk=pk)
    items = sale.items.select_related('product').all()
    company_settings = CompanySettings.get_settings()
    
    # توليد QR Code
    import qrcode
    from io import BytesIO
    import base64
    
    # بيانات QR Code حسب متطلبات هيئة الزكاة والدخل
    qr_data = f"""اسم المنشأة: {company_settings.company_name_ar or 'البصريات الحديثة'}
الرقم الضريبي: {company_settings.tax_number or 'غير متوفر'}
التاريخ: {sale.order_date.strftime('%Y-%m-%d %H:%M')}
الإجمالي: {sale.total_amount} ر.س
الضريبة: {sale.tax} ر.س"""
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data.strip())
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    context = {
        'sale': sale,
        'items': items,
        'company': company_settings,
        'qr_code': qr_code_base64,
    }
    
    return render(request, 'sales/sale_print.html', context)


@login_required
def add_payment(request, pk):
    """إضافة دفعة"""
    
    if request.method == 'POST':
        sale = get_object_or_404(Sale, pk=pk)
        
        amount = Decimal(request.POST.get('amount', 0))
        payment_method = request.POST.get('payment_method')
        reference = request.POST.get('reference', '')
        notes = request.POST.get('notes', '')
        
        # التحقق من المبلغ
        remaining = sale.get_remaining_amount()
        if amount > remaining:
            messages.error(request, 'المبلغ أكبر من المبلغ المتبقي')
            return redirect('sales:detail', pk=pk)
        
        # إضافة الدفعة
        Payment.objects.create(
            sale=sale,
            amount=amount,
            payment_method=payment_method,
            reference=reference,
            notes=notes,
            created_by=request.user.username if request.user.is_authenticated else 'System'
        )
        
        # تحديث المبلغ المدفوع
        sale.paid_amount += amount
        sale.save()
        
        messages.success(request, f'تم إضافة دفعة بمبلغ {amount} ريال')
        return redirect('sales:detail', pk=pk)
    
    return redirect('sales:list')


@login_required
def get_product_info(request, pk):
    """الحصول على معلومات المنتج"""
    
    product = get_object_or_404(Product, pk=pk)
    
    data = {
        'id': product.id,
        'name': product.item_name,
        'barcode': product.barcode,
        'price': float(product.selling_price),
        'quantity_available': product.quantity,
        'category': product.category.name if product.category else '',
    }
    
    return JsonResponse(data)


@login_required
def credit_note(request, pk):
    """إنشاء إشعار دائن (مرتجع)"""
    
    sale = get_object_or_404(Sale, pk=pk)
    
    if request.method == 'POST':
        # إنشاء فاتورة مرتجع
        credit_sale = Sale.objects.create(
            order_number=f'CN-{sale.order_number}',
            customer=sale.customer,
            status='cancelled',
            notes=f'إشعار دائن للفاتورة {sale.order_number}',
            subtotal=-sale.subtotal,
            discount=-sale.discount,
            tax=-sale.tax,
            payment_method=sale.payment_method,
            created_by=request.user.username if request.user.is_authenticated else 'System'
        )
        
        # نسخ العناصر
        for item in sale.items.all():
            if item.product:
                SaleItem.objects.create(
                    sale=credit_sale,
                    product=item.product,
                    quantity=-item.quantity,
                    unit_price=item.unit_price
                )
                
                # إرجاع المخزون
                item.product.quantity += item.quantity
                item.product.save()
        
        messages.success(request, f'تم إنشاء إشعار دائن {credit_sale.order_number}')
        return redirect('sales:detail', pk=credit_sale.pk)
    
    return redirect('sales:detail', pk=pk)


@login_required
def debit_note(request, pk):
    """إنشاء إشعار مدين (رسوم إضافية)"""
    
    sale = get_object_or_404(Sale, pk=pk)
    
    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount', 0))
        reason = request.POST.get('reason', '')
        
        # إنشاء فاتورة رسوم
        debit_sale = Sale.objects.create(
            order_number=f'DN-{sale.order_number}',
            customer=sale.customer,
            status='completed',
            notes=f'إشعار مدين للفاتورة {sale.order_number}: {reason}',
            subtotal=amount,
            tax=amount * Decimal('0.15'),
            payment_method=sale.payment_method,
            created_by=request.user.username if request.user.is_authenticated else 'System'
        )
        
        messages.success(request, f'تم إنشاء إشعار مدين {debit_sale.order_number}')
        return redirect('sales:detail', pk=debit_sale.pk)
    
    return redirect('sales:detail', pk=pk)

# استبدل دالة print_eye_exam في sales/views.py بهذا الكود المحسّن

from django.http import HttpResponse
from django.template.loader import render_to_string
from customers.models import EyeExam  # إذا EyeExam فعلاً هنا
from customers.models import Customer, EyeExam
from settings.models import CompanySettings
# --- PDF Eye Exam Print (Safe for Railway) ---
# Place this near the bottom of sales/views.py (or anywhere in the file).
# IMPORTANT:
# 1) Do NOT keep "from weasyprint import HTML" at module level.
# 2) Ensure EyeExam import path is correct for your project.

from django.template.loader import render_to_string

@login_required
def print_eye_exam(request, invoice_id):
    """طباعة فحص العين للعميل المرتبط بالفاتورة (PDF عند توفر WeasyPrint)"""

    # 1) الحصول على الفاتورة
    sale = get_object_or_404(Sale, pk=invoice_id)
    customer = sale.customer

    if not customer:
        messages.error(request, 'هذه الفاتورة غير مرتبطة بعميل')
        return redirect('sales:detail', pk=invoice_id)

    # 2) جلب آخر فحص للعميل
    # عدّل مسار EyeExam إذا كان في تطبيق آخر
    try:
        from customers.models import EyeExam
    except Exception:
        # إذا EyeExam غير موجود أو في تطبيق آخر، لا نكسر النظام
        messages.error(request, 'نموذج فحص العين (EyeExam) غير متوفر أو مساره غير صحيح')
        return redirect('sales:detail', pk=invoice_id)

    # إذا كان عندك related_name مختلف عدله هنا
    # الافتراضي: customer.eye_exams.first()
    eye_exam = getattr(customer, "eye_exams", None)
    eye_exam = eye_exam.first() if eye_exam is not None else None

    if not eye_exam:
        messages.error(request, 'لا يوجد فحص عين مسجل لهذا العميل')
        return redirect('sales:detail', pk=invoice_id)

    # 3) إعداد بيانات الشركة (مع قيم افتراضية)
    try:
        company_settings = CompanySettings.get_settings()
        company_data = {
            'company_name': company_settings.company_name_ar or 'محل النظارات الحديثة',
            'company_name_en': company_settings.company_name_en or 'Modern Optics',
            'phone': company_settings.contact_phone or '0500000000',
            'email': company_settings.contact_email or 'info@optics.sa',
            'address': company_settings.national_address or 'المدينة المنورة، المملكة العربية السعودية',
            'tax_number': company_settings.tax_number or '300000000000003',
            'commercial_register': company_settings.commercial_register or '1010000000',
            'unified_number': company_settings.unified_number or '7000000000',
            'location_url': company_settings.location_url or '',
            'logo': company_settings.logo.url if getattr(company_settings, "logo", None) else None,
            'owner_name': company_settings.owner_name or 'المدير العام',
        }
    except Exception:
        company_data = {
            'company_name': 'محل النظارات الحديثة',
            'company_name_en': 'Modern Optics',
            'phone': '0500000000',
            'email': 'info@optics.sa',
            'address': 'المدينة المنورة، المملكة العربية السعودية',
            'tax_number': '300000000000003',
            'commercial_register': '1010000000',
            'unified_number': '7000000000',
            'location_url': '',
            'logo': None,
            'owner_name': 'المدير العام',
        }

    # 4) إعداد السياق للقالب
    context = {
        'customer': customer,
        'eye_exam': eye_exam,
        'invoice': sale,
        'print_date': timezone.now(),
        'company': company_data,

        # للتوافق مع قوالب قديمة
        'company_name': company_data['company_name'],
        'company_phone': company_data['phone'],
        'company_address': company_data['address'],
    }

    # 5) HTML من القالب
    html_string = render_to_string('sales/eye_exam_print.html', context)

    # 6) تحويل إلى PDF (Lazy import لتجنب كسر تشغيل السيرفر على Railway)
    try:
        from weasyprint import HTML
    except Exception:
        # خيار 1: رجّع HTML بدل PDF (مفيد للطباعة من المتصفح)
        # return HttpResponse(html_string)

        # خيار 2: رسالة واضحة
        return HttpResponse(
            "PDF generation is temporarily unavailable on the server (WeasyPrint dependencies missing).",
            status=503
        )

    pdf = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()

    # 7) إرجاع PDF
    filename = f"eye_exam_{getattr(customer, 'customer_id', customer.pk)}.pdf"
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response
