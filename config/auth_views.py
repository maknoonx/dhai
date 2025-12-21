# في config/auth_views.py
# أنشئ ملف جديد للـ authentication views

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from settings.models import CompanySettings


def login_view(request):
    """صفحة تسجيل الدخول"""
    
    # إذا كان المستخدم مسجل دخول بالفعل، أعد توجيهه للصفحة الرئيسية
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # الحصول على إعدادات الشركة
    try:
        company = CompanySettings.get_settings()
        company_name = company.company_name_ar or 'نظام إدارة المحلات'
        company_logo = company.logo.url if company.logo else None
    except:
        company_name = 'نظام إدارة المحلات'
        company_logo = None
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')
        
        # محاولة تسجيل الدخول
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # تسجيل دخول ناجح
            auth_login(request, user)
            
            # إدارة "تذكرني"
            if not remember:
                # إذا لم يتم تفعيل "تذكرني"، انتهي الجلسة عند إغلاق المتصفح
                request.session.set_expiry(0)
            else:
                # إذا تم تفعيل "تذكرني"، اجعل الجلسة تستمر لمدة أسبوعين
                request.session.set_expiry(1209600)  # أسبوعين بالثواني
            
            messages.success(request, f'مرحباً {user.get_full_name() or user.username}!')
            
            # إعادة التوجيه إلى الصفحة المطلوبة أو الصفحة الرئيسية
            next_page = request.GET.get('next', 'dashboard')
            return redirect(next_page)
        else:
            # فشل تسجيل الدخول
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة')
    
    context = {
        'company_name': company_name,
        'company_logo': company_logo,
    }
    
    return render(request, 'auth/login.html', context)


@login_required
def logout_view(request):
    """تسجيل الخروج"""
    
    user_name = request.user.get_full_name() or request.user.username
    
    # تسجيل الخروج
    auth_logout(request)
    
    messages.success(request, f'تم تسجيل خروج {user_name} بنجاح')
    
    return redirect('login')