// Products List JavaScript

const searchInput = document.getElementById('searchInput');
const categoryFilter = document.getElementById('categoryFilter');
const statusFilter = document.getElementById('statusFilter');
const productModal = document.getElementById('productModal');
const deleteModal = document.getElementById('deleteModal');
const productForm = document.getElementById('productForm');
const deleteForm = document.getElementById('deleteForm');

// Search functionality
let searchTimeout;
searchInput?.addEventListener('input', function() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        applyFilters();
    }, 500);
});

function applyFilters() {
    const params = new URLSearchParams();
    
    const search = searchInput?.value.trim();
    if (search) {
        params.set('search', search);
    }
    
    const category = categoryFilter?.value;
    if (category) {
        params.set('category', category);
    }
    
    const status = statusFilter?.value;
    if (status) {
        params.set('status', status);
    }
    
    window.location.href = `?${params.toString()}`;
}

function clearFilters() {
    window.location.href = window.location.pathname;
}

// Modal Management
function showAddModal() {
    productForm.reset();
    productForm.action = '/stock/products/add/';
    document.getElementById('modalTitle').textContent = 'إضافة منتج جديد';
    document.getElementById('submitText').textContent = 'حفظ المنتج';
    productModal.classList.add('active');
}

function showEditModal(productId) {
    // This would need to fetch product data via AJAX in a real implementation
    productForm.action = `/stock/products/${productId}/edit/`;
    document.getElementById('modalTitle').textContent = 'تعديل المنتج';
    document.getElementById('submitText').textContent = 'حفظ التعديلات';
    productModal.classList.add('active');
}

function closeModal() {
    productModal.classList.remove('active');
    productForm.reset();
}

function showDeleteModal(productId, productName) {
    document.getElementById('deleteProductName').textContent = productName;
    deleteForm.action = `/stock/products/${productId}/delete/`;
    deleteModal.classList.add('active');
}

function closeDeleteModal() {
    deleteModal.classList.remove('active');
}

// Close modal on outside click
productModal?.addEventListener('click', function(e) {
    if (e.target === productModal) {
        closeModal();
    }
});

deleteModal?.addEventListener('click', function(e) {
    if (e.target === deleteModal) {
        closeDeleteModal();
    }
});

// Close modal on Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeModal();
        closeDeleteModal();
    }
});

// Calculate profit margin
const costPriceInput = document.getElementById('cost_price');
const sellingPriceInput = document.getElementById('selling_price');
const profitMarginDisplay = document.getElementById('profitMargin');

function calculateProfit() {
    const cost = parseFloat(costPriceInput?.value) || 0;
    const selling = parseFloat(sellingPriceInput?.value) || 0;
    
    if (cost > 0) {
        const margin = ((selling - cost) / cost) * 100;
        const amount = selling - cost;
        
        profitMarginDisplay.querySelector('.profit-value').textContent = 
            `${margin.toFixed(1)}%`;
        profitMarginDisplay.querySelector('.profit-amount').textContent = 
            `${amount.toFixed(2)} ريال`;
    } else {
        profitMarginDisplay.querySelector('.profit-value').textContent = '0%';
        profitMarginDisplay.querySelector('.profit-amount').textContent = '0 ريال';
    }
}

costPriceInput?.addEventListener('input', calculateProfit);
sellingPriceInput?.addEventListener('input', calculateProfit);

// Form validation
productForm?.addEventListener('submit', function(e) {
    const itemName = document.getElementById('item_name').value.trim();
    const barcode = document.getElementById('barcode').value.trim();
    
    if (!itemName || !barcode) {
        e.preventDefault();
        alert('الرجاء ملء جميع الحقول المطلوبة');
        return false;
    }
});

// Auto-hide messages
document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelectorAll('.message');
    messages.forEach(function(message) {
        setTimeout(function() {
            message.style.opacity = '0';
            setTimeout(function() {
                message.remove();
            }, 300);
        }, 5000);
    });
});

console.log('Products JS loaded successfully');