from django.contrib import admin
from .models import CompanySettings, PaymentMethod, Attachment


@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
    list_display = ['company_name_ar', 'company_name_en', 'contact_phone', 'updated_at']
    fieldsets = (
        ('بيانات المؤسسة', {
            'fields': ('company_name_ar', 'company_name_en', 'unified_number', 
                      'commercial_register', 'tax_number', 'national_address', 'location_url')
        }),
        ('بيانات التواصل', {
            'fields': ('contact_phone', 'contact_email')
        }),
        ('بيانات المفوض/المالك', {
            'fields': ('owner_name', 'owner_id_number', 'owner_phone', 'owner_email')
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one settings instance
        return not CompanySettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of settings
        return False


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'percentage', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'company']
    list_editable = ['is_active']


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_file_size', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['name', 'description']
    readonly_fields = ['uploaded_at']
