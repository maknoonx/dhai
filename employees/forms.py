from django import forms
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from .models import EmployeeProfile, EmployeeGroup


class EmployeeForm(forms.ModelForm):
    """نموذج إضافة/تعديل موظف"""
    
    # حقول إضافية
    email = forms.EmailField(
        label='البريد الإلكتروني',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@company.com'
        })
    )
    
    password = forms.CharField(
        label='كلمة المرور',
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'اتركه فارغاً للاحتفاظ بالقديمة'
        }),
        help_text='اترك الحقل فارغاً إذا كنت لا تريد تغيير كلمة المرور'
    )
    
    password_confirm = forms.CharField(
        label='تأكيد كلمة المرور',
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'أعد إدخال كلمة المرور'
        })
    )
    
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        label='المجموعات',
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text='اختر المجموعات التي ينتمي إليها الموظف'
    )
    
    class Meta:
        model = EmployeeProfile
        fields = [
            'employee_id', 'full_name_arabic', 'position', 'gender',
            'phone', 'national_id', 'photo',
            'hire_date', 'department', 'salary',
            'address', 'notes'
        ]
        widgets = {
            'employee_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'EMP001'
            }),
            'full_name_arabic': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أحمد محمد عبدالله'
            }),
            'position': forms.Select(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '05xxxxxxxx'
            }),
            'national_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1xxxxxxxxx'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'hire_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'المبيعات'
            }),
            'salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '5000.00'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'العنوان الكامل'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات إضافية'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        # التحقق من تطابق كلمات المرور
        if password and password != password_confirm:
            raise forms.ValidationError('كلمات المرور غير متطابقة')
        
        return cleaned_data
    
    def clean_employee_id(self):
        """التحقق من عدم تكرار رقم الموظف"""
        employee_id = self.cleaned_data.get('employee_id')
        
        # في حالة التعديل، استثناء الموظف الحالي
        if self.instance.pk:
            if EmployeeProfile.objects.exclude(pk=self.instance.pk).filter(employee_id=employee_id).exists():
                raise forms.ValidationError('رقم الموظف موجود مسبقاً')
        else:
            if EmployeeProfile.objects.filter(employee_id=employee_id).exists():
                raise forms.ValidationError('رقم الموظف موجود مسبقاً')
        
        return employee_id


class EmployeeGroupForm(forms.ModelForm):
    """نموذج إضافة/تعديل مجموعة"""
    
    # الصلاحيات المخصصة
    permissions = forms.MultipleChoiceField(
        label='الصلاحيات',
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=[],
    )
    
    class Meta:
        model = EmployeeGroup
        fields = [
            'name', 'name_arabic', 'description',
            'can_view_reports', 'can_manage_sales', 'can_manage_inventory',
            'can_manage_customers', 'can_manage_suppliers',
            'can_view_financial', 'can_manage_settings'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'sales_team'
            }),
            'name_arabic': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'فريق المبيعات'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'وصف المجموعة'
            }),
            'can_view_reports': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_manage_sales': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_manage_inventory': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_manage_customers': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_manage_suppliers': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_view_financial': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_manage_settings': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # الحصول على جميع الصلاحيات المتاحة
        permissions = Permission.objects.select_related('content_type').all()
        
        self.fields['permissions'].choices = [
            (perm.id, f"{perm.content_type.app_label} | {perm.name}")
            for perm in permissions
        ]
        
        # في حالة التعديل، ملء الصلاحيات الحالية
        if self.instance.pk and hasattr(self.instance, 'group'):
            self.fields['permissions'].initial = list(
                self.instance.group.permissions.values_list('id', flat=True)
            )
    
    def save_permissions(self, employee_group):
        """حفظ الصلاحيات"""
        if self.cleaned_data.get('permissions'):
            permission_ids = [int(p) for p in self.cleaned_data['permissions']]
            permissions = Permission.objects.filter(id__in=permission_ids)
            employee_group.group.permissions.set(permissions)
        else:
            employee_group.group.permissions.clear()


class EmployeeSearchForm(forms.Form):
    """نموذج البحث عن الموظفين"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ابحث بالاسم، رقم الموظف، الجوال...'
        })
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'الكل'),
            ('active', 'نشط'),
            ('inactive', 'موقوف'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    position = forms.ChoiceField(
        required=False,
        choices=[('', 'جميع المناصب')] + list(EmployeeProfile.POSITION_CHOICES),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    group = forms.ModelChoiceField(
        queryset=EmployeeGroup.objects.all(),
        required=False,
        empty_label='جميع المجموعات',
        widget=forms.Select(attrs={'class': 'form-control'})
    )