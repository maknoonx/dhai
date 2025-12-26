from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import F
from customers.models import Customer
from stock.models import Product, Laboratory


class Sale(models.Model):
    """نموذج المبيعات"""
    
    # معلومات الطلب
    order_number = models.CharField('رقم الطلب', max_length=50, unique=True)
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.PROTECT, 
        related_name='sales',
        verbose_name='العميل'
    )
    
    # المعمل (اختياري)
    laboratory = models.ForeignKey(
        Laboratory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales',
        verbose_name='المعمل'
    )
    
    # حالة الطلب
    STATUS_CHOICES = [
        ('created', 'تم الإنشاء'),
        ('lab', 'في المعمل'),
        ('ready', 'جاهز للاستلام'),
        ('received', 'تم الاستلام'),
        ('completed', 'مكتمل'),
        ('cancelled', 'ملغي'),
    ]
    status = models.CharField('حالة الطلب', max_length=20, choices=STATUS_CHOICES, default='created')
    
    # التواريخ
    order_date = models.DateTimeField('تاريخ الطلب', auto_now_add=True)
    delivery_date = models.DateField('تاريخ التسليم المتوقع', null=True, blank=True)
    completed_date = models.DateTimeField('تاريخ الإكمال', null=True, blank=True)
    
    # المبالغ
    subtotal = models.DecimalField(
        'المجموع الفرعي',
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    discount = models.DecimalField(
        'الخصم',
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    tax = models.DecimalField(
        'الضريبة (15%)',
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    total_amount = models.DecimalField(
        'المبلغ الإجمالي',
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # الدفع
    PAYMENT_METHODS = [
        ('cash', 'نقدي'),
        ('card', 'بطاقة'),
        ('transfer', 'تحويل بنكي'),
        ('mada', 'مدى'),
        ('later', 'آجل'),
    ]
    payment_method = models.CharField(
        'طريقة الدفع',
        max_length=20,
        choices=PAYMENT_METHODS,
        default='cash'
    )
    paid_amount = models.DecimalField(
        'المبلغ المدفوع',
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # ملاحظات
    notes = models.TextField('ملاحظات', blank=True)
    prescription_notes = models.TextField('ملاحظات القياس', blank=True)
    
    # معلومات إضافية
    created_by = models.CharField('أنشئ بواسطة', max_length=100, blank=True)
    updated_by = models.CharField('عُدل بواسطة', max_length=100, blank=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    
    class Meta:
        verbose_name = 'فاتورة'
        verbose_name_plural = 'الفواتير'
        ordering = ['-order_date']
    
    def __str__(self):
        return f"{self.order_number} - {self.customer.name}"
    
    def save(self, *args, **kwargs):
        """حساب المبلغ الإجمالي تلقائياً"""
        self.total_amount = self.subtotal - self.discount + self.tax
        super().save(*args, **kwargs)
    
    def get_remaining_amount(self):
        """حساب المبلغ المتبقي"""
        return self.total_amount - self.paid_amount
    
    def is_paid(self):
        """التحقق من اكتمال الدفع"""
        return self.paid_amount >= self.total_amount
    
    def get_payment_status(self):
        """حالة الدفع"""
        if self.paid_amount == 0:
            return 'unpaid'
        elif self.paid_amount < self.total_amount:
            return 'partial'
        else:
            return 'paid'
    
    def get_payment_status_display_ar(self):
        """عرض حالة الدفع بالعربي"""
        status = self.get_payment_status()
        if status == 'unpaid':
            return 'غير مدفوع'
        elif status == 'partial':
            return 'مدفوع جزئياً'
        else:
            return 'مدفوع بالكامل'
    
    def get_payment_status_color(self):
        """لون حالة الدفع"""
        status = self.get_payment_status()
        if status == 'unpaid':
            return 'danger'
        elif status == 'partial':
            return 'warning'
        else:
            return 'success'
    
    def get_status_color(self):
        """لون حالة الطلب"""
        colors = {
            'created': 'info',
            'lab': 'warning',
            'ready': 'primary',
            'received': 'success',
            'completed': 'success',
            'cancelled': 'danger',
        }
        return colors.get(self.status, 'secondary')


class SaleItem(models.Model):
    """عناصر المبيعات"""
    
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='الفاتورة'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='المنتج'
    )
    
    # للخدمات الإضافية (بدون منتج)
    service_name = models.CharField('اسم الخدمة', max_length=200, blank=True)
    
    quantity = models.IntegerField(
        'الكمية',
        default=1,
        validators=[MinValueValidator(1)]
    )
    unit_price = models.DecimalField(
        'سعر الوحدة',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    total_price = models.DecimalField(
        'السعر الإجمالي',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # معلومات إضافية للنظارات الطبية
    prescription_right = models.TextField('قياس العين اليمنى', blank=True)
    prescription_left = models.TextField('قياس العين اليسرى', blank=True)
    
    class Meta:
        verbose_name = 'عنصر فاتورة'
        verbose_name_plural = 'عناصر الفواتير'
    
    def __str__(self):
        if self.product:
            return f"{self.product.item_name} x {self.quantity}"
        else:
            return f"{self.service_name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        """حساب السعر الإجمالي تلقائياً"""
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
    
    def get_item_name(self):
        """الحصول على اسم العنصر"""
        if self.product:
            return self.product.item_name
        else:
            return self.service_name


class Payment(models.Model):
    """سجل الدفعات"""
    
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='الفاتورة'
    )
    amount = models.DecimalField(
        'المبلغ',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    payment_method = models.CharField(
        'طريقة الدفع',
        max_length=20,
        choices=Sale.PAYMENT_METHODS
    )
    payment_date = models.DateTimeField('تاريخ الدفع', auto_now_add=True)
    reference = models.CharField('المرجع', max_length=100, blank=True, help_text='رقم المعاملة أو الإيصال')
    notes = models.TextField('ملاحظات', blank=True)
    created_by = models.CharField('أضيف بواسطة', max_length=100, blank=True)
    
    class Meta:
        verbose_name = 'دفعة'
        verbose_name_plural = 'الدفعات'
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"دفعة {self.amount} ريال - {self.sale.order_number}"
    


    # إضافة هذا الكود إلى ملف sales/models.py

from django.db import models
from django.core.validators import MinValueValidator

class Service(models.Model):
    """نموذج الخدمات"""
    
    service_code = models.CharField('رمز الخدمة', max_length=50, unique=True)
    service_name = models.CharField('اسم الخدمة', max_length=200)
    
    # التكلفة (اختياري)
    cost = models.DecimalField(
        'التكلفة',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text='تكلفة الخدمة (اختياري)'
    )
    
    # السعر
    price = models.DecimalField(
        'السعر',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # حالة الخدمة
    is_active = models.BooleanField('نشط', default=True)
    
    # معلومات إضافية
    description = models.TextField('الوصف', blank=True)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)
    created_by = models.CharField('أنشئ بواسطة', max_length=100, blank=True)
    
    class Meta:
        verbose_name = 'خدمة'
        verbose_name_plural = 'الخدمات'
        ordering = ['service_name']
    
    def __str__(self):
        return f"{self.service_code} - {self.service_name}"
    
    def get_profit(self):
        """حساب الربح"""
        if self.cost:
            return self.price - self.cost
        return None
    
    def get_profit_percentage(self):
        """نسبة الربح"""
        if self.cost and self.cost > 0:
            return ((self.price - self.cost) / self.cost) * 100
        return None