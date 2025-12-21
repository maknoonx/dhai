// Customers Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initSearch();
    initFilters();
});

/**
 * Initialize search functionality
 */
function initSearch() {
    const searchInput = document.getElementById('searchInput');
    if (!searchInput) return;
    
    // Debounce search to avoid too many requests
    const debouncedSearch = OpticsSystem.debounce(function(value) {
        const url = new URL(window.location.href);
        if (value) {
            url.searchParams.set('search', value);
        } else {
            url.searchParams.delete('search');
        }
        window.location.href = url.toString();
    }, 500);
    
    searchInput.addEventListener('input', function(e) {
        debouncedSearch(e.target.value);
    });
}

/**
 * Initialize filters
 */
function initFilters() {
    const statusFilter = document.getElementById('statusFilter');
    if (!statusFilter) return;
    
    statusFilter.addEventListener('change', function() {
        const url = new URL(window.location.href);
        if (this.value) {
            url.searchParams.set('status', this.value);
        } else {
            url.searchParams.delete('status');
        }
        window.location.href = url.toString();
    });
}

/**
 * Delete customer with confirmation
 */
function deleteCustomer(customerId, customerName) {
    if (!OpticsSystem.confirmAction(`هل أنت متأكد من حذف العميل "${customerName}"؟`)) {
        return;
    }
    
    const form = document.getElementById('deleteForm');
    form.action = `/customers/${customerId}/delete/`;
    form.submit();
}

/**
 * Export customers to Excel (future implementation)
 */
function exportCustomers() {
    // This will be implemented later
    console.log('Exporting customers...');
    alert('سيتم تنفيذ هذه الميزة قريباً');
}

/**
 * Print customers list (future implementation)
 */
function printCustomers() {
    window.print();
}
