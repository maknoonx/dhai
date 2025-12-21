from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime

from .models import EmployeeProfile, EmployeeGroup, EmployeeAttendance, EmployeeActivity
from .forms import EmployeeForm, EmployeeGroupForm


@login_required
def employee_list(request):
    """قائمة الموظفين"""
    
    # الفلترة
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    position = request.GET.get('position', '')
    group_id = request.GET.get('group', '')
    
    employees = EmployeeProfile.objects.select_related('user').all()
    
    if search:
        employees = employees.filter(
            Q(full_name_arabic__icontains=search) |
            Q(employee_id__icontains=search) |
            Q(phone__icontains=search) |
            Q(user__email__icontains=search)
        )
    
    if status == 'active':
        employees = employees.filter(is_active=True)
    elif status == 'inactive':
        employees = employees.filter(is_active=False)
    
    if position:
        employees = employees.filter(position=position)
    
    if group_id:
        employees = employees.filter(user__groups__id=group_id)
    
    # الإحصائيات
    total_employees = EmployeeProfile.objects.count()
    active_employees = EmployeeProfile.objects.filter(is_active=True).count()
    inactive_employees = total_employees - active_employees
    
    # الموظفين المتصلين (محاكاة - يمكن تطويرها)
    online_employees = []
    for emp in employees.filter(is_active=True)[:10]:
        if emp.is_online():
            online_employees.append(emp.id)
    
    groups = EmployeeGroup.objects.all()
    
    context = {
        'employees': employees,
        'total_employees': total_employees,
        'active_employees': active_employees,
        'inactive_employees': inactive_employees,
        'online_count': len(online_employees),
        'online_employees': online_employees,
        'groups': groups,
        'search': search,
        'status': status,
        'position': position,
        'selected_group': group_id,
        'position_choices': EmployeeProfile.POSITION_CHOICES,
    }
    
    return render(request, 'employees/employee_list.html', context)


@login_required
@permission_required('employees.add_employeeprofile', raise_exception=True)
def employee_add(request):
    """إضافة موظف جديد"""
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            # إنشاء مستخدم Django
            user = User.objects.create_user(
                username=form.cleaned_data['email'].split('@')[0],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['full_name_arabic'].split()[0],
                is_staff=True,
                is_active=True
            )
            
            # إنشاء ملف الموظف
            employee = form.save(commit=False)
            employee.user = user
            employee.save()
            
            # إضافة إلى المجموعات
            if form.cleaned_data.get('groups'):
                user.groups.set(form.cleaned_data['groups'])
            
            # تسجيل النشاط
            EmployeeActivity.objects.create(
                employee=employee,
                action='تم إنشاء حساب جديد',
                description=f'تم إنشاء حساب للموظف {employee.full_name_arabic}',
                ip_address=get_client_ip(request)
            )
            
            messages.success(request, f'تم إضافة الموظف {employee.full_name_arabic} بنجاح')
            return redirect('employees:list')
    else:
        form = EmployeeForm()
    
    context = {
        'form': form,
        'groups': EmployeeGroup.objects.all(),
    }
    
    return render(request, 'employees/employee_form.html', context)


@login_required
def employee_detail(request, pk):
    """تفاصيل الموظف"""
    
    employee = get_object_or_404(EmployeeProfile, pk=pk)
    
    # آخر النشاطات
    recent_activities = employee.activities.all()[:10]
    
    # سجل الحضور (آخر 30 يوم)
    attendance_records = employee.attendance_records.filter(
        date__gte=timezone.now().date() - timezone.timedelta(days=30)
    )
    
    context = {
        'employee': employee,
        'recent_activities': recent_activities,
        'attendance_records': attendance_records,
        'is_online': employee.is_online(),
    }
    
    return render(request, 'employees/employee_detail.html', context)


