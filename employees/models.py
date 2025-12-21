from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.utils import timezone
from django.core.validators import RegexValidator


class EmployeeProfile(models.Model):
    """ملف تعريف الموظف"""
    
    POSITION_CHOICES = [
        ('manager', 'مدير'),
        ('accountant', 'محاسب'),
        ('sales', 'موظف مبيعات'),
        ('inventory', 'أمين مخزن'),
        ('technician', 'فني'),
        ('cashier', 'كاشير'),
        ('other', 'أخرى'),
    ]
    
    GENDER_CHOICES = [
        ('male', 'ذكر'),
        ('female', 'أنثى'),
    ]
    
    # ربط بمستخدم Django
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    
    # معلومات شخصية
    employee_id = models.CharField('رقم الموظف', max_length=20, unique=True)
    full_name_arabic = models.CharField('الاسم الكامل بالعربي', max_length=200)
    position = models.CharField('المسمى الوظيفي', max_length=50, choices=POSITION_CHOICES)
    gender = models.CharField('الجنس', max_length=10, choices=GENDER_CHOICES, default='male')
    
    # معلومات الاتصال
    phone_regex = RegexValidator(
        regex=r'^05\d{8}$',
        message="رقم الجوال يجب أن يبدأ بـ 05 ويتكون من 10 أرقام"
    )
    phone = models.CharField('رقم الجوال', validators=[phone_regex], max_length=10)
    national_id = models.CharField('رقم الهوية الوطنية', max_length=10, blank=True)
    
    # صورة الموظف
    photo = models.ImageField('صورة الموظف', upload_to='employees/photos/', blank=True, null=True)
    
    # معلومات العمل
    hire_date = models.DateField('تاريخ التوظيف', default=timezone.now)
    department = models.CharField('القسم', max_length=100, blank=True)
    salary = models.DecimalField('الراتب', max_digits=10, decimal_places=2, default=0)
    
    # الحالة
    is_active = models.BooleanField('نشط', default=True)
    termination_date = models.DateField('تاريخ إنهاء الخدمة', null=True, blank=True)
    termination_reason = models.TextField('سبب إنهاء الخدمة', blank=True)
    
    # معلومات إضافية
    address = models.TextField('العنوان', blank=True)
    notes = models.TextField('ملاحظات', blank=True)
    
    # تواريخ النظام
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        verbose_name = 'موظف'
        verbose_name_plural = 'الموظفين'
        ordering = ['-created_at']
        permissions = [
            ('view_salary', 'يمكنه عرض الرواتب'),
            ('manage_employees', 'يمكنه إدارة الموظفين'),
        ]
    
    def __str__(self):
        return f"{self.employee_id} - {self.full_name_arabic}"
    
    def get_photo_url(self):
        """الحصول على رابط الصورة أو الافتراضية"""
        if self.photo:
            return self.photo.url
        # صورة افتراضية حسب الجنس
        if self.gender == 'female':
            return '/static/images/default-avatar-female.png'
        return '/static/images/default-avatar-male.png'
    
    def is_online(self):
        """التحقق من حالة الاتصال"""
        if not self.user.is_active:
            return False
        
        # التحقق من آخر نشاط (إذا كان لديك نظام تتبع الجلسات)
        try:
            from django.contrib.sessions.models import Session
            from django.utils import timezone
            
            sessions = Session.objects.filter(expire_date__gte=timezone.now())
            for session in sessions:
                data = session.get_decoded()
                if data.get('_auth_user_id') == str(self.user.id):
                    return True
        except:
            pass
        
        return False
    
    def deactivate(self, reason=''):
        """إيقاف الموظف"""
        self.is_active = False
        self.user.is_active = False
        self.termination_date = timezone.now().date()
        self.termination_reason = reason
        self.save()
        self.user.save()
    
    def activate(self):
        """تفعيل الموظف"""
        self.is_active = True
        self.user.is_active = True
        self.termination_date = None
        self.termination_reason = ''
        self.save()
        self.user.save()


class EmployeeGroup(models.Model):
    """مجموعات الموظفين مع الصلاحيات"""
    
    name = models.CharField('اسم المجموعة', max_length=100, unique=True)
    name_arabic = models.CharField('الاسم بالعربي', max_length=100)
    description = models.TextField('الوصف', blank=True)
    
    # الصلاحيات
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='employee_group')
    
    # صلاحيات مخصصة
    can_view_reports = models.BooleanField('عرض التقارير', default=False)
    can_manage_sales = models.BooleanField('إدارة المبيعات', default=False)
    can_manage_inventory = models.BooleanField('إدارة المخزون', default=False)
    can_manage_customers = models.BooleanField('إدارة العملاء', default=False)
    can_manage_suppliers = models.BooleanField('إدارة الموردين', default=False)
    can_view_financial = models.BooleanField('عرض البيانات المالية', default=False)
    can_manage_settings = models.BooleanField('إدارة الإعدادات', default=False)
    
    # تواريخ
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        verbose_name = 'مجموعة موظفين'
        verbose_name_plural = 'مجموعات الموظفين'
        ordering = ['name']
    
    def __str__(self):
        return self.name_arabic
    
    def get_employees_count(self):
        """عدد الموظفين في المجموعة"""
        return self.group.user_set.count()


class EmployeeAttendance(models.Model):
    """سجل الحضور"""
    
    ATTENDANCE_TYPE = [
        ('in', 'حضور'),
        ('out', 'انصراف'),
    ]
    
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField('التاريخ', default=timezone.now)
    time = models.TimeField('الوقت', default=timezone.now)
    type = models.CharField('النوع', max_length=10, choices=ATTENDANCE_TYPE)
    notes = models.TextField('ملاحظات', blank=True)
    
    created_at = models.DateTimeField('تاريخ التسجيل', auto_now_add=True)
    
    class Meta:
        verbose_name = 'سجل حضور'
        verbose_name_plural = 'سجلات الحضور'
        ordering = ['-date', '-time']
    
    def __str__(self):
        return f"{self.employee.full_name_arabic} - {self.date} - {self.get_type_display()}"


class EmployeeActivity(models.Model):
    """سجل نشاطات الموظف"""
    
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField('الإجراء', max_length=200)
    description = models.TextField('الوصف', blank=True)
    ip_address = models.GenericIPAddressField('عنوان IP', null=True, blank=True)
    
    created_at = models.DateTimeField('التاريخ', auto_now_add=True)
    
    class Meta:
        verbose_name = 'نشاط موظف'
        verbose_name_plural = 'نشاطات الموظفين'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.employee.full_name_arabic} - {self.action}"