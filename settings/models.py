from django.db import models
from django.core.validators import RegexValidator, FileExtensionValidator

class CompanySettings(models.Model):
    """إعدادات بيانات المؤسسة"""
    
    # بيانات المؤسسة
    company_name_ar = models.CharField('اسم المؤسسة (عربي)', max_length=200, blank=True)
    company_name_en = models.CharField('اسم المؤسسة (إنجليزي)', max_length=200, blank=True)
    logo = models.ImageField('شعار المؤسسة', upload_to='company/', blank=True, null=True)
    unified_number = models.CharField('الرقم الموحد', max_length=50, blank=True)
    commercial_register = models.CharField('السجل التجاري', max_length=50, blank=True)
    tax_number = models.CharField('الرقم الضريبي', max_length=50, blank=True)
    national_address = models.TextField('العنوان الوطني', blank=True)
    location_url = models.URLField('رابط الموقع', blank=True)
    
    # بيانات التواصل
    phone_regex = RegexValidator(
        regex=r'^\+?966?\d{9,10}$',
        message="رقم الهاتف يجب أن يكون بصيغة: '0501234567' أو '+966501234567'"
    )
    contact_phone = models.CharField(
        'رقم الجوال',
        validators=[phone_regex],
        max_length=17,
        blank=True
    )
    contact_email = models.EmailField('البريد الإلكتروني', blank=True)
    
    # بيانات المفوض/المالك
    owner_name = models.CharField('اسم المفوض/المالك', max_length=200, blank=True)
    owner_id_number = models.CharField('رقم الهوية', max_length=20, blank=True)
    owner_phone = models.CharField(
        'رقم جوال المفوض',
        validators=[phone_regex],
        max_length=17,
        blank=True
    )
    owner_email = models.EmailField('بريد المفوض الإلكتروني', blank=True)
    
    # تواريخ
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        verbose_name = 'إعدادات المؤسسة'
        verbose_name_plural = 'إعدادات المؤسسة'
    
    def __str__(self):
        return self.company_name_ar or 'إعدادات المؤسسة'
    
    @classmethod
    def get_settings(cls):
        """الحصول على الإعدادات أو إنشاءها"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class PaymentMethod(models.Model):
    """طرق الدفع"""
    
    name = models.CharField('اسم طريقة الدفع', max_length=100)
    company = models.CharField('الشركة', max_length=100, blank=True)
    percentage = models.DecimalField(
        'النسبة (%)',
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='نسبة العمولة إن وجدت'
    )
    is_active = models.BooleanField('نشط', default=True)
    created_at = models.DateTimeField('تاريخ الإضافة', auto_now_add=True)
    
    class Meta:
        verbose_name = 'طريقة دفع'
        verbose_name_plural = 'طرق الدفع'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.company}" if self.company else self.name


class Attachment(models.Model):
    """المرفقات"""
    
    name = models.CharField('اسم المرفق', max_length=200)
    file = models.FileField(
        'الملف',
        upload_to='attachments/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    description = models.TextField('الوصف', blank=True)
    uploaded_at = models.DateTimeField('تاريخ الرفع', auto_now_add=True)
    
    class Meta:
        verbose_name = 'مرفق'
        verbose_name_plural = 'المرفقات'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.name
    
    def get_file_size(self):
        """الحصول على حجم الملف بالميجابايت"""
        if self.file:
            size_mb = self.file.size / (1024 * 1024)
            return f"{size_mb:.2f} MB"
        return "0 MB"