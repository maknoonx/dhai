from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count, F
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
import json

from .models import Sale, SaleItem, Payment, Service
from customers.models import Customer, EyeExam
from stock.models import Product, Laboratory
from settings.models import CompanySettings
from whatsapp.service import whatsapp


def _build_sale_print_context(sale):
    """يبني سياق قالب طباعة الفاتورة (مستخدم في الطباعة وفي توليد PDF)."""
    import base64
    from io import BytesIO
    import qrcode

    items = sale.items.select_related('product').all()
    company_settings = CompanySettings.get_settings()

    latest_exam = None
    if sale.customer:
        try:
            latest_exam = sale.customer.eye_exams.first()
        except Exception:
            latest_exam = None

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

    return {
        'sale': sale,
        'items': items,
        'company': company_settings,
        'qr_code': qr_code_base64,
        'latest_exam': latest_exam,
    }


def _render_invoice_pdf(request, sale) -> bytes:
    """يولّد الفاتورة كملف PDF (bytes) من نفس قالب الطباعة عبر WeasyPrint."""
    from django.template.loader import render_to_string
    from weasyprint import HTML

    context = _build_sale_print_context(sale)
    html_string = render_to_string('sales/sale_print.html', context)
    base_url = request.build_absolute_uri('/') if request else None
    return HTML(string=html_string, base_url=base_url).write_pdf()


def _send_invoice_whatsapp(request, sale) -> bool:
    """يرسل فاتورة PDF للعميل عبر واتساب مع ملاحظة. يُرجع True عند النجاح."""
    customer = sale.customer
    if not customer or not customer.phone or not customer.notify_whatsapp:
        return False

    caption = (
        f"مرحباً {customer.name}،\n"
        f"مرفق فاتورتكم رقم {sale.order_number} من بصريات ضي.\n"
        f"الإجمالي: {sale.total_amount} ر.س\n\n"
        f"سيتم التواصل معكم عند استلام النظارة. شكراً لزيارتكم 🌟"
    )
    try:
        # نرسل الفاتورة عبر رابط يجلبه Evolution (أكثر موثوقية من base64)
        token = getattr(settings, 'EVOLUTION_WEBHOOK_TOKEN', '')
        site = getattr(settings, 'SITE_URL', '').rstrip('/')
        pdf_url = f"{site}/sales/{sale.pk}/invoice.pdf"
        if token:
            pdf_url += f"?token={token}"
        result = whatsapp.send_document_url(
            customer.phone,
            pdf_url,
            filename=f'{sale.order_number}.pdf',
            caption=caption,
        )
        if isinstance(result, dict) and not result.get('error'):
            sale.invoice_sent_at = timezone.now()
            sale.save(update_fields=['invoice_sent_at'])
            return True
    except Exception as e:
        # لا نوقف إنشاء الفاتورة إذا فشل الإرسال — نسجّل الخطأ فقط
        print(f"WhatsApp invoice send failed for {sale.order_number}: {e}")
    return False


