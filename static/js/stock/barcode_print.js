// Barcode Printing Functionality

/**
 * طباعة باركود منتج واحد
 */
function printSingleBarcode(barcode, productName) {
    // Create print window
    const printWindow = window.open('', '_blank', 'width=800,height=600');
    
    // Generate barcode HTML
    const html = `
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <title>طباعة الباركود - ${productName}</title>
            <script src="https://cdn.jsdelivr.net/npm/jsbarcode@3.11.5/dist/JsBarcode.all.min.js"></script>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    padding: 20px;
                    background: white;
                }
                
                .barcode-container {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                    page-break-after: always;
                }
                
                .barcode-label {
                    border: 2px dashed #4A9EAD;
                    padding: 30px;
                    border-radius: 12px;
                    background: white;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                    text-align: center;
                }
                
                .product-name {
                    font-size: 20px;
                    font-weight: bold;
                    color: #2c3e50;
                    margin-bottom: 20px;
                    text-align: center;
                }
                
                .barcode-svg {
                    margin: 20px 0;
                }
                
                .barcode-number {
                    font-family: 'Courier New', monospace;
                    font-size: 18px;
                    font-weight: 600;
                    color: #2c3e50;
                    margin-top: 15px;
                    letter-spacing: 2px;
                }
                
                .print-date {
                    margin-top: 20px;
                    font-size: 12px;
                    color: #7f8c8d;
                    text-align: center;
                }
                
                @media print {
                    body {
                        padding: 0;
                    }
                    
                    .barcode-container {
                        min-height: auto;
                    }
                    
                    .barcode-label {
                        border: 2px solid #4A9EAD;
                        box-shadow: none;
                    }
                }
            </style>
        </head>
        <body>
            <div class="barcode-container">
                <div class="barcode-label">
                    <div class="product-name">${productName}</div>
                    <svg class="barcode-svg" id="barcode"></svg>
                    <div class="barcode-number">${barcode}</div>
                    <div class="print-date">تاريخ الطباعة: ${new Date().toLocaleDateString('ar-SA')}</div>
                </div>
            </div>
            
            <script>
                // Generate barcode
                JsBarcode("#barcode", "${barcode}", {
                    format: "CODE128",
                    width: 3,
                    height: 100,
                    displayValue: false,
                    margin: 10
                });
                
                // Auto print after barcode is generated
                window.onload = function() {
                    setTimeout(function() {
                        window.print();
                        // Optional: close window after print
                        // window.onafterprint = function() { window.close(); };
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
 * طباعة باركودات متعددة
 */
function printMultipleBarcodes(products) {
    if (!products || products.length === 0) {
        alert('لا توجد منتجات للطباعة');
        return;
    }
    
    // Create print window
    const printWindow = window.open('', '_blank', 'width=1200,height=800');
    
    // Generate barcodes HTML
    let barcodesHTML = '';
    products.forEach((product, index) => {
        barcodesHTML += `
            <div class="barcode-item">
                <div class="barcode-label">
                    <div class="product-name">${product.name}</div>
                    <svg class="barcode-svg" id="barcode-${index}"></svg>
                    <div class="barcode-number">${product.barcode}</div>
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
                
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    padding: 20px;
                    background: #f5f5f5;
                }
                
                .header {
                    text-align: center;
                    margin-bottom: 30px;
                    padding: 20px;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                }
                
                .header h1 {
                    color: #4A9EAD;
                    margin-bottom: 10px;
                }
                
                .header p {
                    color: #7f8c8d;
                    font-size: 14px;
                }
                
                .barcodes-grid {
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 20px;
                    margin-bottom: 30px;
                }
                
                .barcode-item {
                    page-break-inside: avoid;
                }
                
                .barcode-label {
                    border: 2px dashed #4A9EAD;
                    padding: 20px;
                    border-radius: 12px;
                    background: white;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
                    text-align: center;
                }
                
                .product-name {
                    font-size: 16px;
                    font-weight: bold;
                    color: #2c3e50;
                    margin-bottom: 15px;
                    min-height: 40px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                
                .barcode-svg {
                    margin: 15px 0;
                }
                
                .barcode-number {
                    font-family: 'Courier New', monospace;
                    font-size: 14px;
                    font-weight: 600;
                    color: #2c3e50;
                    margin-top: 10px;
                    letter-spacing: 1px;
                }
                
                .footer {
                    text-align: center;
                    margin-top: 30px;
                    padding: 20px;
                    background: white;
                    border-radius: 12px;
                    color: #7f8c8d;
                    font-size: 12px;
                }
                
                @media print {
                    body {
                        padding: 10px;
                        background: white;
                    }
                    
                    .header,
                    .footer {
                        box-shadow: none;
                    }
                    
                    .barcodes-grid {
                        gap: 15px;
                    }
                    
                    .barcode-label {
                        border: 2px solid #4A9EAD;
                        box-shadow: none;
                    }
                }
                
                @page {
                    margin: 1cm;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>باركودات المنتجات</h1>
                <p>إجمالي المنتجات: ${products.length} | تاريخ الطباعة: ${new Date().toLocaleDateString('ar-SA')}</p>
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
                        width: 2,
                        height: 60,
                        displayValue: false,
                        margin: 5
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
        
        if (name && barcode) {
            products.push({
                name: name,
                barcode: barcode
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
    
    if (!productName || !barcodeNumber) {
        alert('خطأ في جلب بيانات المنتج');
        return;
    }
    
    printSingleBarcode(barcodeNumber, productName);
}

// Export functions
window.printSingleBarcode = printSingleBarcode;
window.printMultipleBarcodes = printMultipleBarcodes;
window.printAllVisibleBarcodes = printAllVisibleBarcodes;
window.printBarcodeFromDetail = printBarcodeFromDetail;

console.log('Barcode printing functions loaded');