// Task Manager Pro - Main JavaScript
document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Auto-hide alerts after 5 seconds
    document.querySelectorAll('.alert').forEach(function(alert) {
        setTimeout(function() {
            if (alert.classList.contains('alert-success') || alert.classList.contains('alert-info')) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });
    
    // Add loading state to forms
    document.querySelectorAll('form').forEach(function(form) {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';
                submitBtn.disabled = true;
                
                // Re-enable after 10 seconds as failsafe
                setTimeout(function() {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 10000);
            }
        });
    });
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            // Skip empty or invalid anchors
            if (!href || href === '#' || href.length < 2) {
                return; // Don't prevent default, let normal behavior happen
            }
            
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add fade-in animation to cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.card:not(.fade-in)').forEach(function(card) {
        observer.observe(card);
    });
    
    // Search enhancement
    const searchInputs = document.querySelectorAll('input[type="search"], input[name="search"]');
    searchInputs.forEach(function(input) {
        let searchTimeout;
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(function() {
                // Auto-submit search forms after 500ms of no typing
                const form = input.closest('form');
                if (form && input.value.length >= 2 || input.value.length === 0) {
                    form.submit();
                }
            }, 500);
        });
        
        // Clear search on Escape key
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                this.value = '';
                const form = this.closest('form');
                if (form) {
                    form.submit();
                }
            }
        });
    });
    
    // Status change animations
    document.querySelectorAll('.status-badge').forEach(function(badge) {
        badge.addEventListener('animationend', function() {
            this.style.animation = '';
        });
    });
    
    // Priority badge animations
    document.querySelectorAll('.priority-badge').forEach(function(badge) {
        badge.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05)';
            this.style.transition = 'transform 0.2s ease';
        });
        
        badge.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
    
    // Delete confirmation enhancement
    document.querySelectorAll('button[data-bs-target*="deleteModal"]').forEach(function(btn) {
        btn.addEventListener('click', function() {
            // Add pulse animation for attention
            this.style.animation = 'pulse 0.5s ease-in-out';
            setTimeout(() => {
                this.style.animation = '';
            }, 500);
        });
    });
    
    // Prevent dropdown menu clicks from bubbling
    document.querySelectorAll('.dropdown-menu').forEach(function(menu) {
        menu.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    });
    
    // Task card hover effects
    document.querySelectorAll('.task-card').forEach(function(card) {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-4px)';
            this.style.boxShadow = '0 8px 25px rgba(0,0,0,0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '';
        });
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for quick search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[name="search"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(function(modal) {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) {
                    bsModal.hide();
                }
            });
        }
    });
    
    // Progress bar animations
    document.querySelectorAll('.progress-bar').forEach(function(progressBar) {
        const width = progressBar.style.width;
        progressBar.style.width = '0%';
        setTimeout(function() {
            progressBar.style.width = width;
            progressBar.addEventListener('transitionend', function() {
                if (parseInt(width) >= 100) {
                    progressBar.classList.add('bg-success');
                }
            });
        }, 100);
    });
    
    // Add shortcut hints
    const shortcutsInfo = document.createElement('div');
    shortcutsInfo.innerHTML = `
        <div class="position-fixed bottom-0 end-0 p-3" style="z-index: 1030;">
            <div class="toast" role="alert" aria-live="polite" aria-atomic="true">
                <div class="toast-header">
                    <i class="fas fa-keyboard text-primary me-2"></i>
                    <strong class="me-auto">Keyboard Shortcuts</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
                </div>
                <div class="toast-body">
                    <small>
                        <strong>Ctrl+K:</strong> Quick search<br>
                        <strong>Esc:</strong> Close modals
                    </small>
                </div>
            </div>
        </div>
    `;
    
    // Only show shortcuts hint once per session
    if (!sessionStorage.getItem('shortcuts-shown')) {
        document.body.appendChild(shortcutsInfo);
        const toast = new bootstrap.Toast(document.querySelector('.toast'));
        toast.show();
        sessionStorage.setItem('shortcuts-shown', 'true');
        
        // Remove toast element after dismissal
        document.querySelector('.toast').executeEventListeners('hidden.bs.toast');
        setTimeout(() => {
            shortcutsInfo.remove();
        }, 6000);
    }
    
});

// Utility functions
window.TaskManager = {
    // Show notification
    notify: function(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto-remove after 4 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 4000);
    },
    
    // Show loading overlay
    showLoading: function() {
        const loadingDiv = document.createElement('div');
        loadingDiv.id = 'loading-overlay';
        loadingDiv.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center';
        loadingDiv.style.cssText = 'background: rgba(255,255,255,0.8); z-index: 9999;';
        loadingDiv.innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-primary mb-3" role="status"></div>
                <div class="text-muted">Loading...</div>
            </div>
        `;
        document.body.appendChild(loadingDiv);
    },
    
    // Hide loading overlay
    hideLoading: function() {
        const loadingDiv = document.getElementById('loading-overlay');
        if (loadingDiv) {
            loadingDiv.remove();
        }
    },
    
    // Confirm action
    confirm: function(message, callback) {
        if (confirm(message)) {
            callback();
        }
    }
};

// Global error handler
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.error);
    if (window.TaskManager) {
        window.TaskManager.notify('An error occurred. Please refresh the page.', 'danger');
    }
});

// Service worker registration (for future PWA features) - DISABLED
// Commenting out until PWA features are needed
/*
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registered');
            })
            .catch(function(error) {
                console.log('ServiceWorker registration failed');
            });
    });
}
*/
