from django.db import models
from django.utils import timezone


class Report(models.Model):
    """التقارير المحفوظة"""
    
    REPORT_TYPES = [
        ('daily_balance', 'الموازنة اليومية'),
        ('revenue', 'تقرير الإيرادات'),
        ('inventory', 'تقرير المخزون'),
        ('sales', 'تقرير المبيعات'),
        ('customers', 'تقرير العملاء'),
        ('products', 'تقرير المنتجات'),
        ('payments', 'تقرير المدفوعات'),
        ('profit', 'تقرير الأرباح'),
    ]
    
    name = models.CharField('اسم التقرير', max_length=200)
    report_type = models.CharField('نوع التقرير', max_length=50, choices=REPORT_TYPES)
    date_from = models.DateField('من تاريخ')
    date_to = models.DateField('إلى تاريخ')
    
    # بيانات التقرير (JSON)
    data = models.JSONField('البيانات', null=True, blank=True)
    
    # معلومات إضافية
    notes = models.TextField('ملاحظات', blank=True)
    created_by = models.CharField('أنشئ بواسطة', max_length=100)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    
    class Meta:
        verbose_name = 'تقرير'
        verbose_name_plural = 'التقارير'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_report_type_display()}"


class ReportSchedule(models.Model):
    """جدولة التقارير التلقائية"""
    
    FREQUENCY_CHOICES = [
        ('daily', 'يومي'),
        ('weekly', 'أسبوعي'),
        ('monthly', 'شهري'),
    ]
    
    name = models.CharField('اسم الجدولة', max_length=200)
    report_type = models.CharField('نوع التقرير', max_length=50, choices=Report.REPORT_TYPES)
    frequency = models.CharField('التكرار', max_length=20, choices=FREQUENCY_CHOICES)
    
    is_active = models.BooleanField('نشط', default=True)
    last_run = models.DateTimeField('آخر تشغيل', null=True, blank=True)
    next_run = models.DateTimeField('التشغيل القادم', null=True, blank=True)
    
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    
    class Meta:
        verbose_name = 'جدولة تقرير'
        verbose_name_plural = 'جدولة التقارير'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_frequency_display()}"