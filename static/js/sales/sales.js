// Sales List JavaScript

// Filter form auto-submit on change (optional)
const filterSelects = document.querySelectorAll('.filters-form select');
filterSelects.forEach(select => {
    select.addEventListener('change', function() {
        // Optional: auto-submit on filter change
        // this.form.submit();
    });
});

// Date filters
const dateInputs = document.querySelectorAll('input[type="date"]');
dateInputs.forEach(input => {
    input.addEventListener('change', function() {
        // Optional: auto-submit on date change
        // this.form.submit();
    });
});

// Confirm delete
function confirmDelete(orderNumber) {
    return confirm(`هل أنت متأكد من حذف الفاتورة ${orderNumber}؟`);
}

// Print invoice
function printInvoice(url) {
    window.open(url, '_blank');
}

// Export to Excel (future feature)
function exportToExcel() {
    alert('هذه الميزة قيد التطوير');
}

console.log('Sales List JS loaded');