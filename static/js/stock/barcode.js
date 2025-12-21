// Barcode Generation JavaScript

// Function to generate barcode
function generateBarcode(elementId, barcodeValue, options = {}) {
    const defaults = {
        format: "CODE128",
        width: 2,
        height: 80,
        displayValue: false,
        background: "#ffffff",
        lineColor: "#000000"
    };
    
    const settings = { ...defaults, ...options };
    
    try {
        JsBarcode(`#${elementId}`, barcodeValue, settings);
        console.log(`Barcode generated for: ${barcodeValue}`);
    } catch (error) {
        console.error('Error generating barcode:', error);
    }
}

// Function to print barcode
function printBarcode() {
    window.print();
}

// Function to download barcode as image
function downloadBarcode(elementId, filename = 'barcode.png') {
    const svg = document.getElementById(elementId);
    if (!svg) {
        console.error('Barcode element not found');
        return;
    }
    
    // Convert SVG to canvas
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const data = new XMLSerializer().serializeToString(svg);
    const img = new Image();
    
    img.onload = function() {
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0);
        
        // Download
        canvas.toBlob(function(blob) {
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.download = filename;
            link.href = url;
            link.click();
            URL.revokeObjectURL(url);
        });
    };
    
    img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(data)));
}

// Initialize barcodes on page load
document.addEventListener('DOMContentLoaded', function() {
    // Auto-generate barcodes for elements with data-barcode attribute
    const barcodeElements = document.querySelectorAll('[data-barcode]');
    
    barcodeElements.forEach(element => {
        const barcodeValue = element.getAttribute('data-barcode');
        const format = element.getAttribute('data-format') || 'CODE128';
        const width = parseInt(element.getAttribute('data-width')) || 2;
        const height = parseInt(element.getAttribute('data-height')) || 80;
        
        generateBarcode(element.id, barcodeValue, {
            format: format,
            width: width,
            height: height
        });
    });
    
    console.log('Barcode.js loaded successfully');
});

// Export functions for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        generateBarcode,
        printBarcode,
        downloadBarcode
    };
}