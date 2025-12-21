// Import Products JavaScript

const fileInput = document.getElementById('file');
const fileUploadArea = document.getElementById('fileUploadArea');
const selectedFileDiv = document.getElementById('selectedFile');
const submitBtn = document.getElementById('submitBtn');
const uploadForm = document.getElementById('uploadForm');
const uploadProgress = document.getElementById('uploadProgress');

// File input change
fileInput?.addEventListener('change', function(e) {
    handleFile(this.files[0]);
});

// Drag and drop
fileUploadArea?.addEventListener('dragover', function(e) {
    e.preventDefault();
    this.classList.add('drag-over');
});

fileUploadArea?.addEventListener('dragleave', function(e) {
    e.preventDefault();
    this.classList.remove('drag-over');
});

fileUploadArea?.addEventListener('drop', function(e) {
    e.preventDefault();
    this.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

// Click to upload
fileUploadArea?.addEventListener('click', function() {
    fileInput?.click();
});

function handleFile(file) {
    if (!file) return;
    
    // Check file type
    const allowedTypes = [
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/csv'
    ];
    
    if (!allowedTypes.includes(file.type) && !file.name.match(/\.(xlsx|xls|csv)$/i)) {
        alert('يرجى اختيار ملف Excel أو CSV');
        return;
    }
    
    // Show file info
    document.getElementById('fileName').textContent = file.name;
    document.getElementById('fileSize').textContent = formatFileSize(file.size);
    
    fileUploadArea.style.display = 'none';
    selectedFileDiv.style.display = 'flex';
    submitBtn.disabled = false;
}

function removeFile() {
    fileInput.value = '';
    fileUploadArea.style.display = 'block';
    selectedFileDiv.style.display = 'none';
    submitBtn.disabled = true;
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
}

// Form submission
uploadForm?.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> جاري الرفع...';
    uploadProgress.style.display = 'block';
    
    // Simulate progress (in real app, use xhr.upload.onprogress)
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += 10;
        document.getElementById('progressFill').style.width = progress + '%';
        
        if (progress >= 90) {
            clearInterval(progressInterval);
        }
    }, 200);
    
    fetch(this.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': formData.get('csrfmiddlewaretoken')
        }
    })
    .then(response => response.text())
    .then(html => {
        clearInterval(progressInterval);
        document.getElementById('progressFill').style.width = '100%';
        
        setTimeout(() => {
            // Reload page with results
            document.open();
            document.write(html);
            document.close();
        }, 500);
    })
    .catch(error => {
        clearInterval(progressInterval);
        console.error('Error:', error);
        alert('حدث خطأ أثناء رفع الملف');
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-upload"></i> رفع واستيراد المنتجات';
        uploadProgress.style.display = 'none';
    });
});

console.log('Import products JS loaded');