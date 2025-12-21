// Laboratory JavaScript

const laboratoryModal = document.getElementById('laboratoryModal');
const laboratoryForm = document.getElementById('laboratoryForm');
const viewLaboratoryModal = document.getElementById('viewLaboratoryModal');
let currentLaboratoryId = null;

function showAddModal() {
    laboratoryForm.reset();
    laboratoryForm.action = '/stock/laboratory/add/';
    document.getElementById('modalTitle').textContent = 'إضافة معمل جديد';
    laboratoryModal.classList.add('active');
    laboratoryModal.style.display = 'flex'; // إضافة هذا السطر
}

function closeModal() {
    laboratoryModal.classList.remove('active');
    laboratoryModal.style.display = 'none'; // إضافة هذا السطر
    laboratoryForm.reset();
}

function editLaboratory(laboratoryId) {
    // جلب بيانات المعمل أولاً
    fetch(`/stock/laboratory/${laboratoryId}/details/`)
        .then(response => response.json())
        .then(data => {
            // ملء النموذج بالبيانات
            document.getElementById('company_name').value = data.company_name || '';
            document.getElementById('phone').value = data.phone || '';
            document.getElementById('email').value = data.email || '';
            document.getElementById('address').value = data.address || '';
            document.getElementById('representative_name').value = data.representative_name || '';
            document.getElementById('representative_phone').value = data.representative_phone || '';
            document.getElementById('notes').value = data.notes || '';
            
            // تغيير العنوان والـ action
            laboratoryForm.action = `/stock/laboratory/${laboratoryId}/edit/`;
            document.getElementById('modalTitle').textContent = 'تعديل المعمل';
            laboratoryModal.classList.add('active');
            laboratoryModal.style.display = 'flex';
        })
        .catch(error => {
            console.error('Error:', error);
            alert('حدث خطأ في تحميل البيانات');
        });
}

function deleteLaboratory(laboratoryId, laboratoryName) {
    if (confirm(`هل أنت متأكد من حذف المعمل "${laboratoryName}"؟`)) {
        window.location.href = `/stock/laboratory/${laboratoryId}/delete/`;
    }
}

function viewLaboratory(laboratoryId) {
    currentLaboratoryId = laboratoryId;
    
    fetch(`/stock/laboratory/${laboratoryId}/details/`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('view_company_name').textContent = data.company_name || '-';
            document.getElementById('view_laboratory_code').textContent = data.laboratory_code || '-';
            document.getElementById('view_status').textContent = data.is_active ? 'نشط' : 'غير نشط';
            document.getElementById('view_phone').textContent = data.phone || '-';
            document.getElementById('view_email').textContent = data.email || '-';
            document.getElementById('view_address').textContent = data.address || '-';
            document.getElementById('view_rep_name').textContent = data.representative_name || '-';
            document.getElementById('view_rep_phone').textContent = data.representative_phone || '-';
            // تم إزالة products_count
            document.getElementById('view_created_at').textContent = data.created_at || '-';
            document.getElementById('view_updated_at').textContent = data.updated_at || '-';
            document.getElementById('view_notes').textContent = data.notes || 'لا توجد ملاحظات';
            
            viewLaboratoryModal.classList.add('active');
            viewLaboratoryModal.style.display = 'flex'; // إضافة هذا السطر
        })
        .catch(error => {
            console.error('Error:', error);
            alert('حدث خطأ في تحميل البيانات');
        });
}

function closeViewModal() {
    viewLaboratoryModal.classList.remove('active');
    viewLaboratoryModal.style.display = 'none'; // إضافة هذا السطر
    currentLaboratoryId = null;
}

function editLaboratoryFromView() {
    closeViewModal();
    if (currentLaboratoryId) {
        editLaboratory(currentLaboratoryId);
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
laboratoryModal?.addEventListener('click', function(e) {
    if (e.target === laboratoryModal) {
        closeModal();
    }
});

viewLaboratoryModal?.addEventListener('click', function(e) {
    if (e.target === viewLaboratoryModal) {
        closeViewModal();
    }
});

// Close on Escape
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeModal();
        closeViewModal();
    }
});

// Form validation
laboratoryForm?.addEventListener('submit', function(e) {
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

console.log('Laboratory JS loaded');