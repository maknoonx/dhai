// Barcode Printing Functionality

/**
 * طباعة باركود منتج واحد - أقسام متساوية
 */
function printSingleBarcode(barcode, productName, price = '') {
    // Create print window
    const printWindow = window.open('', '_blank', 'width=400,height=300');
    
    // Generate barcode HTML with equal sections, no product name
    const html = `
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <title>باركود - ${barcode}</title>
            <script src="https://cdn.jsdelivr.net/npm/jsbarcode@3.11.5/dist/JsBarcode.all.min.js"></script>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                @page {
                    size: 60mm 40mm;
                    margin: 2mm;
                }
                
                body {
                    font-family: Arial, sans-serif;
                    background: white;
                    width: 60mm;
                    height: 40mm;
                    margin: 0 auto;
                    padding: 2mm;
                }
                
                .barcode-label {
                    width: 100%;
                    height: 100%;
                    border: 1px solid #000;
                    display: flex;
                    background: white;
                }
                
                /* القسم الأيمن: الباركود فقط */
                .right-section {
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    padding: 2mm;
                    border-left: 1px solid #ddd;
                }
                
                .barcode-container {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    width: 100%;
                }
                
                .barcode-svg {
                    width: 100%;
                    max-width: 26mm;
                }
                
                .barcode-number {
                    font-family: 'Courier New', monospace;
                    font-size: 7pt;
                    font-weight: bold;
                    color: #000;
                    margin-top: 2mm;
                    letter-spacing: 0.3px;
                    text-align: center;
                }
                
                /* القسم الأيسر: الشعار والسعر */
                .left-section {
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    align-items: center;
                    padding: 2mm;
                }
                
                .logo-container {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    flex: 1;
                }
                
                .logo {
                    max-width: 24mm;
                    max-height: 18mm;
                    object-fit: contain;
                }
                
                .price-container {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    flex: 1;
                    border-top: 1px solid #ddd;
                    width: 100%;
                    padding-top: 2mm;
                }
                
                .price {
                    font-size: 12pt;
                    font-weight: bold;
                    color: #000;
                    text-align: center;
                }
                
                .price-label {
                    font-size: 7pt;
                    color: #666;
                    margin-top: 1mm;
                }
                
                @media print {
                    body {
                        padding: 0;
                        margin: 0;
                    }
                    
                    .barcode-label {
                        border: 1px solid #000;
                    }
                }
            </style>
        </head>
        <body>
            <div class="barcode-label">
                <!-- القسم الأيمن: الباركود فقط -->
                <div class="right-section">
                    <div class="barcode-container">
                        <svg class="barcode-svg" id="barcode"></svg>
                        <div class="barcode-number">${barcode}</div>
                    </div>
                </div>
                
                <!-- القسم الأيسر: الشعار والسعر -->
                <div class="left-section">
                    <div class="logo-container">
                        <img src="/static/images/logo.png" alt="Logo" class="logo" onerror="this.style.display='none'">
                    </div>
                    ${price ? `
                    <div class="price-container">
                        <div class="price">${price}</div>
                        <div class="price-label">ر.س</div>
                    </div>
                    ` : ''}
                </div>
            </div>
            
            <script>
                // Generate barcode
                JsBarcode("#barcode", "${barcode}", {
                    format: "CODE128",
                    width: 1.5,
                    height: 35,
                    displayValue: false,
                    margin: 0
                });
                
                // Auto print after barcode is generated
                window.onload = function() {
                    setTimeout(function() {
                        window.print();
                    }, 500);
                };
            </script>
        </body>
        </html>
    `;
    
    printWindow.document.write(html);
    printWindow.document.close();
}

/**
 * طباعة باركودات متعددة - أقسام متساوية
 */
