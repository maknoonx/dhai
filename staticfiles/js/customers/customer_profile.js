// Customer Profile JavaScript - FINAL VERSION

console.log('Loading customer profile JS...');

// Modal Management
const examModal = document.getElementById('examModal');

function showAddExamModal() {
    console.log('showAddExamModal called');
    if (document.getElementById('examModalTitle')) {
        document.getElementById('examModalTitle').textContent = 'إضافة فحص نظر جديد';
    }
    if (examModal) {
        examModal.classList.add('active');
    }
}

function showEditExamModal() {
    console.log('showEditExamModal called');
    if (document.getElementById('examModalTitle')) {
        document.getElementById('examModalTitle').textContent = 'تعديل الفحص الطبي للنظر';
    }
    if (examModal) {
        examModal.classList.add('active');
    }
}

function closeExamModal() {
    console.log('closeExamModal called');
    if (examModal) {
        examModal.classList.remove('active');
    }
}

// Close modal on outside click
if (examModal) {
    examModal.addEventListener('click', function(e) {
        if (e.target === examModal) {
            closeExamModal();
        }
    });
}

// Close modal on Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeExamModal();
    }
});

// Auto-hide success messages
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded');
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

// Form validation for exam inputs
const examForm = document.querySelector('#examModal form');
if (examForm) {
    examForm.addEventListener('submit', function(e) {
        console.log('Submitting exam form...');
    });
}

// Smooth scroll to sections
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Print customer profile
function printProfile() {
    window.print();
}

// Export customer data
function exportCustomerData() {
    alert('ميزة التصدير ستكون متاحة قريباً');
}

console.log('Customer Profile JS loaded successfully!');
console.log('Functions available:', {
    showAddExamModal: typeof showAddExamModal,
    showEditExamModal: typeof showEditExamModal,
    closeExamModal: typeof closeExamModal
});