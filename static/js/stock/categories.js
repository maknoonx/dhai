// Categories JavaScript
const categoryModal = document.getElementById('categoryModal');
const categoryForm = document.getElementById('categoryForm');
const iconSelect = document.getElementById('icon');
const colorInput = document.getElementById('color');
const previewIcon = document.getElementById('previewIcon');
const colorPreview = document.getElementById('colorPreview');

function showAddModal() {
    categoryForm.reset();
    categoryForm.action = '/stock/categories/add/';  // ← هنا التغيير
    document.getElementById('modalTitle').textContent = 'إضافة تصنيف جديد';
    if (typeof updatePreview === 'function') updatePreview();
    categoryModal.classList.add('active');
}

function closeModal() {
    categoryModal.classList.remove('active');
    categoryForm.reset();
}

function editCategory(categoryId) {
    categoryForm.action = `/stock/categories/${categoryId}/edit/`;
    document.getElementById('modalTitle').textContent = 'تعديل التصنيف';
    categoryModal.classList.add('active');
}

function deleteCategory(categoryId, categoryName) {
    if (confirm(`هل أنت متأكد من حذف التصنيف "${categoryName}"؟`)) {
        window.location.href = `/stock/categories/${categoryId}/delete/`;
    }
}

function updatePreview() {
    const icon = iconSelect?.value || 'fas fa-cube';
    const color = colorInput?.value || '#4A9EAD';
    
    if (previewIcon) {
        previewIcon.style.backgroundColor = color;
        const iconElement = previewIcon.querySelector('i');
        if (iconElement) {
            iconElement.className = icon;
        }
    }
    
    if (colorPreview) {
        colorPreview.textContent = color;
    }
}

// Event Listeners
iconSelect?.addEventListener('change', updatePreview);
colorInput?.addEventListener('input', updatePreview);

// Close modal on outside click
categoryModal?.addEventListener('click', function(e) {
    if (e.target === categoryModal) {
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
categoryForm?.addEventListener('submit', function(e) {
    const name = document.getElementById('name').value.trim();
    
    if (!name) {
        e.preventDefault();
        alert('الرجاء إدخال اسم التصنيف');
        return false;
    }
});

// Initialize preview on page load
document.addEventListener('DOMContentLoaded', function() {
    if (typeof updatePreview === 'function') updatePreview();
    console.log('Categories JS loaded');
});