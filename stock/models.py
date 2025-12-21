from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from django.db.models import F, Sum


class Category(models.Model):
    """التصنيفات"""
    
    name = models.CharField('اسم التصنيف', max_length=100, unique=True)
    description = models.TextField('الوصف', blank=True)
    icon = models.CharField('أيقونة', max_length=50, default='fas fa-cube', help_text='مثال: fas fa-glasses')
    color = models.CharField('اللون', max_length=7, default='#4A9EAD', help_text='مثال: #FF5733')
    is_active = models.BooleanField('نشط', default=True)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        verbose_name = 'تصنيف'
        verbose_name_plural = 'التصنيفات'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def products_count(self):
        """عدد المنتجات في التصنيف"""
        return self.products.filter(is_active=True).count()
    
    @property
    def total_quantity(self):
        """إجمالي الكمية في التصنيف"""
        return self.products.filter(is_active=True).aggregate(
            total=Sum('quantity')
        )['total'] or 0


class Supplier(models.Model):
    """الموردين"""
    
    supplier_code = models.CharField('كود المورد', max_length=20, unique=True, editable=False)
    company_name = models.CharField('اسم الشركة', max_length=200)
    
    # معلومات الاتصال
    phone_regex = RegexValidator(
        regex=r'^5\d{8}$',
        message="يجب أن يبدأ رقم الجوال بـ 5 ويتكون من 9 أرقام"
    )
    phone = models.CharField('رقم الجوال', validators=[phone_regex], max_length=9)
    email = models.EmailField('البريد الإلكتروني', blank=True, null=True)
    address = models.TextField('العنوان', blank=True)
    
    # معلومات المندوب
    representative_name = models.CharField('اسم المندوب', max_length=200, blank=True)
    representative_phone = models.CharField('جوال المندوب', max_length=9, blank=True)
    
    # تفاصيل إضافية
    notes = models.TextField('ملاحظات', blank=True)
    is_active = models.BooleanField('نشط', default=True)
    
    # تواريخ
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        verbose_name = 'مورد'
        verbose_name_plural = 'الموردين'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.supplier_code} - {self.company_name}"
    
    def save(self, *args, **kwargs):
        if not self.supplier_code:
            # توليد كود المورد
            last_supplier = Supplier.objects.order_by('-id').first()
            if last_supplier and last_supplier.supplier_code:
                try:
                    last_number = int(last_supplier.supplier_code.split('-')[1])
                    new_number = last_number + 1
                except:
                    new_number = 1
            else:
                new_number = 1
            self.supplier_code = f'SUP-{new_number:04d}'
        super().save(*args, **kwargs)
    
    @property
    def products_count(self):
        """عدد المنتجات من هذا المورد"""
        return self.products.filter(is_active=True).count()
    
    @property
    def total_products_value(self):
        """إجمالي قيمة المنتجات من هذا المورد"""
        return self.products.filter(is_active=True).aggregate(
            total=Sum(F('quantity') * F('cost_price'))
        )['total'] or 0


class Product(models.Model):
    """المنتجات"""
    
    # معلومات أساسية
    item_name = models.CharField('اسم المنتج', max_length=200)
    barcode = models.CharField('الباركود', max_length=100, unique=True)
    sku = models.CharField('SKU', max_length=50, blank=True, help_text='رمز المنتج الداخلي')
    
    # التصنيف والمورد
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name='التصنيف'
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name='المورد'
    )
    
    # الكميات والأسعار
    quantity = models.IntegerField('الكمية المتوفرة', default=0)
    min_quantity = models.IntegerField('الحد الأدنى للكمية', default=5, help_text='تنبيه عند الوصول لهذا الحد')
    box_number = models.CharField('رقم الصندوق', max_length=50, blank=True)
    
    cost_price = models.DecimalField('سعر التكلفة', max_digits=10, decimal_places=2, default=0)
    selling_price = models.DecimalField('سعر البيع', max_digits=10, decimal_places=2, default=0)
    
    # معلومات إضافية
    description = models.TextField('الوصف', blank=True)
    notes = models.TextField('ملاحظات', blank=True)
    image = models.ImageField('صورة المنتج', upload_to='products/', blank=True, null=True)
    
    # حالة المنتج
    is_active = models.BooleanField('نشط', default=True)
    is_featured = models.BooleanField('منتج مميز', default=False)
    
    # تواريخ
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        verbose_name = 'منتج'
        verbose_name_plural = 'المنتجات'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['barcode']),
            models.Index(fields=['item_name']),
        ]
    
    def __str__(self):
        return f"{self.barcode} - {self.item_name}"
    
    @property
    def is_low_stock(self):
        """هل الكمية منخفضة؟"""
        return self.quantity <= self.min_quantity and self.quantity > 0
    
    @property
    def is_out_of_stock(self):
        """هل نفذت الكمية؟"""
        return self.quantity == 0
    
    @property
    def stock_status(self):
        """حالة المخزون"""
        if self.is_out_of_stock:
            return 'نفذ'
        elif self.is_low_stock:
            return 'منخفض'
        else:
            return 'متوفر'
    
    @property
    def stock_status_color(self):
        """لون حالة المخزون"""
        if self.is_out_of_stock:
            return 'danger'
        elif self.is_low_stock:
            return 'warning'
        else:
            return 'success'
    
    @property
    def profit_margin(self):
        """هامش الربح بالنسبة المئوية"""
        if self.cost_price > 0:
            return ((self.selling_price - self.cost_price) / self.cost_price) * 100
        return 0
    
    @property
    def profit_amount(self):
        """مبلغ الربح للقطعة الواحدة"""
        return self.selling_price - self.cost_price
    
    @property
    def total_cost_value(self):
        """القيمة الإجمالية للمخزون (بسعر التكلفة)"""
        return self.quantity * self.cost_price
    
    @property
    def total_selling_value(self):
        """القيمة الإجمالية للمخزون (بسعر البيع)"""
        return self.quantity * self.selling_price


