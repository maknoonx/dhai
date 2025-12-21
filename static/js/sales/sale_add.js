// Sale Add JavaScript - Fixed Version

let selectedProducts = [];
let selectedServices = [];
let selectedCustomer = null;

// ============== Customer Search Functions ==============

function showCustomerSearchModal() {
    document.getElementById('customerSearchModal').classList.add('active');
    document.getElementById('customerSearchModal').style.display = 'flex';
    document.getElementById('customerSearchInput').focus();
}

function closeCustomerSearchModal() {
    document.getElementById('customerSearchModal').classList.remove('active');
    document.getElementById('customerSearchModal').style.display = 'none';
    document.getElementById('customerSearchInput').value = '';
    // Reset search results
    const results = document.querySelectorAll('.customer-result-item');
    results.forEach(item => item.style.display = 'flex');
}

function searchCustomers() {
    const query = document.getElementById('customerSearchInput').value.toLowerCase().trim();
    const results = document.querySelectorAll('.customer-result-item');
    
    results.forEach(item => {
        const text = item.textContent.toLowerCase();
        if (text.includes(query)) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}

function selectCustomer(element) {
    // Get data from element attributes
    const id = element.getAttribute('data-id');
    const customerId = element.getAttribute('data-customer-id');
    const name = element.getAttribute('data-name');
    const phone = element.getAttribute('data-phone');
    const email = element.getAttribute('data-email') || '';
    
    selectedCustomer = { id, customerId, name, phone, email };
    
    // Update hidden input
    document.getElementById('customer_id').value = id;
    
    // Show selected customer
    document.getElementById('displayCustomerName').textContent = name;
    document.getElementById('displayCustomerDetails').textContent = `${customerId} | ${phone}${email ? ' | ' + email : ''}`;
    
    document.getElementById('selectedCustomerDisplay').style.display = 'block';
    document.getElementById('searchCustomerBtn').style.display = 'none';
    
    closeCustomerSearchModal();
}

function removeCustomer() {
    selectedCustomer = null;
    document.getElementById('customer_id').value = '';
    document.getElementById('selectedCustomerDisplay').style.display = 'none';
    document.getElementById('searchCustomerBtn').style.display = 'block';
}

// ============== Product Search Functions ==============

function showProductSearchModal() {
    document.getElementById('productSearchModal').classList.add('active');
    document.getElementById('productSearchModal').style.display = 'flex';
    document.getElementById('productSearchInput').focus();
}

function closeProductSearchModal() {
    document.getElementById('productSearchModal').classList.remove('active');
    document.getElementById('productSearchModal').style.display = 'none';
    document.getElementById('productSearchInput').value = '';
    // Reset search results
    const results = document.querySelectorAll('.product-result-item');
    results.forEach(item => item.style.display = 'flex');
}

function searchProducts() {
    const query = document.getElementById('productSearchInput').value.toLowerCase().trim();
    const results = document.querySelectorAll('.product-result-item');
    
    results.forEach(item => {
        const text = item.textContent.toLowerCase();
        if (text.includes(query)) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}

function selectProduct(element) {
    // Get data from element attributes
    const id = parseInt(element.getAttribute('data-id'));
    const name = element.getAttribute('data-name');
    const price = parseFloat(element.getAttribute('data-price'));
    const quantity = parseInt(element.getAttribute('data-quantity'));
    const barcode = element.getAttribute('data-barcode');
    
    console.log('Product selected:', { id, name, price, quantity, barcode }); // Debug
    
    // Check if product is already added
    if (selectedProducts.find(p => p.id === id)) {
        alert('هذا المنتج مضاف مسبقاً');
        return;
    }
    
    // Check if product is out of stock
    if (quantity <= 0) {
        if (!confirm('هذا المنتج غير متوفر في المخزون. هل تريد المتابعة؟')) {
            return;
        }
    }
    
    // Add to list
    selectedProducts.push({
        id: id,
        name: name,
        barcode: barcode,
        price: price,
        quantity: 1,
        available: quantity,
        prescription_right: '',
        prescription_left: ''
    });
    
    console.log('Products list:', selectedProducts); // Debug
    
    // Update display
    updateProductsTable();
    calculateTotal();
    
    closeProductSearchModal();
}

// Update Products Table
function updateProductsTable() {
    const tbody = document.getElementById('productsTableBody');
    
    if (selectedProducts.length === 0 && selectedServices.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center; padding: 2rem; color: #7f8c8d;">
                    لم يتم إضافة منتجات أو خدمات
                </td>
            </tr>
        `;
        return;
    }
    
    let html = '';
    
    // Products
    selectedProducts.forEach((product, index) => {
        html += `
            <tr>
                <td>
                    <div style="font-weight: 600;">${product.name}</div>
                    <small style="color: #7f8c8d;">${product.barcode}</small>
                </td>
                <td>
                    <input type="number" 
                           value="${product.price}" 
                           min="0" 
                           step="0.01"
                           onchange="updateProductPrice(${index}, this.value)"
                           style="width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 6px;">
                </td>
                <td>
                    <input type="number" 
                           value="${product.quantity}" 
                           min="1"
                           max="${product.available}"
                           onchange="updateProductQuantity(${index}, this.value)"
                           style="width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 6px;">
                    <small style="color: #7f8c8d; display: block; margin-top: 3px;">متوفر: ${product.available}</small>
                </td>
                <td style="font-weight: 600; color: #4A9EAD;">${(product.price * product.quantity).toFixed(2)} ر.س</td>
                <td>
                    <input type="text"
                           placeholder="قياس يمنى"
                           value="${product.prescription_right}"
                           onchange="updateProductPrescription(${index}, 'right', this.value)"
                           style="width: 100%; padding: 0.4rem; border: 1px solid #ddd; border-radius: 6px; margin-bottom: 3px;">
                    <input type="text"
                           placeholder="قياس يسرى"
                           value="${product.prescription_left}"
                           onchange="updateProductPrescription(${index}, 'left', this.value)"
                           style="width: 100%; padding: 0.4rem; border: 1px solid #ddd; border-radius: 6px;">
                </td>
                <td>
                    <button type="button" 
                            class="btn-remove" 
                            onclick="removeProduct(${index})"
                            title="حذف">
                        <i class="fas fa-times"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    // Services
    selectedServices.forEach((service, index) => {
        html += `
            <tr style="background: #f8f9fa;">
                <td>
                    <div style="font-weight: 600;">${service.name}</div>
                    <small style="color: #7f8c8d;">خدمة إضافية</small>
                </td>
                <td>
                    <input type="number" 
                           value="${service.price}" 
                           min="0" 
                           step="0.01"
                           onchange="updateServicePrice(${index}, this.value)"
                           style="width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 6px;">
                </td>
                <td style="text-align: center;">1</td>
                <td style="font-weight: 600; color: #4A9EAD;">${service.price.toFixed(2)} ر.س</td>
                <td style="text-align: center;">-</td>
                <td>
                    <button type="button" 
                            class="btn-remove" 
                            onclick="removeService(${index})"
                            title="حذف">
                        <i class="fas fa-times"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    tbody.innerHTML = html;
}

// Update Product Price
function updateProductPrice(index, price) {
    selectedProducts[index].price = parseFloat(price) || 0;
    updateProductsTable();
    calculateTotal();
}

// Update Product Quantity
function updateProductQuantity(index, quantity) {
    const qty = parseInt(quantity) || 1;
    const available = selectedProducts[index].available;
    
    if (qty > available) {
        alert(`الكمية المطلوبة أكبر من المتوفر (${available})`);
        selectedProducts[index].quantity = available;
    } else {
        selectedProducts[index].quantity = qty;
    }
    
    updateProductsTable();
    calculateTotal();
}

// Update Product Prescription
function updateProductPrescription(index, eye, value) {
    if (eye === 'right') {
        selectedProducts[index].prescription_right = value;
    } else {
        selectedProducts[index].prescription_left = value;
    }
}

// Remove Product
function removeProduct(index) {
    if (confirm('هل تريد حذف هذا المنتج؟')) {
        selectedProducts.splice(index, 1);
        updateProductsTable();
        calculateTotal();
    }
}

// Update Service Price
function updateServicePrice(index, price) {
    selectedServices[index].price = parseFloat(price) || 0;
    updateProductsTable();
    calculateTotal();
}

// Remove Service
function removeService(index) {
    if (confirm('هل تريد حذف هذه الخدمة؟')) {
        selectedServices.splice(index, 1);
        updateProductsTable();
        calculateTotal();
    }
}

// ============== Service Functions ==============

const serviceModal = document.getElementById('serviceModal');

function addService() {
    document.getElementById('service_name').value = '';
    document.getElementById('service_price').value = '';
    serviceModal.classList.add('active');
    serviceModal.style.display = 'flex';
}

function closeServiceModal() {
    serviceModal.classList.remove('active');
    serviceModal.style.display = 'none';
}

function addServiceToList() {
    const name = document.getElementById('service_name').value.trim();
    const price = parseFloat(document.getElementById('service_price').value) || 0;
    
    if (!name) {
        alert('الرجاء إدخال اسم الخدمة');
        return;
    }
    
    if (price <= 0) {
        alert('الرجاء إدخال سعر صحيح');
        return;
    }
    
    selectedServices.push({
        name: name,
        price: price
    });
    
    updateProductsTable();
    calculateTotal();
    closeServiceModal();
}

// ============== Calculate Total ==============

function calculateTotal() {
    // Subtotal
    let subtotal = 0;
    
    selectedProducts.forEach(product => {
        subtotal += product.price * product.quantity;
    });
    
    selectedServices.forEach(service => {
        subtotal += service.price;
    });
    
    // Discount
    const discount = parseFloat(document.getElementById('discount')?.value || 0);
    
    // Tax (15%)
    const taxableAmount = subtotal - discount;
    const tax = taxableAmount > 0 ? taxableAmount * 0.15 : 0;
    
    // Total
    const total = subtotal - discount + tax;
    
    // Update display
    document.getElementById('subtotalDisplay').textContent = subtotal.toFixed(2) + ' ر.س';
    document.getElementById('taxDisplay').textContent = tax.toFixed(2) + ' ر.س';
    document.getElementById('totalDisplay').textContent = total.toFixed(2) + ' ر.س';
}

// ============== Form Submit ==============

const saleForm = document.getElementById('saleForm');

saleForm?.addEventListener('submit', function(e) {
    // Validate customer
    if (!selectedCustomer) {
        e.preventDefault();
        alert('الرجاء اختيار العميل');
        return false;
    }
    
    // Validate products/services
    if (selectedProducts.length === 0 && selectedServices.length === 0) {
        e.preventDefault();
        alert('الرجاء إضافة منتج أو خدمة واحدة على الأقل');
        return false;
    }
    
    // Prepare data
    const productsData = selectedProducts.map(p => ({
        product_id: p.id,
        quantity: p.quantity,
        unit_price: p.price,
        prescription_right: p.prescription_right,
        prescription_left: p.prescription_left
    }));
    
    const servicesData = selectedServices.map(s => ({
        name: s.name,
        price: s.price
    }));
    
    // Set hidden fields
    document.getElementById('products').value = JSON.stringify(productsData);
    document.getElementById('services').value = JSON.stringify(servicesData);
    
    console.log('Submitting products:', productsData); // Debug
    console.log('Submitting services:', servicesData); // Debug
});

// ============== Modal Close Events ==============

// Close modals on outside click
document.getElementById('customerSearchModal')?.addEventListener('click', function(e) {
    if (e.target === this) {
        closeCustomerSearchModal();
    }
});

document.getElementById('productSearchModal')?.addEventListener('click', function(e) {
    if (e.target === this) {
        closeProductSearchModal();
    }
});

serviceModal?.addEventListener('click', function(e) {
    if (e.target === serviceModal) {
        closeServiceModal();
    }
});

// Close on Escape
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeCustomerSearchModal();
        closeProductSearchModal();
        closeServiceModal();
    }
});

// ============== Initialize ==============

document.addEventListener('DOMContentLoaded', function() {
    updateProductsTable();
    calculateTotal();
    console.log('Sale Add JS loaded');
});