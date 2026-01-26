// Sale Add JavaScript - مع دعم الخدمات وضريبة صفرية وعرض فحص النظر

let selectedProducts = [];
let selectedServices = [];
let selectedCustomer = null;

// ============== Customer Functions ==============

function showCustomerSearchModal() {
    document.getElementById('customerSearchModal').classList.add('active');
    document.getElementById('customerSearchModal').style.display = 'flex';
    document.getElementById('customerSearchInput').focus();
}

function closeCustomerSearchModal() {
    document.getElementById('customerSearchModal').classList.remove('active');
    document.getElementById('customerSearchModal').style.display = 'none';
    document.getElementById('customerSearchInput').value = '';
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
    const id = element.getAttribute('data-id');
    const customerId = element.getAttribute('data-customer-id');
    const name = element.getAttribute('data-name');
    const phone = element.getAttribute('data-phone');
    const email = element.getAttribute('data-email') || '';
    
    selectedCustomer = { id, customerId, name, phone, email };
    
    document.getElementById('customer_id').value = id;
    document.getElementById('displayCustomerName').textContent = name;
    document.getElementById('displayCustomerDetails').textContent = `${customerId} | ${phone}${email ? ' | ' + email : ''}`;
    
    document.getElementById('selectedCustomerDisplay').style.display = 'block';
    document.getElementById('searchCustomerBtn').style.display = 'none';
    
    // جلب فحص النظر للعميل
    loadCustomerEyeExam(id);
    
    closeCustomerSearchModal();
}

function removeCustomer() {
    selectedCustomer = null;
    document.getElementById('customer_id').value = '';
    document.getElementById('selectedCustomerDisplay').style.display = 'none';
    document.getElementById('searchCustomerBtn').style.display = 'block';
    
    // إخفاء قسم فحص النظر
    document.getElementById('eyeExamDisplay').style.display = 'none';
    document.getElementById('noExamMessage').style.display = 'none';
}

// ============== Eye Exam Functions ==============