@login_required
@permission_required('employees.change_employeeprofile', raise_exception=True)
def employee_edit(request, pk):
    """تعديل موظف"""
    
    employee = get_object_or_404(EmployeeProfile, pk=pk)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            employee = form.save()
            
            # تحديث البريد الإلكتروني
            if form.cleaned_data.get('email'):
                employee.user.email = form.cleaned_data['email']
                employee.user.save()
            
            # تحديث المجموعات
            if form.cleaned_data.get('groups'):
                employee.user.groups.set(form.cleaned_data['groups'])
            
            # تحديث كلمة المرور إذا تم إدخالها
            if form.cleaned_data.get('password'):
                employee.user.set_password(form.cleaned_data['password'])
                employee.user.save()
            
            messages.success(request, 'تم تحديث بيانات الموظف بنجاح')
            return redirect('employees:detail', pk=employee.pk)
    else:
        form = EmployeeForm(instance=employee)
        # ملء البيانات الحالية
        form.initial['email'] = employee.user.email
        form.initial['groups'] = employee.user.groups.all()
    
    context = {
        'form': form,
        'employee': employee,
        'groups': EmployeeGroup.objects.all(),
    }
    
    return render(request, 'employees/employee_form.html', context)


@login_required
@permission_required('employees.delete_employeeprofile', raise_exception=True)
def employee_toggle_active(request, pk):
    """تفعيل/إيقاف الموظف"""
    
    employee = get_object_or_404(EmployeeProfile, pk=pk)
    
    if request.method == 'POST':
        if employee.is_active:
            reason = request.POST.get('reason', '')
            employee.deactivate(reason)
            messages.warning(request, f'تم إيقاف الموظف {employee.full_name_arabic}')
        else:
            employee.activate()
            messages.success(request, f'تم تفعيل الموظف {employee.full_name_arabic}')
        
        return redirect('employees:list')
    
    return redirect('employees:detail', pk=pk)


# ============== Employee Groups ==============

@login_required
def group_list(request):
    """قائمة المجموعات"""
    
    groups = EmployeeGroup.objects.annotate(
        employees_count=Count('group__user')
    ).all()
    
    context = {
        'groups': groups,
    }
    
    return render(request, 'employees/group_list.html', context)


@login_required
@permission_required('auth.add_group', raise_exception=True)
def group_add(request):
    """إضافة مجموعة جديدة"""
    
    if request.method == 'POST':
        form = EmployeeGroupForm(request.POST)
        if form.is_valid():
            # إنشاء مجموعة Django
            django_group = Group.objects.create(
                name=form.cleaned_data['name']
            )
            
            # إنشاء مجموعة الموظفين
            employee_group = form.save(commit=False)
            employee_group.group = django_group
            employee_group.save()
            
            # إضافة الصلاحيات
            form.save_permissions(employee_group)
            
            messages.success(request, f'تم إنشاء المجموعة {employee_group.name_arabic} بنجاح')
            return redirect('employees:group_list')
    else:
        form = EmployeeGroupForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'employees/group_form.html', context)


@login_required
def group_detail(request, pk):
    """تفاصيل المجموعة"""
    
    group = get_object_or_404(EmployeeGroup, pk=pk)
    employees = EmployeeProfile.objects.filter(user__groups=group.group)
    
    context = {
        'group': group,
        'employees': employees,
    }
    
    return render(request, 'employees/group_detail.html', context)


@login_required
@permission_required('auth.change_group', raise_exception=True)
def group_edit(request, pk):
    """تعديل مجموعة"""
    
    employee_group = get_object_or_404(EmployeeGroup, pk=pk)
    
    if request.method == 'POST':
        form = EmployeeGroupForm(request.POST, instance=employee_group)
        if form.is_valid():
            employee_group = form.save()
            
            # تحديث اسم المجموعة
            employee_group.group.name = form.cleaned_data['name']
            employee_group.group.save()
            
            # تحديث الصلاحيات
            form.save_permissions(employee_group)
            
            messages.success(request, 'تم تحديث المجموعة بنجاح')
            return redirect('employees:group_detail', pk=employee_group.pk)
    else:
        form = EmployeeGroupForm(instance=employee_group)
    
    context = {
        'form': form,
        'group': employee_group,
    }
    
    return render(request, 'employees/group_form.html', context)


@login_required
@permission_required('auth.delete_group', raise_exception=True)
def group_delete(request, pk):
    """حذف مجموعة"""
    
    employee_group = get_object_or_404(EmployeeGroup, pk=pk)
    
    if request.method == 'POST':
        group_name = employee_group.name_arabic
        employee_group.group.delete()  # سيحذف EmployeeGroup تلقائياً
        
        messages.success(request, f'تم حذف المجموعة {group_name}')
        return redirect('employees:group_list')
    
    return redirect('employees:group_detail', pk=pk)


# ============== Utility Functions ==============

def get_client_ip(request):
    """الحصول على IP الخاص بالعميل"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip