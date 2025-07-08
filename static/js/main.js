// Main JavaScript file for Insurance Tracker Portal

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Confirm delete actions
    document.querySelectorAll('[data-confirm]').forEach(function(element) {
        element.addEventListener('click', function(e) {
            var message = this.getAttribute('data-confirm') || 'Are you sure?';
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });

    // Form validation enhancements
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // File upload preview
    document.querySelectorAll('input[type="file"]').forEach(function(input) {
        input.addEventListener('change', function() {
            var files = this.files;
            var preview = this.parentNode.querySelector('.file-preview');
            
            if (preview) {
                preview.innerHTML = '';
                
                for (var i = 0; i < files.length; i++) {
                    var file = files[i];
                    var fileInfo = document.createElement('div');
                    fileInfo.className = 'file-info';
                    fileInfo.innerHTML = `
                        <small class="text-muted">
                            <i class="fas fa-file"></i> ${file.name} (${formatFileSize(file.size)})
                        </small>
                    `;
                    preview.appendChild(fileInfo);
                }
            }
        });
    });

    // Search functionality
    var searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(function(input) {
        var searchTimeout;
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(function() {
                // Auto-submit search form after 500ms of inactivity
                var form = input.closest('form');
                if (form) {
                    form.submit();
                }
            }, 500);
        });
    });

    // Dashboard statistics animation
    animateCounters();

    // Policy expiry warnings
    checkPolicyExpiry();

    // Notification management
    initializeNotifications();
});

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    var k = 1024;
    var sizes = ['Bytes', 'KB', 'MB', 'GB'];
    var i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Animate counter numbers
function animateCounters() {
    var counters = document.querySelectorAll('.counter');
    counters.forEach(function(counter) {
        var target = parseInt(counter.textContent);
        var current = 0;
        var increment = target / 100;
        var duration = 2000; // 2 seconds
        var stepTime = duration / 100;
        
        var timer = setInterval(function() {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            counter.textContent = Math.floor(current);
        }, stepTime);
    });
}

// Check for policy expiry warnings
function checkPolicyExpiry() {
    var expiryWarnings = document.querySelectorAll('.expiry-warning');
    expiryWarnings.forEach(function(warning) {
        var expiryDate = new Date(warning.getAttribute('data-expiry'));
        var today = new Date();
        var daysLeft = Math.ceil((expiryDate - today) / (1000 * 60 * 60 * 24));
        
        if (daysLeft <= 0) {
            warning.classList.add('expired');
            warning.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Expired';
        } else if (daysLeft <= 30) {
            warning.classList.add('expiring-soon');
            warning.innerHTML = `<i class="fas fa-exclamation-triangle"></i> Expires in ${daysLeft} day${daysLeft > 1 ? 's' : ''}`;
        }
    });
}

// Initialize notification system
function initializeNotifications() {
    // Mark notifications as read when clicked
    document.querySelectorAll('.notification-item').forEach(function(item) {
        item.addEventListener('click', function() {
            var notificationId = this.getAttribute('data-notification-id');
            if (notificationId) {
                markNotificationAsRead(notificationId);
            }
        });
    });
}

// Mark notification as read
function markNotificationAsRead(notificationId) {
    fetch(`/notifications/mark_read/${notificationId}`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken()
        }
    }).then(function(response) {
        if (response.ok) {
            var notification = document.querySelector(`[data-notification-id="${notificationId}"]`);
            if (notification) {
                notification.classList.add('read');
            }
        }
    });
}

// Get CSRF token from meta tag or form
function getCsrfToken() {
    var token = document.querySelector('meta[name="csrf-token"]');
    if (token) {
        return token.getAttribute('content');
    }
    
    var form = document.querySelector('form');
    if (form) {
        var hiddenInput = form.querySelector('input[name="csrf_token"]');
        if (hiddenInput) {
            return hiddenInput.value;
        }
    }
    
    return '';
}

// Loading state management
function showLoading(element) {
    if (element) {
        element.disabled = true;
        element.classList.add('loading');
        var originalText = element.textContent;
        element.setAttribute('data-original-text', originalText);
        element.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
    }
}

function hideLoading(element) {
    if (element) {
        element.disabled = false;
        element.classList.remove('loading');
        var originalText = element.getAttribute('data-original-text');
        if (originalText) {
            element.textContent = originalText;
        }
    }
}

// Form submission helpers
function handleFormSubmission(form, onSuccess, onError) {
    var submitButton = form.querySelector('button[type="submit"]');
    showLoading(submitButton);
    
    var formData = new FormData(form);
    
    fetch(form.action, {
        method: 'POST',
        body: formData
    }).then(function(response) {
        hideLoading(submitButton);
        
        if (response.ok) {
            if (onSuccess) onSuccess(response);
        } else {
            if (onError) onError(response);
        }
    }).catch(function(error) {
        hideLoading(submitButton);
        if (onError) onError(error);
    });
}

// Utility functions
function showToast(message, type = 'info') {
    var toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(function() {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 5000);
}

// Export functions for use in other scripts
window.InsuranceTracker = {
    showLoading: showLoading,
    hideLoading: hideLoading,
    showToast: showToast,
    formatFileSize: formatFileSize,
    markNotificationAsRead: markNotificationAsRead
};
