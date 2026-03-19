// Thermal Label Printing System - LOGO + PRICE ONLY
// Label specifications: 72mm (W) × 11mm (H)
// Layout: Left tail (blank): 35mm | Right panel (logo + price): 37mm

/**
 * Print single thermal label for a product - Logo and Price only
 * @param {string} barcode - Product barcode (kept for function signature compatibility)
 * @param {string} productName - Product name (not displayed)
 * @param {string} price - Product price
 * @param {string} logoUrl - URL to company logo
 */
function printThermalLabel(barcode, productName, price = '', logoUrl = '/static/images/logo.png') {
    const printWindow = window.open('', '_blank', 'width=400,height=200');
    
    const html = `
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <title>ملصق حراري</title>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                @page {
                    size: 72mm 11mm;
                    margin: 0;
                }
                
                body {
                    font-family: Arial, sans-serif;
                    background: white;
                    width: 72mm;
                    height: 11mm;
                    margin: 0;
                    padding: 0;
                    overflow: hidden;
                }
                
                .thermal-label {
                    width: 72mm;
                    height: 11mm;
                    display: flex;
                    flex-direction: row;
                    background: white;
                }
                
                /* Left tail - completely blank - 35mm */
                .left-tail {
                    width: 35mm;
                    height: 11mm;
                    background: white;
                }
                
                /* Right panel - Logo + Price - 37mm */
                .right-panel {
                    width: 37mm;
                    height: 11mm;
                    display: flex;
                    flex-direction: row;
                    align-items: center;
                    justify-content: center;
                    padding: 0.5mm 1mm;
                    gap: 1.5mm;
                }
                
                .logo-area {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    flex-shrink: 0;
                }
                
                .logo {
                    max-width: 16mm;
                    max-height: 9mm;
                    object-fit: contain;
                }
                
                .divider {
                    width: 0.3mm;
                    height: 8mm;
                    background: #ccc;
                    flex-shrink: 0;
                }
                
                .price-area {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    flex: 1;
                    min-width: 0;
                }
                
                .price {
                    font-size: 8pt;
                    font-weight: bold;
                    color: #000;
                    text-align: center;
                    white-space: nowrap;
                    line-height: 1.1;
                }
                
                .price-currency {
                    font-size: 5pt;
                    color: #444;
                    margin-top: 0.3mm;
                }
                
                @media print {
                    body {
                        margin: 0;
                        padding: 0;
                    }
                    
                    .thermal-label {
                        page-break-after: always;
                    }
                }
            </style>
        </head>
        <body>
            <div class="thermal-label">
                <!-- Left tail - completely blank - 35mm -->
                <div class="left-tail"></div>
                
                <!-- Right panel - Logo + Price - 37mm -->
                <div class="right-panel">
                    <div class="logo-area">
                        <img src="${logoUrl}" alt="Logo" class="logo" onerror="this.style.display='none'">
                    </div>
                    ${price ? `
                    <div class="divider"></div>
                    <div class="price-area">
                        <div class="price">${price}</div>
                        <div class="price-currency">ر.س</div>
                    </div>
                    ` : ''}
                </div>
            </div>
            
            <script>
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
 * Print multiple thermal labels in a sheet - Logo and Price only
 * @param {Array} products - Array of product objects {barcode, name, price}
 * @param {string} logoUrl - URL to company logo
 */
function printMultipleThermalLabels(products, logoUrl = '/static/images/logo.png') {
    if (!products || products.length === 0) {
        alert('لا توجد منتجات للطباعة');
        return;
    }
    
    const printWindow = window.open('', '_blank', 'width=1000,height=800');
    
    let labelsHTML = '';
    products.forEach((product) => {
        labelsHTML += `
            <div class="thermal-label">
                <div class="left-tail"></div>
                <div class="right-panel">
                    <div class="logo-area">
                        <img src="${logoUrl}" alt="Logo" class="logo" onerror="this.style.display='none'">
                    </div>
                    ${product.price ? `
                    <div class="divider"></div>
                    <div class="price-area">
                        <div class="price">${product.price}</div>
                        <div class="price-currency">ر.س</div>
                    </div>
                    ` : ''}
                </div>
            </div>
        `;
    });
    
    const html = `
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <title>ملصقات حرارية - ${products.length} منتج</title>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                @page {
                    size: A4;
                    margin: 5mm;
                }
                
                body {
                    font-family: Arial, sans-serif;
                    background: #f5f5f5;
                    padding: 5mm;
                }
                
                .header {
                    text-align: center;
                    margin-bottom: 5mm;
                    padding: 3mm;
                    background: white;
                    border-radius: 4px;
                }
                
                .header h1 {
                    font-size: 14pt;
                    color: #2c3e50;
                    margin-bottom: 2mm;
                }
                
                .header p {
                    font-size: 9pt;
                    color: #7f8c8d;
                }
                
                .labels-container {
                    display: flex;
                    flex-direction: column;
                    gap: 2mm;
                }
                
                .thermal-label {
                    width: 72mm;
                    height: 11mm;
                    display: flex;
                    flex-direction: row;
                    background: white;
                    page-break-inside: avoid;
                    break-inside: avoid;
                }
                
                .left-tail {
                    width: 35mm;
                    height: 11mm;
                    background: white;
                }
                
                .right-panel {
                    width: 37mm;
                    height: 11mm;
                    display: flex;
                    flex-direction: row;
                    align-items: center;
                    justify-content: center;
                    padding: 0.5mm 1mm;
                    gap: 1.5mm;
                }
                
                .logo-area {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    flex-shrink: 0;
                }
                
                .logo {
                    max-width: 16mm;
                    max-height: 9mm;
                    object-fit: contain;
                }
                
                .divider {
                    width: 0.3mm;
                    height: 8mm;
                    background: #ccc;
                    flex-shrink: 0;
                }
                
                .price-area {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    flex: 1;
                    min-width: 0;
                }
                
                .price {
                    font-size: 8pt;
                    font-weight: bold;
                    color: #000;
                    text-align: center;
                    white-space: nowrap;
                    line-height: 1.1;
                }
                
                .price-currency {
                    font-size: 5pt;
                    color: #444;
                    margin-top: 0.3mm;
                }
                
                .footer {
                    text-align: center;
                    margin-top: 5mm;
                    padding: 3mm;
                    background: white;
                    border-radius: 4px;
                    font-size: 8pt;
                    color: #7f8c8d;
                }
                
                @media print {
                    body {
                        background: white;
                        padding: 0;
                    }
                    
                    .header,
                    .footer {
                        display: none;
                    }
                    
                    .labels-container {
                        gap: 1mm;
                    }
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>ملصقات حرارية للمنتجات</h1>
                <p>إجمالي: ${products.length} ملصق | ${new Date().toLocaleDateString('ar-SA')}</p>
            </div>
            
            <div class="labels-container">
                ${labelsHTML}
            </div>
            
            <div class="footer">
                تم الطباعة من نظام إدارة المخزون
            </div>
            
            <script>
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
 * Print all visible thermal labels from current page
 */
function printAllVisibleThermalLabels() {
    const productCards = document.querySelectorAll('.product-card');
    const products = [];
    
    productCards.forEach(card => {
        const barcode = card.querySelector('.product-barcode')?.textContent.trim();
        const priceElement = card.querySelector('.product-price, .value.price, .price');
        let price = '';
        
        if (priceElement) {
            price = priceElement.textContent.trim().replace('ريال', '').replace('ر.س', '').trim();
        }
        
        if (barcode) {
            products.push({
                barcode: barcode,
                price: price
            });
        }
    });
    
    if (products.length === 0) {
        alert('لا توجد منتجات لطباعة الملصقات');
        return;
    }
    
    printMultipleThermalLabels(products);
}

/**
 * Print thermal label from product detail page
 */
function printThermalLabelFromDetail() {
    const barcodeNumber = document.querySelector('.barcode-number')?.textContent.trim();
    
    let price = '';
    const priceElement = document.querySelector('.info-item .value.price, .selling-price');
    if (priceElement) {
        price = priceElement.textContent.trim().replace('ريال', '').replace('ر.س', '').trim();
    }
    
    // Use logo URL from page if available
    const logoUrl = window.LOGO_URL || '/static/images/logo.png';
    
    if (!barcodeNumber) {
        alert('خطأ في جلب بيانات المنتج');
        return;
    }
    
    printThermalLabel(barcodeNumber, '', price, logoUrl);
}

// Backward compatibility
window.printSingleBarcode = printThermalLabel;
window.printMultipleBarcodes = printMultipleThermalLabels;
window.printAllVisibleBarcodes = printAllVisibleThermalLabels;
window.printBarcodeFromDetail = printThermalLabelFromDetail;

// Export thermal label functions
window.printThermalLabel = printThermalLabel;
window.printMultipleThermalLabels = printMultipleThermalLabels;
window.printAllVisibleThermalLabels = printAllVisibleThermalLabels;
window.printThermalLabelFromDetail = printThermalLabelFromDetail;

console.log('Thermal label printing system (Logo + Price only) loaded successfully');