def invoice_pdf(request, pk):
    """
    يعيد الفاتورة كملف PDF بدون تسجيل دخول (محمي بـ token)،
    ليتمكّن Evolution من جلبه وإرساله للعميل عبر واتساب.
    """
    expected = getattr(settings, 'EVOLUTION_WEBHOOK_TOKEN', '')
    if expected and request.GET.get('token') != expected:
        return HttpResponse('Forbidden', status=403)

    sale = get_object_or_404(
        Sale.objects.select_related('customer', 'laboratory'), pk=pk
    )
    pdf_bytes = _render_invoice_pdf(request, sale)
    resp = HttpResponse(pdf_bytes, content_type='application/pdf')
    resp['Content-Disposition'] = f'inline; filename="{sale.order_number}.pdf"'
    return resp


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
                paid_amount=0,
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
                    unit_price=unit_price
                )
                
                subtotal += sale_item.total_price
                
                # تحديث المخزون
                product.quantity -= quantity
                product.save()
            
            # الخدمات
            services_data = json.loads(request.POST.get('services', '[]'))
            for service_data in services_data:
                # إذا كانت الخدمة من قائمة الخدمات المحفوظة
                if 'service_id' in service_data:
                    try:
                        service = Service.objects.get(pk=service_data['service_id'])
                        service_name = service.service_name
                        service_price = Decimal(service_data['price'])
                        quantity = int(service_data.get('quantity', 1))
                    except Service.DoesNotExist:
                        continue
                else:
                    # خدمة مخصصة
                    service_name = service_data['name']
                    service_price = Decimal(service_data['price'])
                    quantity = int(service_data.get('quantity', 1))
                
                # إنشاء عنصر خدمة
                SaleItem.objects.create(
                    sale=sale,
                    product=None,
                    quantity=quantity,
                    unit_price=service_price,
                    service_name=service_name
                )
                
                subtotal += (service_price * quantity)
            
            # حساب الضريبة (0% - صفرية)
            # الضريبة موجودة في الحقل ولكن قيمتها صفر
            tax = Decimal('0')
            
            # تحديث الفاتورة
            sale.subtotal = subtotal
            sale.tax = tax  # ضريبة صفرية
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
            
            # إرسال الفاتورة للعميل عبر واتساب (الخيار مفعّل تلقائياً، ويمكن إلغاؤه في الفورم)
            send_invoice = request.POST.get('send_invoice') == 'on'
            if send_invoice:
                sent = _send_invoice_whatsapp(request, sale)
                if sent:
                    messages.success(request, f'تم إنشاء الفاتورة {order_number} وإرسالها للعميل عبر واتساب ✅')
                else:
                    messages.warning(
                        request,
                        f'تم إنشاء الفاتورة {order_number}، لكن تعذّر إرسالها عبر واتساب '
                        f'(تحقق من رقم العميل وإعدادات Evolution).'
                    )
            else:
                messages.success(request, f'تم إنشاء الفاتورة {order_number} بنجاح')

            return redirect('sales:detail', pk=sale.pk)
            
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
            return redirect('sales:add')
    
    # GET request
    customers = Customer.objects.all().order_by('name')
    products = Product.objects.filter(is_active=True).select_related('category')
    laboratories = Laboratory.objects.filter(is_active=True)
    services = Service.objects.filter(is_active=True).order_by('service_name')
    
    context = {
        'customers': customers,
        'products': products,
        'laboratories': laboratories,
        'services': services,
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
    """طباعة الفاتورة مع تفاصيل فحص النظر"""

    sale = get_object_or_404(Sale.objects.select_related('customer', 'laboratory'), pk=pk)
    context = _build_sale_print_context(sale)
    return render(request, 'sales/sale_print.html', context)


@login_required
def notify_arrival(request, pk):
    """إشعار العميل بوصول النظارة وسؤاله: استلام من المحل (1) أم توصيل (2)."""
    sale = get_object_or_404(Sale.objects.select_related('customer'), pk=pk)

    if request.method != 'POST':
        return redirect('sales:detail', pk=sale.pk)

    customer = sale.customer
    if not customer or not customer.phone:
        messages.error(request, 'لا يوجد رقم جوال لهذا العميل.')
        return redirect('sales:detail', pk=sale.pk)

    body = (
        f"مرحباً {customer.name} 👋\n"
        f"يسعدنا إبلاغكم بوصول نظارتكم الخاصة بالطلب رقم {sale.order_number} إلى بصريات ضي.\n\n"
        f"هل تودون الاستلام من المحل أم التوصيل؟\n"
        f"↩️ ردّوا بـ *1* للاستلام من المحل\n"
        f"↩️ ردّوا بـ *2* للتوصيل\n\n"
        f"شكراً لكم 🌟"
    )

    result = whatsapp.send_text(customer.phone, body)
    if isinstance(result, dict) and not result.get('error'):
        sale.arrival_notified_at = timezone.now()
        # لا نغيّر الحالة إن كانت أبعد من "جاهز"
        if sale.status in ('created', 'lab'):
            sale.status = 'ready'
        sale.save(update_fields=['arrival_notified_at', 'status', 'updated_at'])
        messages.success(request, 'تم إرسال إشعار وصول النظارة للعميل عبر واتساب ✅')
    else:
        messages.error(
            request,
            'تعذّر إرسال الإشعار عبر واتساب (تحقق من رقم العميل وإعدادات Evolution).'
        )

    return redirect('sales:detail', pk=sale.pk)



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
            tax=Decimal('0'),  # ضريبة صفرية
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
            tax=Decimal('0'),  # ضريبة صفرية
            payment_method=sale.payment_method,
            created_by=request.user.username if request.user.is_authenticated else 'System'
        )
        
        messages.success(request, f'تم إنشاء إشعار مدين {debit_sale.order_number}')
        return redirect('sales:detail', pk=debit_sale.pk)
    
    return redirect('sales:detail', pk=pk)


