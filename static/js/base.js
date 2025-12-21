// Base JavaScript for Optics System

document.addEventListener('DOMContentLoaded', function() {
    // Sidebar Toggle
    initSidebarToggle();
    
    // Auto-hide messages
    autoHideMessages();
    
    // Mobile menu handler
    initMobileMenu();
});

/**
 * Initialize sidebar toggle functionality
 */
function initSidebarToggle() {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebar-toggle');
    const mainContent = document.getElementById('main-content');
    
    if (!sidebar || !toggleBtn) return;
    
    // Load saved state
    const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    if (isCollapsed) {
        sidebar.classList.add('collapsed');
    }
    
    toggleBtn.addEventListener('click', function() {
        sidebar.classList.toggle('collapsed');
        const collapsed = sidebar.classList.contains('collapsed');
        localStorage.setItem('sidebarCollapsed', collapsed);
    });
}

/**
 * Auto-hide success messages after 5 seconds
 */
function autoHideMessages() {
    const messages = document.querySelectorAll('.alert');
    
    messages.forEach(function(message) {
        setTimeout(function() {
            message.style.opacity = '0';
            message.style.transform = 'translateY(-20px)';
            setTimeout(function() {
                message.remove();
            }, 300);
        }, 5000);
    });
}

/**
 * Initialize mobile menu
 */
function initMobileMenu() {
    const sidebar = document.getElementById('sidebar');
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const mobileOverlay = document.getElementById('mobile-overlay');
    
    if (!sidebar || !mobileMenuToggle || !mobileOverlay) return;
    
    // Toggle mobile menu
    mobileMenuToggle.addEventListener('click', function(e) {
        e.stopPropagation();
        sidebar.classList.toggle('mobile-open');
        mobileOverlay.classList.toggle('active');
        document.body.style.overflow = sidebar.classList.contains('mobile-open') ? 'hidden' : '';
    });
    
    // Close menu when clicking overlay
    mobileOverlay.addEventListener('click', function() {
        closeMobileMenu();
    });
    
    // Close menu when clicking nav items
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(function(item) {
        item.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                closeMobileMenu();
            }
        });
    });
    
    // Close menu on window resize if desktop
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            closeMobileMenu();
        }
    });
}

/**
 * Close mobile menu
 */
function closeMobileMenu() {
    const sidebar = document.getElementById('sidebar');
    const mobileOverlay = document.getElementById('mobile-overlay');
    
    if (sidebar) sidebar.classList.remove('mobile-open');
    if (mobileOverlay) mobileOverlay.classList.remove('active');
    document.body.style.overflow = '';
}

/**
 * Confirm dialog helper
 */
function confirmAction(message) {
    return confirm(message || 'هل أنت متأكد من هذا الإجراء؟');
}

/**
 * Format number as currency
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('ar-SA', {
        style: 'currency',
        currency: 'SAR',
        minimumFractionDigits: 0
    }).format(amount);
}

/**
 * Format date to Arabic
 */
function formatDate(date) {
    return new Intl.DateTimeFormat('ar-SA', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(new Date(date));
}

/**
 * Show loading indicator
 */
function showLoading(element) {
    if (!element) return;
    
    const loader = document.createElement('div');
    loader.className = 'loading-spinner';
    loader.innerHTML = `
        <svg class="spinner" viewBox="0 0 50 50">
            <circle cx="25" cy="25" r="20" fill="none" stroke-width="5"></circle>
        </svg>
    `;
    
    element.style.position = 'relative';
    element.appendChild(loader);
}

/**
 * Hide loading indicator
 */
function hideLoading(element) {
    if (!element) return;
    
    const loader = element.querySelector('.loading-spinner');
    if (loader) {
        loader.remove();
    }
}

/**
 * Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Add this to base.css for loading spinner
 */
const loadingStyles = `
.loading-spinner {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.spinner {
    width: 40px;
    height: 40px;
    animation: rotate 1s linear infinite;
}

.spinner circle {
    stroke: var(--secondary-color);
    stroke-linecap: round;
    animation: dash 1.5s ease-in-out infinite;
}

@keyframes rotate {
    100% {
        transform: rotate(360deg);
    }
}

@keyframes dash {
    0% {
        stroke-dasharray: 1, 150;
        stroke-dashoffset: 0;
    }
    50% {
        stroke-dasharray: 90, 150;
        stroke-dashoffset: -35;
    }
    100% {
        stroke-dasharray: 90, 150;
        stroke-dashoffset: -124;
    }
}

.mobile-menu-btn {
    display: none;
    padding: 0.5rem;
    background: transparent;
    border: none;
    cursor: pointer;
    margin-left: 0.5rem;
}

.mobile-menu-btn .icon {
    width: 1.5rem;
    height: 1.5rem;
    stroke: var(--text-primary);
    stroke-width: 2;
}

@media (max-width: 1024px) {
    .mobile-menu-btn {
        display: block;
    }
    
    .sidebar {
        box-shadow: none;
    }
    
    .sidebar.show {
        box-shadow: var(--shadow-lg);
    }
}
`;

// Export functions for use in other scripts
window.OpticsSystem = {
    confirmAction,
    formatCurrency,
    formatDate,
    showLoading,
    hideLoading,
    debounce
};