from django.contrib import admin
from .models import Customer, EyeExam, Notification

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['customer_id', 'name', 'phone', 'gender', 'age', 'join_date', 'created_at']
    list_filter = ['gender', 'join_date', 'notify_whatsapp', 'notify_sms']
    search_fields = ['customer_id', 'name', 'phone', 'email']
    readonly_fields = ['customer_id', 'created_at', 'updated_at']
    
    fieldsets = [
        ('معلومات أساسية', {
            'fields': ['customer_id', 'name', 'phone', 'email', 'address']
        }),
        ('معلومات شخصية', {
            'fields': ['gender', 'age', 'join_date']
        }),
        ('إعدادات الإشعارات', {
            'fields': ['notify_whatsapp', 'notify_sms', 'notify_email']
        }),
        ('معلومات النظام', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]


@admin.register(EyeExam)
class EyeExamAdmin(admin.ModelAdmin):
    list_display = ['customer', 'exam_date', 'created_at']
    list_filter = ['exam_date']
    search_fields = ['customer__name', 'customer__customer_id']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ('معلومات الفحص', {
            'fields': ['customer', 'exam_date']
        }),
        ('العين اليمنى', {
            'fields': ['right_sphere', 'right_cylinder', 'right_axis', 'right_add', 'right_pd']
        }),
        ('العين اليسرى', {
            'fields': ['left_sphere', 'left_cylinder', 'left_axis', 'left_add', 'left_pd']
        }),
        ('ملاحظات', {
            'fields': ['notes']
        }),
        ('معلومات النظام', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['customer', 'notification_type', 'message_type', 'sent_at']
    list_filter = ['notification_type', 'message_type', 'sent_at']
    search_fields = ['customer__name', 'customer__customer_id', 'message']
    readonly_fields = ['sent_at']
    
    fieldsets = [
        ('معلومات الإشعار', {
            'fields': ['customer', 'notification_type', 'message_type', 'message']
        }),
        ('معلومات النظام', {
            'fields': ['sent_at'],
            'classes': ['collapse']
        }),
    ]