function loadCustomerEyeExam(customerId) {
    // إظهار رسالة تحميل
    const eyeExamDisplay = document.getElementById('eyeExamDisplay');
    const noExamMessage = document.getElementById('noExamMessage');
    
    eyeExamDisplay.style.display = 'none';
    noExamMessage.style.display = 'none';
    
    // جلب البيانات من API
    fetch(`/customers/api/eye-exam/${customerId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('No exam found');
            }
            return response.json();
        })
        .then(data => {
            if (data.exam) {
                displayEyeExam(data.exam);
            } else {
                showNoExamMessage();
            }
        })
        .catch(error => {
            console.error('Error loading eye exam:', error);
            showNoExamMessage();
        });
}

function displayEyeExam(exam) {
    // عرض تاريخ الفحص
    const examDate = new Date(exam.exam_date);
    document.getElementById('examDate').textContent = 
        `${examDate.toLocaleDateString('ar-SA')}`;
    
    // العين اليمنى
    document.getElementById('rightSphere').textContent = exam.right_sphere || '-';
    document.getElementById('rightCylinder').textContent = exam.right_cylinder || '-';
    document.getElementById('rightAxis').textContent = exam.right_axis || '-';
    document.getElementById('rightAdd').textContent = exam.right_add || '-';
    
    // العين اليسرى
    document.getElementById('leftSphere').textContent = exam.left_sphere || '-';
    document.getElementById('leftCylinder').textContent = exam.left_cylinder || '-';
    document.getElementById('leftAxis').textContent = exam.left_axis || '-';
    document.getElementById('leftAdd').textContent = exam.left_add || '-';
    
    // المسافة البؤرية
    document.getElementById('rightPD').textContent = exam.right_pd || '-';
    document.getElementById('leftPD').textContent = exam.left_pd || '-';
    
    // الملاحظات
    const examNotesContainer = document.getElementById('examNotesContainer');
    const examNotes = document.getElementById('examNotes');
    if (exam.notes && exam.notes.trim() !== '') {
        examNotes.textContent = exam.notes;
        examNotesContainer.style.display = 'block';
    } else {
        examNotesContainer.style.display = 'none';
    }
    
    // إظهار قسم الفحص
    document.getElementById('eyeExamDisplay').style.display = 'block';
    document.getElementById('noExamMessage').style.display = 'none';
}

function showNoExamMessage() {
    document.getElementById('eyeExamDisplay').style.display = 'none';
    document.getElementById('noExamMessage').style.display = 'flex';
}

// ============== Product Functions ==============

function showProductSearchModal() {
    document.getElementById('productSearchModal').classList.add('active');
    document.getElementById('productSearchModal').style.display = 'flex';
    document.getElementById('productSearchInput').focus();
}

function closeProductSearchModal() {
    document.getElementById('productSearchModal').classList.remove('active');
    document.getElementById('productSearchModal').style.display = 'none';
    document.getElementById('productSearchInput').value = '';
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
    const id = parseInt(element.getAttribute('data-id'));
    const name = element.getAttribute('data-name');
    const price = parseFloat(element.getAttribute('data-price'));
    const quantity = parseInt(element.getAttribute('data-quantity'));
    const barcode = element.getAttribute('data-barcode');
    
    if (selectedProducts.find(p => p.id === id)) {
        alert('هذا المنتج مضاف مسبقاً');
        return;
    }
    
    if (quantity <= 0) {
        if (!confirm('هذا المنتج غير متوفر في المخزون. هل تريد المتابعة؟')) {
            return;
        }
    }
    
    selectedProducts.push({
        id: id,
        name: name,
        barcode: barcode,
        price: price,
        quantity: 1,
        available: quantity,
        type: 'product'
    });
    
    updateProductsTable();
    calculateTotal();
    
    closeProductSearchModal();
}

// ============== Service Functions ==============

function showServiceSearchModal() {
    document.getElementById('serviceSearchModal').classList.add('active');
    document.getElementById('serviceSearchModal').style.display = 'flex';
    document.getElementById('serviceSearchInput').focus();
}

function closeServiceSearchModal() {
    document.getElementById('serviceSearchModal').classList.remove('active');
    document.getElementById('serviceSearchModal').style.display = 'none';
    document.getElementById('serviceSearchInput').value = '';
    const results = document.querySelectorAll('.service-result-item');
    results.forEach(item => item.style.display = 'flex');
}

function searchServices() {
    const query = document.getElementById('serviceSearchInput').value.toLowerCase().trim();
    const results = document.querySelectorAll('.service-result-item');
    
    results.forEach(item => {
        const text = item.textContent.toLowerCase();
        if (text.includes(query)) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}

function selectService(element) {
    const id = parseInt(element.getAttribute('data-id'));
    const code = element.getAttribute('data-code');
    const name = element.getAttribute('data-name');
    const price = parseFloat(element.getAttribute('data-price'));
    
    if (selectedServices.find(s => s.id === id)) {
        alert('هذه الخدمة مضافة مسبقاً');
        return;
    }
    
    selectedServices.push({
        id: id,
        code: code,
        name: name,
        price: price,
        quantity: 1,
        type: 'service'
    });
    
    updateProductsTable();
    calculateTotal();
    
    closeServiceSearchModal();
}

// ============== Update Table ==============

function updateProductsTable() {
    const tbody = document.getElementById('productsTableBody');
    
    if (selectedProducts.length === 0 && selectedServices.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center; padding: 2rem; color: #7f8c8d;">
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
                    <div style="font-weight: 600;">
                        <i class="fas fa-box" style="color: #4A9EAD; margin-left: 5px;"></i>
                        ${product.name}
                    </div>
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
            <tr style="background: #f0f4ff;">
                <td>
                    <div style="font-weight: 600;">
                        <i class="fas fa-concierge-bell" style="color: #667eea; margin-left: 5px;"></i>
                        ${service.name}
                    </div>
                    <small style="color: #7f8c8d;">${service.code}</small>
                </td>
                <td>
                    <input type="number" 
                           value="${service.price}" 
                           min="0" 
                           step="0.01"
                           onchange="updateServicePrice(${index}, this.value)"
                           style="width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 6px;">
                </td>
                <td style="text-align: center;">
                    <input type="number" 
                           value="${service.quantity}" 
                           min="1"
                           onchange="updateServiceQuantity(${index}, this.value)"
                           style="width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 6px;">
                </td>
                <td style="font-weight: 600; color: #667eea;">${(service.price * service.quantity).toFixed(2)} ر.س</td>
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

// ============== Update Functions ==============

function updateProductPrice(index, price) {
    selectedProducts[index].price = parseFloat(price) || 0;
    updateProductsTable();
    calculateTotal();
}

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

function removeProduct(index) {
    if (confirm('هل تريد حذف هذا المنتج؟')) {
        selectedProducts.splice(index, 1);
        updateProductsTable();
        calculateTotal();
    }
}

function updateServicePrice(index, price) {
    selectedServices[index].price = parseFloat(price) || 0;
    updateProductsTable();
    calculateTotal();
}

function updateServiceQuantity(index, quantity) {
    selectedServices[index].quantity = parseInt(quantity) || 1;
    updateProductsTable();
    calculateTotal();
}

function removeService(index) {
    if (confirm('هل تريد حذف هذه الخدمة؟')) {
        selectedServices.splice(index, 1);
        updateProductsTable();
        calculateTotal();
    }
}

// ============== Calculate Total (ضريبة صفرية) ==============

function calculateTotal() {
    let subtotal = 0;
    
    selectedProducts.forEach(product => {
        subtotal += product.price * product.quantity;
    });
    
    selectedServices.forEach(service => {
        subtotal += service.price * service.quantity;
    });
    
    const discount = parseFloat(document.getElementById('discount')?.value || 0);
    
    // الضريبة صفرية (0%)
    const tax = 0;
    
    // المبلغ الإجمالي = المجموع الفرعي - الخصم (بدون ضريبة)
    const total = subtotal - discount;
    
    document.getElementById('subtotalDisplay').textContent = subtotal.toFixed(2) + ' ر.س';
    document.getElementById('taxDisplay').textContent = tax.toFixed(2) + ' ر.س';
    document.getElementById('totalDisplay').textContent = total.toFixed(2) + ' ر.س';
}

// ============== Form Submit ==============

const saleForm = document.getElementById('saleForm');

saleForm?.addEventListener('submit', function(e) {
    if (!selectedCustomer) {
        e.preventDefault();
        alert('الرجاء اختيار العميل');
        return false;
    }
    
    if (selectedProducts.length === 0 && selectedServices.length === 0) {
        e.preventDefault();
        alert('الرجاء إضافة منتج أو خدمة واحدة على الأقل');
        return false;
    }
    
    const productsData = selectedProducts.map(p => ({
        product_id: p.id,
        quantity: p.quantity,
        unit_price: p.price
    }));
    
    const servicesData = selectedServices.map(s => ({
        service_id: s.id,
        name: s.name,
        price: s.price,
        quantity: s.quantity
    }));
    
    document.getElementById('products').value = JSON.stringify(productsData);
    document.getElementById('services').value = JSON.stringify(servicesData);
});

// ============== Modal Events ==============

document.getElementById('customerSearchModal')?.addEventListener('click', function(e) {
    if (e.target === this) closeCustomerSearchModal();
});

document.getElementById('productSearchModal')?.addEventListener('click', function(e) {
    if (e.target === this) closeProductSearchModal();
});

document.getElementById('serviceSearchModal')?.addEventListener('click', function(e) {
    if (e.target === this) closeServiceSearchModal();
});

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeCustomerSearchModal();
        closeProductSearchModal();
        closeServiceSearchModal();
    }
});

// ============== Initialize ==============

document.addEventListener('DOMContentLoaded', function() {
    updateProductsTable();
    calculateTotal();
    console.log('Sale Add JS loaded with Eye Exam Display and Zero Tax (0%) support');
});