class StockMovement(models.Model):
    """حركة المخزون"""
    
    MOVEMENT_TYPES = [
        ('in', 'إدخال'),
        ('out', 'إخراج'),
        ('adjustment', 'تعديل'),
        ('return', 'مرتجع'),
    ]
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='movements',
        verbose_name='المنتج'
    )
    movement_type = models.CharField('نوع الحركة', max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField('الكمية')
    previous_quantity = models.IntegerField('الكمية السابقة')
    new_quantity = models.IntegerField('الكمية الجديدة')
    
    # تفاصيل إضافية
    reference = models.CharField('المرجع', max_length=100, blank=True, help_text='مثال: رقم الفاتورة')
    notes = models.TextField('ملاحظات', blank=True)
    
    # التاريخ
    created_at = models.DateTimeField('تاريخ الحركة', auto_now_add=True)
    
    class Meta:
        verbose_name = 'حركة مخزون'
        verbose_name_plural = 'حركات المخزون'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.item_name} - {self.quantity}"
    
    @property
    def movement_type_icon(self):
        """أيقونة نوع الحركة"""
        icons = {
            'in': 'fa-arrow-down',
            'out': 'fa-arrow-up',
            'adjustment': 'fa-edit',
            'return': 'fa-undo',
        }
        return icons.get(self.movement_type, 'fa-exchange-alt')
    
    @property
    def movement_type_color(self):
        """لون نوع الحركة"""
        colors = {
            'in': 'success',
            'out': 'danger',
            'adjustment': 'warning',
            'return': 'info',
        }
        return colors.get(self.movement_type, 'secondary')

class Laboratory(models.Model):
    """المعامل"""
    
    laboratory_code = models.CharField('كود المعمل', max_length=20, unique=True, editable=False)
    company_name = models.CharField('اسم المعمل', max_length=200)
    
    # معلومات الاتصال
    phone_regex = RegexValidator(
        regex=r'^5\d{8}$',
        message="يجب أن يبدأ رقم الجوال بـ 5 ويتكون من 9 أرقام"
    )
    phone = models.CharField('رقم الجوال', validators=[phone_regex], max_length=9)
    email = models.EmailField('البريد الإلكتروني', blank=True, null=True)
    address = models.TextField('العنوان', blank=True)
    
    # معلومات المندوب
    representative_name = models.CharField('اسم المندوب', max_length=200, blank=True)
    representative_phone = models.CharField('جوال المندوب', max_length=9, blank=True)
    
    # تفاصيل إضافية
    notes = models.TextField('ملاحظات', blank=True)
    is_active = models.BooleanField('نشط', default=True)
    
    # تواريخ
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        verbose_name = 'معمل'
        verbose_name_plural = 'المعامل'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.laboratory_code} - {self.company_name}"
    
    def save(self, *args, **kwargs):
        if not self.laboratory_code:
            # توليد كود المعمل
            last_lab = Laboratory.objects.order_by('-id').first()
            if last_lab and last_lab.laboratory_code:
                try:
                    last_number = int(last_lab.laboratory_code.split('-')[1])
                    new_number = last_number + 1
                except:
                    new_number = 1
            else:
                new_number = 1
            self.laboratory_code = f'LAB-{new_number:04d}'
        super().save(*args, **kwargs)
    

