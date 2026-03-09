from django.contrib import admin
from .models import WhatsAppMessage, WebhookLog


@admin.register(WhatsAppMessage)
class WhatsAppMessageAdmin(admin.ModelAdmin):
    list_display = ['recipient_phone', 'direction', 'message_type', 'status', 'body_preview', 'created_at']
    list_filter = ['direction', 'status', 'message_type', 'created_at']
    search_fields = ['recipient_phone', 'body', 'wa_message_id']
    readonly_fields = ['wa_message_id', 'raw_payload', 'created_at', 'updated_at']
    ordering = ['-created_at']

    def body_preview(self, obj):
        return obj.body[:80] + '...' if len(obj.body) > 80 else obj.body
    body_preview.short_description = 'محتوى الرسالة'


@admin.register(WebhookLog)
class WebhookLogAdmin(admin.ModelAdmin):
    list_display = ['received_at', 'processed']
    list_filter = ['processed', 'received_at']
    readonly_fields = ['payload', 'received_at']
    ordering = ['-received_at']