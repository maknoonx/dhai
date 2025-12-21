// Settings Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initTabs();
    initModals();
    initFileUpload();
    initLogoUpload();
});

/**
 * Initialize tabs functionality
 */
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            
            // Remove active class from all tabs and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked tab and corresponding content
            this.classList.add('active');
            document.getElementById(targetTab + '-tab').classList.add('active');
            
            // Save active tab to localStorage
            localStorage.setItem('activeSettingsTab', targetTab);
        });
    });
    
    // Restore last active tab
    const savedTab = localStorage.getItem('activeSettingsTab');
    if (savedTab) {
        const savedButton = document.querySelector(`[data-tab="${savedTab}"]`);
        if (savedButton) {
            savedButton.click();
        }
    }
}

/**
 * Initialize modals
 */
function initModals() {
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.classList.remove('active');
        }
    });
    
    // Close modal on Escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            closeAllModals();
        }
    });
}

/**
 * Show payment method modal
 */
function showAddPaymentModal() {
    const modal = document.getElementById('paymentModal');
    if (modal) {
        modal.classList.add('active');
        setTimeout(() => {
            const firstInput = modal.querySelector('input[name="payment_name"]');
            if (firstInput) firstInput.focus();
        }, 100);
    }
}

/**
 * Close payment method modal
 */
function closePaymentModal() {
    const modal = document.getElementById('paymentModal');
    if (modal) {
        modal.classList.remove('active');
        const form = modal.querySelector('form');
        if (form) form.reset();
    }
}

/**
 * Show edit payment method modal
 */
function showEditPaymentModal(id, name, company, percentage) {
    const modal = document.getElementById('editPaymentModal');
    const form = document.getElementById('editPaymentForm');
    
    if (modal && form) {
        // Set form action
        form.action = `/settings/payment/${id}/edit/`;
        
        // Fill form fields
        document.getElementById('edit_payment_name').value = name || '';
        document.getElementById('edit_payment_company').value = company || '';
        document.getElementById('edit_payment_percentage').value = percentage || '';
        
        modal.classList.add('active');
        setTimeout(() => {
            const firstInput = modal.querySelector('input[name="payment_name"]');
            if (firstInput) firstInput.focus();
        }, 100);
    }
}

/**
 * Close edit payment method modal
 */
function closeEditPaymentModal() {
    const modal = document.getElementById('editPaymentModal');
    if (modal) {
        modal.classList.remove('active');
        const form = modal.querySelector('form');
        if (form) form.reset();
    }
}

/**
 * Confirm delete payment method
 */
function confirmDeletePayment(id, name) {
    const modal = document.getElementById('deleteModal');
    const form = document.getElementById('deleteForm');
    const message = document.getElementById('deleteMessage');
    
    if (modal && form && message) {
        message.textContent = `هل أنت متأكد من حذف طريقة الدفع "${name}"؟`;
        form.action = `/settings/payment/${id}/delete/`;
        modal.classList.add('active');
    }
}

/**
 * Show attachment modal
 */
function showAddAttachmentModal() {
    const modal = document.getElementById('attachmentModal');
    if (modal) {
        modal.classList.add('active');
        setTimeout(() => {
            const firstInput = modal.querySelector('input[name="attachment_name"]');
            if (firstInput) firstInput.focus();
        }, 100);
    }
}

/**
 * Close attachment modal
 */
function closeAttachmentModal() {
    const modal = document.getElementById('attachmentModal');
    if (modal) {
        modal.classList.remove('active');
        const form = modal.querySelector('form');
        if (form) form.reset();
    }
}

/**
 * Show edit attachment modal
 */
function showEditAttachmentModal(id, name, description) {
    const modal = document.getElementById('editAttachmentModal');
    const form = document.getElementById('editAttachmentForm');
    
    if (modal && form) {
        // Set form action
        form.action = `/settings/attachment/${id}/edit/`;
        
        // Fill form fields
        document.getElementById('edit_attachment_name').value = name || '';
        document.getElementById('edit_attachment_description').value = description || '';
        
        modal.classList.add('active');
        setTimeout(() => {
            const firstInput = modal.querySelector('input[name="attachment_name"]');
            if (firstInput) firstInput.focus();
        }, 100);
    }
}

/**
 * Close edit attachment modal
 */
function closeEditAttachmentModal() {
    const modal = document.getElementById('editAttachmentModal');
    if (modal) {
        modal.classList.remove('active');
        const form = modal.querySelector('form');
        if (form) form.reset();
    }
}

/**
 * Confirm delete attachment
 */
function confirmDeleteAttachment(id, name) {
    const modal = document.getElementById('deleteModal');
    const form = document.getElementById('deleteForm');
    const message = document.getElementById('deleteMessage');
    
    if (modal && form && message) {
        message.textContent = `هل أنت متأكد من حذف المرفق "${name}"؟`;
        form.action = `/settings/attachment/${id}/delete/`;
        modal.classList.add('active');
    }
}

/**
 * Close delete modal
 */
function closeDeleteModal() {
    const modal = document.getElementById('deleteModal');
    if (modal) {
        modal.classList.remove('active');
    }
}

/**
 * Close all modals
 */
function closeAllModals() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.classList.remove('active');
        const form = modal.querySelector('form');
        if (form) form.reset();
    });
}

/**
 * Initialize file upload preview
 */
function initFileUpload() {
    const fileInput = document.querySelector('input[name="attachment_file"]');
    if (!fileInput) return;
    
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        // Validate file size (10 MB max)
        const maxSize = 10 * 1024 * 1024; // 10 MB in bytes
        if (file.size > maxSize) {
            alert('حجم الملف أكبر من 10 ميجابايت. يرجى اختيار ملف أصغر.');
            e.target.value = '';
            return;
        }
        
        // Validate file type
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            alert('يجب أن يكون الملف بصيغة PDF فقط.');
            e.target.value = '';
            return;
        }
    });
}

/**
 * Initialize logo upload preview
 */
function initLogoUpload() {
    const logoInput = document.getElementById('logoInput');
    const logoPreview = document.getElementById('logoPreview');
    
    if (!logoInput || !logoPreview) return;
    
    logoInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        // Validate file size (2 MB max)
        const maxSize = 2 * 1024 * 1024;
        if (file.size > maxSize) {
            alert('حجم الشعار أكبر من 2 ميجابايت. يرجى اختيار ملف أصغر.');
            e.target.value = '';
            return;
        }
        
        // Validate file type
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/svg+xml'];
        if (!validTypes.includes(file.type)) {
            alert('يجب أن يكون الملف بصيغة JPG, PNG أو SVG فقط.');
            e.target.value = '';
            return;
        }
        
        // Show preview
        const reader = new FileReader();
        reader.onload = function(e) {
            logoPreview.innerHTML = `<img src="${e.target.result}" alt="Logo">`;
        };
        reader.readAsDataURL(file);
    });
}

/**
 * Format file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}