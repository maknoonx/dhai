// Thermal Label Barcode Printing System - NO BORDERS - LONGER BARCODE VERSION
// Label specifications: 72mm (W) × 11mm (H)
// Adjusted layout: Left tail (blank): 35mm | Middle panel (logo+price): 18mm | Right panel (barcode): 19mm

/**
 * Print single thermal label for a product
 * @param {string} barcode - Product barcode
 * @param {string} productName - Product name (for reference only)
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
            <title>ملصق حراري - ${barcode}</title>
            <script src="https://cdn.jsdelivr.net/npm/jsbarcode@3.11.5/dist/JsBarcode.all.min.js"></script>
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
                
                /* Middle panel - Logo and Price - 18mm */
                .middle-panel {
                    width: 18mm;
                    height: 11mm;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 0.4mm;
                }
                
                .middle-box {
                    width: 100%;
                    height: 100%;
                    background: white;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    gap: 0.3mm;
                    padding: 0.4mm;
                }
                
                .logo {
                    max-width: 11mm;
                    max-height: 4.5mm;
                    object-fit: contain;
                }
                
                .price {
                    font-size: 7.5pt;
                    font-weight: bold;
                    color: #000;
                    text-align: center;
                    white-space: nowrap;
                }
                
                /* Right panel - Barcode - 19mm */
                .right-panel {
                    width: 19mm;
                    height: 11mm;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 0.4mm;
                }
                
                .right-box {
                    width: 100%;
                    height: 100%;
                    background: white;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    gap: 0.2mm;
                    padding: 0.4mm;
                }
                
                .barcode-container {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    width: 100%;
                }
                
                .barcode-svg {
                    width: 17mm;
                    height: 8.5mm;
                }
                
                .barcode-text {
                    font-family: 'Courier New', monospace;
                    font-size: 4pt;
                    font-weight: bold;
                    color: #000;
                    text-align: center;
                    letter-spacing: 0.2px;
                    margin-top: 0.1mm;
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
                
                <!-- Middle panel - Logo and Price - 18mm -->
                <div class="middle-panel">
                    <div class="middle-box">
                        <img src="${logoUrl}" alt="Logo" class="logo" onerror="this.style.display='none'">
                        ${price ? `<div class="price">${price} ر.س</div>` : ''}
                    </div>
                </div>
                
                <!-- Right panel - Barcode - 19mm -->
                <div class="right-panel">
                    <div class="right-box">
                        <div class="barcode-container">
                            <svg class="barcode-svg" id="barcode"></svg>
                            <div class="barcode-text">${barcode}</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
                // Generate barcode with longer lines for better scanning
                try {
                    JsBarcode("#barcode", "${barcode}", {
                        format: "CODE128",
                        width: 1.4,
                        height: 30,
                        displayValue: false,
                        margin: 0,
                        background: "#ffffff",
                        lineColor: "#000000"
                    });
                } catch (error) {
                    console.error('Barcode generation error:', error);
                }
                
                // Auto print
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
 * Print multiple thermal labels in a sheet
 * @param {Array} products - Array of product objects {barcode, name, price}
 * @param {string} logoUrl - URL to company logo
 */
function printMultipleThermalLabels(products, logoUrl = '/static/images/logo.png') {
    if (!products || products.length === 0) {
        alert('لا توجد منتجات للطباعة');
        return;
    }
    
    const printWindow = window.open('', '_blank', 'width=1000,height=800');
    
    // Generate labels HTML
    let labelsHTML = '';
    products.forEach((product, index) => {
        labelsHTML += `
            <div class="thermal-label">
                <!-- Left tail - completely blank -->
                <div class="left-tail"></div>
                
                <!-- Middle panel - Logo and Price -->
                <div class="middle-panel">
                    <div class="middle-box">
                        <img src="${logoUrl}" alt="Logo" class="logo" onerror="this.style.display='none'">
                        ${product.price ? `<div class="price">${product.price} ر.س</div>` : ''}
                    </div>
                </div>
                
                <!-- Right panel - Barcode -->
                <div class="right-panel">
                    <div class="right-box">
                        <div class="barcode-container">
                            <svg class="barcode-svg" id="barcode-${index}"></svg>
                            <div class="barcode-text">${product.barcode}</div>
                        </div>
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
            <title>ملصقات حرارية - ${products.length} منتج</title>
            <script src="https://cdn.jsdelivr.net/npm/jsbarcode@3.11.5/dist/JsBarcode.all.min.js"></script>
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
                
                /* Left tail - completely blank - 35mm */
                .left-tail {
                    width: 35mm;
                    height: 11mm;
                    background: white;
                }
                
                /* Middle panel - Logo and Price - 18mm */
                .middle-panel {
                    width: 18mm;
                    height: 11mm;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 0.4mm;
                }
                
                .middle-box {
                    width: 100%;
                    height: 100%;
                    background: white;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    gap: 0.3mm;
                    padding: 0.4mm;
                }
                
                .logo {
                    max-width: 11mm;
                    max-height: 4.5mm;
                    object-fit: contain;
                }
                
                .price {
                    font-size: 7.5pt;
                    font-weight: bold;
                    color: #000;
                    text-align: center;
                    white-space: nowrap;
                }
                
                /* Right panel - Barcode - 19mm */
                .right-panel {
                    width: 19mm;
                    height: 11mm;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 0.4mm;
                }
                
                .right-box {
                    width: 100%;
                    height: 100%;
                    background: white;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    gap: 0.2mm;
                    padding: 0.4mm;
                }
                
                .barcode-container {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    width: 100%;
                }
                
                .barcode-svg {
                    width: 17mm;
                    height: 8.5mm;
                }
                
                .barcode-text {
                    font-family: 'Courier New', monospace;
                    font-size: 4pt;
                    font-weight: bold;
                    color: #000;
                    text-align: center;
                    letter-spacing: 0.2px;
                    margin-top: 0.1mm;
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
                // Generate all barcodes with longer lines for better scanning
                ${products.map((product, index) => `
                    try {
                        JsBarcode("#barcode-${index}", "${product.barcode}", {
                            format: "CODE128",
                            width: 1.4,
                            height: 30,
                            displayValue: false,
                            margin: 0,
                            background: "#ffffff",
                            lineColor: "#000000"
                        });
                    } catch (error) {
                        console.error('Barcode ${index} generation error:', error);
                    }
                `).join('\n')}
                
                // Auto print
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
    
    if (!barcodeNumber) {
        alert('خطأ في جلب بيانات المنتج');
        return;
    }
    
    printThermalLabel(barcodeNumber, '', price);
}

// Backward compatibility - keep old function names as aliases
window.printSingleBarcode = printThermalLabel;
window.printMultipleBarcodes = printMultipleThermalLabels;
window.printAllVisibleBarcodes = printAllVisibleThermalLabels;
window.printBarcodeFromDetail = printThermalLabelFromDetail;

// Export new thermal label functions
window.printThermalLabel = printThermalLabel;
window.printMultipleThermalLabels = printMultipleThermalLabels;
window.printAllVisibleThermalLabels = printAllVisibleThermalLabels;
window.printThermalLabelFromDetail = printThermalLabelFromDetail;

console.log('Thermal label printing system (NO BORDERS - LONGER BARCODE) loaded successfully');