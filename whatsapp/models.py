from django.db import models
from django.conf import settings


class WhatsAppMessage(models.Model):
    """Log every sent and received WhatsApp message."""

    DIRECTION_CHOICES = [
        ('outbound', 'صادر'),   # Outbound
        ('inbound', 'وارد'),    # Inbound
    ]

    STATUS_CHOICES = [
        ('pending', 'قيد الإرسال'),
        ('sent', 'تم الإرسال'),
        ('delivered', 'تم التسليم'),
        ('read', 'تمت القراءة'),
        ('failed', 'فشل'),
    ]

    MESSAGE_TYPE_CHOICES = [
        ('text', 'نص'),
        ('template', 'قالب'),
        ('image', 'صورة'),
        ('document', 'مستند'),
    ]

    # Core fields
    wa_message_id = models.CharField(
        'معرف رسالة واتساب', max_length=255, blank=True, null=True, db_index=True
    )
    direction = models.CharField('الاتجاه', max_length=10, choices=DIRECTION_CHOICES)
    recipient_phone = models.CharField('رقم المستلم', max_length=20, db_index=True)
    message_type = models.CharField('نوع الرسالة', max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text')
    body = models.TextField('محتوى الرسالة', blank=True)
    template_name = models.CharField('اسم القالب', max_length=255, blank=True)

    # Status tracking
    status = models.CharField('الحالة', max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField('رسالة الخطأ', blank=True)

    # Metadata
    raw_payload = models.JSONField('البيانات الخام', blank=True, null=True)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'رسالة واتساب'
        verbose_name_plural = 'رسائل واتساب'

    def __str__(self):
        direction_label = 'إلى' if self.direction == 'outbound' else 'من'
        return f'{direction_label} {self.recipient_phone} - {self.status}'


class WebhookLog(models.Model):
    """Log raw webhook payloads for debugging."""

    payload = models.JSONField('البيانات')
    received_at = models.DateTimeField('تاريخ الاستلام', auto_now_add=True)
    processed = models.BooleanField('تمت المعالجة', default=False)

    class Meta:
        ordering = ['-received_at']
        verbose_name = 'سجل Webhook'
        verbose_name_plural = 'سجلات Webhook'

    def __str__(self):
        return f'Webhook @ {self.received_at}'