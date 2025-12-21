// Suppliers JavaScript



// عرض تفاصيل المورد
let currentSupplierId = null;

function viewSupplier(supplierId) {
    currentSupplierId = supplierId;
    
    // جلب البيانات من الـ API أو من الصفحة
    // هنا سنستخدم fetch للحصول على البيانات
    fetch(`/stock/suppliers/${supplierId}/details/`)
        .then(response => response.json())
        .then(data => {
            // ملء البيانات في الـ Modal
            document.getElementById('view_company_name').textContent = data.company_name || '-';
            document.getElementById('view_supplier_code').textContent = data.supplier_code || '-';
            document.getElementById('view_status').textContent = data.is_active ? 'نشط' : 'غير نشط';
            document.getElementById('view_phone').textContent = data.phone || '-';
            document.getElementById('view_email').textContent = data.email || '-';
            document.getElementById('view_address').textContent = data.address || '-';
            document.getElementById('view_rep_name').textContent = data.representative_name || '-';
            document.getElementById('view_rep_phone').textContent = data.representative_phone || '-';
            document.getElementById('view_products_count').textContent = data.products_count || '0';
            document.getElementById('view_created_at').textContent = data.created_at || '-';
            document.getElementById('view_updated_at').textContent = data.updated_at || '-';
            document.getElementById('view_notes').textContent = data.notes || 'لا توجد ملاحظات';
            
            // فتح الـ Modal
            document.getElementById('viewSupplierModal').classList.add('active');
        })
        .catch(error => {
            console.error('Error:', error);
            alert('حدث خطأ في تحميل البيانات');
        });
}

function closeViewModal() {
    document.getElementById('viewSupplierModal').classList.remove('active');
    currentSupplierId = null;
}

function editSupplierFromView() {
    closeViewModal();
    if (currentSupplierId) {
        editSupplier(currentSupplierId);
    }
}

// إغلاق عند الضغط خارج الـ Modal
document.getElementById('viewSupplierModal')?.addEventListener('click', function(e) {
    if (e.target === this) {
        closeViewModal();
    }
});

const supplierModal = document.getElementById('supplierModal');
const supplierForm = document.getElementById('supplierForm');



function showAddModal() {
    supplierForm.reset();
    supplierForm.action = '/stock/suppliers/add/';
    document.getElementById('modalTitle').textContent = 'إضافة مورد جديد';
    supplierModal.classList.add('active');
}

function closeModal() {
    supplierModal.classList.remove('active');
    supplierForm.reset();
}

function editSupplier(supplierId) {
    supplierForm.action = `/stock/suppliers/${supplierId}/edit/`;
    document.getElementById('modalTitle').textContent = 'تعديل المورد';
    supplierModal.classList.add('active');
}

function deleteSupplier(supplierId, supplierName) {
    if (confirm(`هل أنت متأكد من حذف المورد "${supplierName}"؟`)) {
        window.location.href = `/stock/suppliers/${supplierId}/delete/`;
    }
}

// Phone validation
const phoneInputs = document.querySelectorAll('input[type="tel"]');
phoneInputs.forEach(input => {
    input.addEventListener('input', function(e) {
        this.value = this.value.replace(/[^0-9]/g, '');
        if (this.value.length > 9) {
            this.value = this.value.slice(0, 9);
        }
    });
});

// Close modal on outside click
supplierModal?.addEventListener('click', function(e) {
    if (e.target === supplierModal) {
        closeModal();
    }
});

// Close on Escape
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeModal();
    }
});

// Form validation
supplierForm?.addEventListener('submit', function(e) {
    const companyName = document.getElementById('company_name').value.trim();
    const phone = document.getElementById('phone').value.trim();
    
    if (!companyName || !phone) {
        e.preventDefault();
        alert('الرجاء ملء الحقول المطلوبة');
        return false;
    }
    
    if (phone.length !== 9 || !phone.startsWith('5')) {
        e.preventDefault();
        alert('رقم الجوال يجب أن يبدأ بـ 5 ويتكون من 9 أرقام');
        return false;
    }
});

console.log('Suppliers JS loaded');