@login_required
def print_eye_exam(request, invoice_id):
    """طباعة فحص العين للعميل المرتبط بالفاتورة (HTML للطباعة من المتصفح)"""

    # 1) الحصول على الفاتورة
    sale = get_object_or_404(Sale, pk=invoice_id)
    customer = sale.customer

    if not customer:
        messages.error(request, 'هذه الفاتورة غير مرتبطة بعميل')
        return redirect('sales:detail', pk=invoice_id)

    # 2) جلب آخر فحص للعميل
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

    # 5) إرجاع HTML مباشرة للطباعة من المتصفح
    return render(request, 'sales/eye_exam_print.html', context)


# ============== إدارة الخدمات ==============

@login_required
def service_list(request):
    """عرض قائمة الخدمات"""
    
    # البحث
    search_query = request.GET.get('search', '')
    
    services = Service.objects.all()
    
    if search_query:
        services = services.filter(
            Q(service_code__icontains=search_query) |
            Q(service_name__icontains=search_query)
        )
    
    services = services.order_by('service_name')
    
    # الإحصائيات
    total_services = services.count()
    active_services = services.filter(is_active=True).count()
    
    context = {
        'services': services,
        'search_query': search_query,
        'total_services': total_services,
        'active_services': active_services,
    }
    
    return render(request, 'sales/service_list.html', context)


@login_required
def service_add(request):
    """إضافة خدمة جديدة"""
    
    if request.method == 'POST':
        try:
            service_name = request.POST.get('service_name')
            cost = request.POST.get('cost') or None
            price = request.POST.get('price')
            description = request.POST.get('description', '')
            
            # توليد رمز الخدمة
            last_service = Service.objects.order_by('-id').first()
            if last_service and last_service.service_code:
                try:
                    last_number = int(last_service.service_code.split('-')[1])
                    new_number = last_number + 1
                except:
                    new_number = 1
            else:
                new_number = 1
            service_code = f'SRV-{new_number:05d}'
            
            # إنشاء الخدمة
            service = Service.objects.create(
                service_code=service_code,
                service_name=service_name,
                cost=cost,
                price=price,
                description=description,
                created_by=request.user.username if request.user.is_authenticated else 'System'
            )
            
            messages.success(request, f'تم إضافة الخدمة {service_code} بنجاح')
            return redirect('sales:service_list')
            
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
    
    return render(request, 'sales/service_add.html')


@login_required
def service_edit(request, pk):
    """تعديل خدمة"""
    
    service = get_object_or_404(Service, pk=pk)
    
    if request.method == 'POST':
        try:
            service.service_name = request.POST.get('service_name')
            service.cost = request.POST.get('cost') or None
            service.price = request.POST.get('price')
            service.description = request.POST.get('description', '')
            service.is_active = request.POST.get('is_active') == 'on'
            
            service.save()
            
            messages.success(request, 'تم تحديث الخدمة بنجاح')
            return redirect('sales:service_list')
            
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
    
    context = {
        'service': service,
    }
    
    return render(request, 'sales/service_edit.html', context)


@login_required
def service_delete(request, pk):
    """حذف خدمة"""
    
    service = get_object_or_404(Service, pk=pk)
    
    if request.method == 'POST':
        service_code = service.service_code
        service.delete()
        
        messages.success(request, f'تم حذف الخدمة {service_code} بنجاح')
        return redirect('sales:service_list')
    
    return redirect('sales:service_list')


@login_required
def get_service_info(request, pk):
    """الحصول على معلومات الخدمة (API)"""
    
    service = get_object_or_404(Service, pk=pk)
    
    data = {
        'id': service.id,
        'service_code': service.service_code,
        'service_name': service.service_name,
        'cost': float(service.cost) if service.cost else 0,
        'price': float(service.price),
        'is_active': service.is_active,
    }
    
    return JsonResponse(data)




