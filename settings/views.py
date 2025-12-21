from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CompanySettings, PaymentMethod, Attachment

@login_required
def settings_index(request):
    """صفحة الإعدادات الرئيسية"""
    
    # الحصول على إعدادات المؤسسة (أو إنشاءها)
    company_settings = CompanySettings.get_settings()
    
    # الحصول على طرق الدفع
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    
    # الحصول على المرفقات
    attachments = Attachment.objects.all()
    
    context = {
        'company_settings': company_settings,
        'payment_methods': payment_methods,
        'attachments': attachments,
    }
    
    return render(request, 'settings/settings_index.html', context)


@login_required
def update_company_settings(request):
    """تحديث إعدادات المؤسسة"""
    
    if request.method == 'POST':
        settings = CompanySettings.get_settings()
        
        # بيانات المؤسسة
        settings.company_name_ar = request.POST.get('company_name_ar', '')
        settings.company_name_en = request.POST.get('company_name_en', '')
        settings.unified_number = request.POST.get('unified_number', '')
        settings.commercial_register = request.POST.get('commercial_register', '')
        settings.tax_number = request.POST.get('tax_number', '')
        settings.national_address = request.POST.get('national_address', '')
        settings.location_url = request.POST.get('location_url', '')
        
        # رفع الشعار
        if request.FILES.get('logo'):
            settings.logo = request.FILES['logo']
        
        # بيانات التواصل
        settings.contact_phone = request.POST.get('contact_phone', '')
        settings.contact_email = request.POST.get('contact_email', '')
        
        # بيانات المفوض
        settings.owner_name = request.POST.get('owner_name', '')
        settings.owner_id_number = request.POST.get('owner_id_number', '')
        settings.owner_phone = request.POST.get('owner_phone', '')
        settings.owner_email = request.POST.get('owner_email', '')
        
        try:
            settings.save()
            messages.success(request, 'تم حفظ إعدادات المؤسسة بنجاح')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
    
    return redirect('settings:index')


@login_required
def add_payment_method(request):
    """إضافة طريقة دفع"""
    
    if request.method == 'POST':
        name = request.POST.get('payment_name')
        company = request.POST.get('payment_company', '')
        percentage = request.POST.get('payment_percentage', None)
        
        try:
            PaymentMethod.objects.create(
                name=name,
                company=company,
                percentage=percentage if percentage else None
            )
            messages.success(request, 'تم إضافة طريقة الدفع بنجاح')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
    
    return redirect('settings:index')


@login_required
def delete_payment_method(request, pk):
    """حذف طريقة دفع"""
    
    if request.method == 'POST':
        payment_method = get_object_or_404(PaymentMethod, pk=pk)
        payment_method.delete()
        messages.success(request, 'تم حذف طريقة الدفع بنجاح')
    
    return redirect('settings:index')


@login_required
def edit_payment_method(request, pk):
    """تعديل طريقة دفع"""
    
    payment_method = get_object_or_404(PaymentMethod, pk=pk)
    
    if request.method == 'POST':
        payment_method.name = request.POST.get('payment_name')
        payment_method.company = request.POST.get('payment_company', '')
        percentage = request.POST.get('payment_percentage', None)
        payment_method.percentage = percentage if percentage else None
        
        try:
            payment_method.save()
            messages.success(request, 'تم تحديث طريقة الدفع بنجاح')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
    
    return redirect('settings:index')


@login_required
def add_attachment(request):
    """إضافة مرفق"""
    
    if request.method == 'POST':
        name = request.POST.get('attachment_name')
        description = request.POST.get('attachment_description', '')
        file = request.FILES.get('attachment_file')
        
        if not file:
            messages.error(request, 'يرجى اختيار ملف')
            return redirect('settings:index')
        
        # التحقق من نوع الملف
        if not file.name.endswith('.pdf'):
            messages.error(request, 'يجب أن يكون الملف بصيغة PDF')
            return redirect('settings:index')
        
        try:
            Attachment.objects.create(
                name=name,
                file=file,
                description=description
            )
            messages.success(request, 'تم إضافة المرفق بنجاح')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
    
    return redirect('settings:index')


@login_required
def delete_attachment(request, pk):
    """حذف مرفق"""
    
    if request.method == 'POST':
        attachment = get_object_or_404(Attachment, pk=pk)
        
        # حذف الملف من الخادم
        if attachment.file:
            attachment.file.delete()
        
        attachment.delete()
        messages.success(request, 'تم حذف المرفق بنجاح')
    
    return redirect('settings:index')


@login_required
def edit_attachment(request, pk):
    """تعديل مرفق"""
    
    attachment = get_object_or_404(Attachment, pk=pk)
    
    if request.method == 'POST':
        attachment.name = request.POST.get('attachment_name')
        attachment.description = request.POST.get('attachment_description', '')
        
        # تحديث الملف إذا تم رفع ملف جديد
        if request.FILES.get('attachment_file'):
            # حذف الملف القديم
            if attachment.file:
                attachment.file.delete()
            
            file = request.FILES['attachment_file']
            
            # التحقق من نوع الملف
            if not file.name.endswith('.pdf'):
                messages.error(request, 'يجب أن يكون الملف بصيغة PDF')
                return redirect('settings:index')
            
            attachment.file = file
        
        try:
            attachment.save()
            messages.success(request, 'تم تحديث المرفق بنجاح')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
    
    return redirect('settings:index')