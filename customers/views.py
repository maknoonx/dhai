from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Customer, EyeExam, Notification

@login_required
def customers_list(request):
    """صفحة قائمة العملاء"""
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    page = int(request.GET.get('page', 1))
    
    # Base queryset
    customers = Customer.objects.all()
    
    # Apply search filter
    if search_query:
        customers = customers.filter(
            Q(name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(customer_id__icontains=search_query)
        )
    
    # Apply date range filter
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            customers = customers.filter(join_date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            customers = customers.filter(join_date__lte=date_to_obj)
        except ValueError:
            pass
    
    # If no filters, show only last 10
    is_filtering = search_query or date_from or date_to
    if not is_filtering:
        customers = customers[:10]
    
    # Calculate statistics
    all_customers = Customer.objects.all()
    now = timezone.now()
    stats = {
        'total': all_customers.count(),
        'male': all_customers.filter(gender='ذكر').count(),
        'female': all_customers.filter(gender='أنثى').count(),
        'new_this_month': all_customers.filter(
            join_date__year=now.year,
            join_date__month=now.month
        ).count(),
    }
    
    # Pagination
    items_per_page = 10
    total_customers = customers.count()
    total_pages = (total_customers + items_per_page - 1) // items_per_page
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page
    
    paginated_customers = list(customers)[start_index:end_index]
    
    context = {
        'customers': paginated_customers,
        'stats': stats,
        'search_query': search_query,
        'date_from': date_from,
        'date_to': date_to,
        'current_page': page,
        'total_pages': total_pages,
        'total_customers': total_customers,
        'start_index': start_index + 1,
        'end_index': min(end_index, total_customers),
    }
    
    return render(request, 'customers/customers_list.html', context)


@login_required
def customer_add(request):
    """إضافة عميل جديد"""
    
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email', '')
        address = request.POST.get('address', '')
        gender = request.POST.get('gender')
        age = request.POST.get('age', '')
        
        # Validation
        if not name or not phone or not gender:
            messages.error(request, 'الرجاء ملء جميع الحقول المطلوبة')
            return redirect('customers:list')
        
        # Check if phone already exists
        if Customer.objects.filter(phone=phone).exists():
            messages.error(request, 'رقم الجوال مسجل مسبقاً')
            return redirect('customers:list')
        
        # Create customer
        customer = Customer(
            name=name,
            phone=phone,
            email=email if email else None,
            address=address,
            gender=gender,
            age=int(age) if age else None,
        )
        
        try:
            customer.save()
            messages.success(request, f'تم إضافة العميل {name} بنجاح')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
    
    return redirect('customers:list')


@login_required
def customer_edit(request, pk):
    """تعديل بيانات عميل"""
    
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        customer.name = request.POST.get('name')
        customer.phone = request.POST.get('phone')
        customer.email = request.POST.get('email', '') or None
        customer.address = request.POST.get('address', '')
        customer.gender = request.POST.get('gender')
        age = request.POST.get('age', '')
        customer.age = int(age) if age else None
        
        try:
            customer.save()
            messages.success(request, f'تم تحديث بيانات العميل {customer.name} بنجاح')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
    
    return redirect('customers:list')


@login_required
def customer_delete(request, pk):
    """حذف عميل"""
    
    if request.method == 'POST':
        customer = get_object_or_404(Customer, pk=pk)
        customer_name = customer.name
        customer.delete()
        messages.success(request, f'تم حذف العميل {customer_name} بنجاح')
    
    return redirect('customers:list')


@login_required
def customer_profile(request, pk):
    """صفحة ملف العميل"""
    
    customer = get_object_or_404(Customer, pk=pk)
    
    # Get customer's invoices
    try:
        from sales.models import Invoice
        invoices = Invoice.objects.filter(customer=customer).order_by('-date')
        
        # Calculate invoice statistics
        invoice_stats = {
            'total': invoices.aggregate(total=Sum('total_amount'))['total'] or 0,
            'paid': invoices.filter(status='paid').aggregate(total=Sum('total_amount'))['total'] or 0,
            'pending': invoices.filter(status='pending').aggregate(total=Sum('total_amount'))['total'] or 0,
            'count': invoices.count(),
        }
    except:
        invoices = []
        invoice_stats = {
            'total': 0,
            'paid': 0,
            'pending': 0,
            'count': 0,
        }
    
    # Get customer's eye exams
    eye_exams = customer.eye_exams.all()
    latest_exam = eye_exams.first()
    
    # Get notification history
    notifications = customer.notifications.all()[:10]
    
    context = {
        'customer': customer,
        'invoices': invoices,
        'invoice_stats': invoice_stats,
        'eye_exams': eye_exams,
        'latest_exam': latest_exam,
        'notifications': notifications,
    }
    
    return render(request, 'customers/customer_profile.html', context)


@login_required
def customer_notifications_update(request, pk):
    """تحديث إعدادات الإشعارات"""
    
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        customer.notify_whatsapp = request.POST.get('whatsapp') == 'on'
        customer.notify_sms = request.POST.get('sms') == 'on'
        customer.notify_email = request.POST.get('email') == 'on'
        customer.save()
        
        messages.success(request, 'تم حفظ إعدادات الإشعارات بنجاح')
    
    return redirect('customers:profile', pk=pk)


@login_required
def eye_exam_add(request, customer_pk):
    """إضافة فحص نظر"""
    
    customer = get_object_or_404(Customer, pk=customer_pk)
    
    if request.method == 'POST':
        # الحصول على قيمة PD الواحدة وحفظها في كلا العينين
        pd_value = request.POST.get('pd_value', '')
        
        exam = EyeExam(
            customer=customer,
            exam_date=request.POST.get('exam_date', timezone.now().date()),
            # Right eye
            right_sphere=request.POST.get('right_sphere', ''),
            right_cylinder=request.POST.get('right_cylinder', ''),
            right_axis=request.POST.get('right_axis', ''),
            right_add=request.POST.get('right_add', ''),
            right_pd=pd_value,
            # Left eye
            left_sphere=request.POST.get('left_sphere', ''),
            left_cylinder=request.POST.get('left_cylinder', ''),
            left_axis=request.POST.get('left_axis', ''),
            left_add=request.POST.get('left_add', ''),
            left_pd=pd_value,
            # Notes
            notes=request.POST.get('notes', ''),
        )
        
        try:
            exam.save()
            messages.success(request, 'تم إضافة الفحص الطبي بنجاح')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
    
    return redirect('customers:profile', pk=customer_pk)


@login_required
def eye_exam_edit(request, pk):
    """تعديل فحص نظر"""
    
    exam = get_object_or_404(EyeExam, pk=pk)
    
    if request.method == 'POST':
        # الحصول على قيمة PD الواحدة وحفظها في كلا العينين
        pd_value = request.POST.get('pd_value', '')
        
        exam.exam_date = request.POST.get('exam_date', exam.exam_date)
        
        # Right eye
        exam.right_sphere = request.POST.get('right_sphere', '')
        exam.right_cylinder = request.POST.get('right_cylinder', '')
        exam.right_axis = request.POST.get('right_axis', '')
        exam.right_add = request.POST.get('right_add', '')
        exam.right_pd = pd_value
        
        # Left eye
        exam.left_sphere = request.POST.get('left_sphere', '')
        exam.left_cylinder = request.POST.get('left_cylinder', '')
        exam.left_axis = request.POST.get('left_axis', '')
        exam.left_add = request.POST.get('left_add', '')
        exam.left_pd = pd_value
        
        # Notes
        exam.notes = request.POST.get('notes', '')
        
        try:
            exam.save()
            messages.success(request, 'تم تحديث الفحص الطبي بنجاح')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
    
    return redirect('customers:profile', pk=exam.customer.pk)


@login_required
def notification_send(request, customer_pk):
    """إرسال إشعار لعميل"""
    
    customer = get_object_or_404(Customer, pk=customer_pk)
    
    if request.method == 'POST':
        notification_type = request.POST.get('notification_type')
        message_type = request.POST.get('message_type')
        message = request.POST.get('message', '')
        
        notification = Notification(
            customer=customer,
            notification_type=notification_type,
            message_type=message_type,
            message=message,
        )
        
        try:
            notification.save()
            messages.success(request, f'تم إرسال الإشعار عبر {notification.get_notification_type_display()}')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
    
    return redirect('customers:profile', pk=customer_pk)