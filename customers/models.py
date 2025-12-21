from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone

class Customer(models.Model):
    """نموذج العملاء"""
    
    GENDER_CHOICES = [
        ('ذكر', 'ذكر'),
        ('أنثى', 'أنثى'),
    ]
    
    # معلومات أساسية
    customer_id = models.CharField('رقم العميل', max_length=20, unique=True, editable=False)
    name = models.CharField('الاسم الثلاثي', max_length=200)
    
    # رقم الجوال السعودي (يبدأ بـ 5 ويتكون من 9 أرقام)
    phone_regex = RegexValidator(
        regex=r'^5\d{8}$',
        message="يجب أن يبدأ رقم الجوال بـ 5 ويتكون من 9 أرقام"
    )
    phone = models.CharField('رقم الجوال', validators=[phone_regex], max_length=9, unique=True)
    
    email = models.EmailField('البريد الإلكتروني', blank=True, null=True)
    address = models.CharField('العنوان', max_length=300, blank=True)
    gender = models.CharField('الجنس', max_length=10, choices=GENDER_CHOICES)
    age = models.PositiveIntegerField('العمر', null=True, blank=True)
    
    # تواريخ
    join_date = models.DateField('تاريخ التسجيل', default=timezone.now)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    # إعدادات الإشعارات
    notify_whatsapp = models.BooleanField('إشعارات واتساب', default=True)
    notify_sms = models.BooleanField('إشعارات SMS', default=True)
    notify_email = models.BooleanField('إشعارات البريد', default=False)
    
    class Meta:
        verbose_name = 'عميل'
        verbose_name_plural = 'العملاء'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer_id} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.customer_id:
            # توليد رقم عميل تلقائي
            last_customer = Customer.objects.order_by('-id').first()
            if last_customer and last_customer.customer_id:
                try:
                    last_number = int(last_customer.customer_id.split('-')[1])
                    new_number = last_number + 1
                except:
                    new_number = 1
            else:
                new_number = 1
            self.customer_id = f'C-{new_number:03d}'
        super().save(*args, **kwargs)
    
    @property
    def total_purchases(self):
        """إجمالي المشتريات"""
        try:
            from sales.models import Invoice
            total = Invoice.objects.filter(customer=self).aggregate(
                total=models.Sum('total_amount')
            )['total'] or 0
            return total
        except:
            return 0
    
    @property
    def invoices_count(self):
        """عدد الفواتير"""
        try:
            from sales.models import Invoice
            return Invoice.objects.filter(customer=self).count()
        except:
            return 0
    
    @property
    def latest_exam(self):
        """آخر فحص نظر"""
        return self.eye_exams.first()


class EyeExam(models.Model):
    """نموذج الفحص الطبي للنظر"""
    
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        related_name='eye_exams', 
        verbose_name='العميل'
    )
    exam_date = models.DateField('تاريخ الفحص', default=timezone.now)
    
    # العين اليمنى
    right_sphere = models.CharField('القوة الكروية - يمنى', max_length=10, blank=True)
    right_cylinder = models.CharField('القوة الأسطوانية - يمنى', max_length=10, blank=True)
    right_axis = models.CharField('المحور - يمنى', max_length=10, blank=True)
    right_add = models.CharField('القراءة - يمنى', max_length=10, blank=True)
    right_pd = models.CharField('المسافة البؤرية - يمنى', max_length=10, blank=True)
    
    # العين اليسرى
    left_sphere = models.CharField('القوة الكروية - يسرى', max_length=10, blank=True)
    left_cylinder = models.CharField('القوة الأسطوانية - يسرى', max_length=10, blank=True)
    left_axis = models.CharField('المحور - يسرى', max_length=10, blank=True)
    left_add = models.CharField('القراءة - يسرى', max_length=10, blank=True)
    left_pd = models.CharField('المسافة البؤرية - يسرى', max_length=10, blank=True)
    
    # ملاحظات
    notes = models.TextField('ملاحظات الفحص', blank=True)
    
    # تواريخ
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        verbose_name = 'فحص نظر'
        verbose_name_plural = 'فحوصات النظر'
        ordering = ['-exam_date']
    
    def __str__(self):
        return f"فحص {self.customer.name} - {self.exam_date}"


class Notification(models.Model):
    """نموذج سجل الإشعارات"""
    
    NOTIFICATION_TYPES = [
        ('whatsapp', 'واتساب'),
        ('sms', 'SMS'),
        ('email', 'بريد إلكتروني'),
    ]
    
    MESSAGE_TYPES = [
        ('exam', 'إرسال الفحص الطبي'),
        ('delivery', 'طلب تسليم أو توصيل'),
        ('pickup', 'إشعار استلام النظارة'),
        ('invoice', 'فاتورة المشتريات'),
        ('confirmation', 'تأكيد الطلب'),
        ('reminder', 'تذكير بموعد الفحص'),
    ]
    
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        related_name='notifications', 
        verbose_name='العميل'
    )
    notification_type = models.CharField('نوع الإشعار', max_length=20, choices=NOTIFICATION_TYPES)
    message_type = models.CharField('نوع الرسالة', max_length=20, choices=MESSAGE_TYPES)
    message = models.TextField('محتوى الرسالة', blank=True)
    sent_at = models.DateTimeField('تاريخ الإرسال', auto_now_add=True)
    
    class Meta:
        verbose_name = 'إشعار'
        verbose_name_plural = 'الإشعارات'
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.customer.name}"
    
    def get_type_color(self):
        """لون حسب نوع الإشعار"""
        colors = {
            'whatsapp': 'blue',
            'sms': 'orange',
            'email': 'purple',
        }
        return colors.get(self.notification_type, 'gray')