function printMultipleBarcodes(products) {
    if (!products || products.length === 0) {
        alert('لا توجد منتجات للطباعة');
        return;
    }
    
    // Create print window
    const printWindow = window.open('', '_blank', 'width=1000,height=800');
    
    // Generate barcodes HTML
    let barcodesHTML = '';
    products.forEach((product, index) => {
        barcodesHTML += `
            <div class="barcode-item">
                <div class="barcode-label">
                    <!-- القسم الأيمن: الباركود فقط -->
                    <div class="right-section">
                        <div class="barcode-container">
                            <svg class="barcode-svg" id="barcode-${index}"></svg>
                            <div class="barcode-number">${product.barcode}</div>
                        </div>
                    </div>
                    
                    <!-- القسم الأيسر: الشعار والسعر -->
                    <div class="left-section">
                        <div class="logo-container">
                            <img src="/static/images/logo.png" alt="Logo" class="logo" onerror="this.style.display='none'">
                        </div>
                        ${product.price ? `
                        <div class="price-container">
                            <div class="price">${product.price}</div>
                            <div class="price-label">ر.س</div>
                        </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    });
    
    const html = `
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <title>طباعة باركودات المنتجات</title>
            <script src="https://cdn.jsdelivr.net/npm/jsbarcode@3.11.5/dist/JsBarcode.all.min.js"></script>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                @page {
                    size: A4;
                    margin: 10mm;
                }
                
                body {
                    font-family: Arial, sans-serif;
                    background: #f5f5f5;
                    padding: 10mm;
                }
                
                .header {
                    text-align: center;
                    margin-bottom: 10mm;
                    padding: 5mm;
                    background: white;
                    border-radius: 8px;
                }
                
                .header h1 {
                    font-size: 18pt;
                    color: #2c3e50;
                    margin-bottom: 3mm;
                }
                
                .header p {
                    font-size: 10pt;
                    color: #7f8c8d;
                }
                
                .barcodes-grid {
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 5mm;
                }
                
                .barcode-item {
                    page-break-inside: avoid;
                    break-inside: avoid;
                }
                
                .barcode-label {
                    width: 100%;
                    height: 40mm;
                    border: 1px solid #000;
                    display: flex;
                    background: white;
                }
                
                /* القسم الأيمن: الباركود فقط */
                .right-section {
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    padding: 2mm;
                    border-left: 1px solid #ddd;
                }
                
                .barcode-container {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    width: 100%;
                }
                
                .barcode-svg {
                    width: 100%;
                    max-width: 26mm;
                }
                
                .barcode-number {
                    font-family: 'Courier New', monospace;
                    font-size: 6pt;
                    font-weight: bold;
                    color: #000;
                    margin-top: 2mm;
                    letter-spacing: 0.3px;
                    text-align: center;
                }
                
                /* القسم الأيسر: الشعار والسعر */
                .left-section {
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    align-items: center;
                    padding: 2mm;
                }
                
                .logo-container {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    flex: 1;
                }
                
                .logo {
                    max-width: 22mm;
                    max-height: 16mm;
                    object-fit: contain;
                }
                
                .price-container {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    flex: 1;
                    border-top: 1px solid #ddd;
                    width: 100%;
                    padding-top: 2mm;
                }
                
                .price {
                    font-size: 11pt;
                    font-weight: bold;
                    color: #000;
                    text-align: center;
                }
                
                .price-label {
                    font-size: 6pt;
                    color: #666;
                    margin-top: 1mm;
                }
                
                .footer {
                    text-align: center;
                    margin-top: 10mm;
                    padding: 5mm;
                    background: white;
                    border-radius: 8px;
                    font-size: 9pt;
                    color: #7f8c8d;
                }
                
                @media print {
                    body {
                        background: white;
                        padding: 0;
                    }
                    
                    .header,
                    .footer {
                        box-shadow: none;
                    }
                    
                    .barcodes-grid {
                        gap: 3mm;
                    }
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>باركودات المنتجات</h1>
                <p>إجمالي: ${products.length} منتج | ${new Date().toLocaleDateString('ar-SA')}</p>
            </div>
            
            <div class="barcodes-grid">
                ${barcodesHTML}
            </div>
            
            <div class="footer">
                تم الطباعة من نظام إدارة المخزون
            </div>
            
            <script>
                // Generate all barcodes
                ${products.map((product, index) => `
                    JsBarcode("#barcode-${index}", "${product.barcode}", {
                        format: "CODE128",
                        width: 1.5,
                        height: 35,
                        displayValue: false,
                        margin: 0
                    });
                `).join('\n')}
                
                // Auto print after all barcodes are generated
                window.onload = function() {
                    setTimeout(function() {
                        window.print();
                    }, 1000);
                };
            </script>
        </body>
        </html>
    `;
    
    printWindow.document.write(html);
    printWindow.document.close();
}

/**
 * جلب وطباعة جميع الباركودات من الصفحة الحالية
 */
function printAllVisibleBarcodes() {
    const productCards = document.querySelectorAll('.product-card');
    const products = [];
    
    productCards.forEach(card => {
        const name = card.querySelector('.product-name')?.textContent.trim();
        const barcode = card.querySelector('.product-barcode')?.textContent.trim();
        const priceElement = card.querySelector('.product-price, .value.price');
        let price = '';
        
        if (priceElement) {
            price = priceElement.textContent.trim().replace('ريال', '').replace('ر.س', '').trim();
        }
        
        if (name && barcode) {
            products.push({
                name: name,
                barcode: barcode,
                price: price
            });
        }
    });
    
    if (products.length === 0) {
        alert('لا توجد منتجات لطباعة الباركود');
        return;
    }
    
    printMultipleBarcodes(products);
}

/**
 * طباعة باركود من زر في صفحة التفاصيل
 */
function printBarcodeFromDetail() {
    const productName = document.querySelector('.page-header h1')?.textContent.trim();
    const barcodeNumber = document.querySelector('.barcode-number')?.textContent.trim();
    
    // محاولة جلب السعر من صفحة التفاصيل
    let price = '';
    const priceElement = document.querySelector('.info-item .value.price, .selling-price');
    if (priceElement) {
        price = priceElement.textContent.trim().replace('ريال', '').replace('ر.س', '').trim();
    }
    
    if (!productName || !barcodeNumber) {
        alert('خطأ في جلب بيانات المنتج');
        return;
    }
    
    printSingleBarcode(barcodeNumber, productName, price);
}

// Export functions
window.printSingleBarcode = printSingleBarcode;
window.printMultipleBarcodes = printMultipleBarcodes;
window.printAllVisibleBarcodes = printAllVisibleBarcodes;
window.printBarcodeFromDetail = printBarcodeFromDetail;

console.log('Barcode printing functions loaded');