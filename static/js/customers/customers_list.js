// Customers List JavaScript

// Search functionality
const searchInput = document.getElementById('searchInput');
const dateFrom = document.getElementById('dateFrom');
const dateTo = document.getElementById('dateTo');

// Debounce search
let searchTimeout;
searchInput?.addEventListener('input', function() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        applyFilters();
    }, 500);
});

// Date filters
dateFrom?.addEventListener('change', applyFilters);
dateTo?.addEventListener('change', applyFilters);

function applyFilters() {
    const params = new URLSearchParams();
    
    const search = searchInput?.value.trim();
    if (search) {
        params.set('search', search);
    }
    
    const from = dateFrom?.value;
    if (from) {
        params.set('date_from', from);
    }
    
    const to = dateTo?.value;
    if (to) {
        params.set('date_to', to);
    }
    
    params.set('page', '1'); // Reset to page 1
    
    window.location.href = `?${params.toString()}`;
}

function clearFilters() {
    window.location.href = window.location.pathname;
}

function goToPage(page) {
    const params = new URLSearchParams(window.location.search);
    params.set('page', page);
    window.location.href = `?${params.toString()}`;
}

// Modal Management
const customerModal = document.getElementById('customerModal');
const deleteModal = document.getElementById('deleteModal');
const customerForm = document.getElementById('customerForm');
const deleteForm = document.getElementById('deleteForm');

function showAddModal() {
    // Reset form
    customerForm.reset();
    customerForm.action = '/customers/add/';
    
    // Update modal title and button
    document.getElementById('modalTitle').textContent = 'إضافة عميل جديد';
    document.getElementById('submitText').textContent = 'إضافة العميل';
    
    // Show modal
    customerModal.classList.add('active');
}

function showEditModal(customerId) {
    // Get customer data from the table row
    const row = event.target.closest('tr');
    const name = row.cells[1].textContent.trim();
    const phone = row.querySelector('.fa-phone').nextElementSibling.textContent.trim();
    const emailEl = row.querySelector('.fa-envelope')?.nextElementSibling;
    const email = emailEl ? emailEl.textContent.trim() : '';
    const addressEl = row.querySelector('.fa-map-marker-alt')?.nextElementSibling;
    const address = addressEl ? addressEl.textContent.trim() : '';
    const gender = row.querySelector('.badge').textContent.trim();
    const age = row.cells[7].textContent.trim();
    
    // Fill form
    document.getElementById('customerName').value = name;
    document.getElementById('customerPhone').value = phone;
    document.getElementById('customerEmail').value = email;
    document.getElementById('customerAddress').value = address;
    document.getElementById('customerGender').value = gender;
    document.getElementById('customerAge').value = age === '-' ? '' : age;
    
    // Update form action
    customerForm.action = `/customers/${customerId}/edit/`;
    
    // Update modal title and button
    document.getElementById('modalTitle').textContent = 'تعديل بيانات العميل';
    document.getElementById('submitText').textContent = 'حفظ التعديلات';
    
    // Show modal
    customerModal.classList.add('active');
}

function closeModal() {
    customerModal.classList.remove('active');
    customerForm.reset();
}

function showDeleteModal(customerId, customerName) {
    document.getElementById('deleteCustomerName').textContent = customerName;
    deleteForm.action = `/customers/${customerId}/delete/`;
    deleteModal.classList.add('active');
}

function closeDeleteModal() {
    deleteModal.classList.remove('active');
}

// Close modal on outside click
customerModal?.addEventListener('click', function(e) {
    if (e.target === customerModal) {
        closeModal();
    }
});

deleteModal?.addEventListener('click', function(e) {
    if (e.target === deleteModal) {
        closeDeleteModal();
    }
});

// Phone number validation
const phoneInput = document.getElementById('customerPhone');
phoneInput?.addEventListener('input', function(e) {
    // Remove any non-digit characters
    let value = e.target.value.replace(/\D/g, '');
    
    // Ensure it starts with 5
    if (value && !value.startsWith('5')) {
        value = '5' + value.replace(/^5+/, '');
    }
    
    // Limit to 9 digits
    value = value.substring(0, 9);
    
    e.target.value = value;
});

// Form validation
customerForm?.addEventListener('submit', function(e) {
    const phone = document.getElementById('customerPhone').value;
    
    if (!/^5\d{8}$/.test(phone)) {
        e.preventDefault();
        alert('رقم الجوال يجب أن يبدأ بـ 5 ويتكون من 9 أرقام');
        return false;
    }
});

// Auto-hide messages after 5 seconds
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