// Global variables
const API_BASE_URL = '/api';
let globalStatus = {
    status: 'active',
    last_run_time: null,
    next_run_time: null,
    api_calls_this_month: 0
};

// Initialize app when DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeModals();
    fetchAndUpdateStatus();
    
    // Set up periodic refresh for status
    setInterval(fetchAndUpdateStatus, 60000); // Refresh every minute
});

/**
 * Initialize modal functionality
 */
function initializeModals() {
    // Get all modals
    const modals = document.querySelectorAll('.modal');
    const closeButtons = document.querySelectorAll('.close-modal');
    
    // Add event listeners to close buttons
    closeButtons.forEach(button => {
        button.addEventListener('click', () => {
            modals.forEach(modal => {
                modal.classList.remove('active');
            });
        });
    });
    
    // Close modal when clicking outside of modal content
    modals.forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });
    });
    
    // Close modals on escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            modals.forEach(modal => {
                modal.classList.remove('active');
            });
        }
    });
}

/**
 * Show a modal by ID
 * @param {string} modalId - ID of the modal to show
 */
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
}

/**
 * Fetch and update application status
 */
function fetchAndUpdateStatus() {
    fetch(`${API_BASE_URL}/status`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            updateStatusDisplay(data.status);
            updateActivityList(data.recent_activity);
            globalStatus = data.status;
        })
        .catch(error => {
            console.error('Error fetching status:', error);
            showError('Failed to fetch application status. Please try again later.');
        });
}

/**
 * Update the status display with current data
 * @param {Object} status - Status data
 */
function updateStatusDisplay(status) {
    const statusElement = document.getElementById('current-status');
    const nextUpdateElement = document.getElementById('next-update');
    const apiUsageText = document.getElementById('api-usage-text');
    const apiUsageCount = document.getElementById('api-usage-count');
    const apiUsageBar = document.getElementById('api-usage-bar');
    
    // Update status text
    statusElement.textContent = `${capitalizeFirstLetter(status.status)}`;
    statusElement.className = status.status;
    
    // Update next update time
    if (status.next_run_time) {
        const nextDate = new Date(status.next_run_time);
        nextUpdateElement.textContent = `Next update scheduled for: ${formatDateTime(nextDate)}`;
    } else {
        nextUpdateElement.textContent = 'No updates scheduled';
    }
    
    // Update API usage
    apiUsageCount.textContent = `${status.api_calls_this_month}/100`;
    const usagePercentage = Math.min(status.api_calls_this_month, 100);
    apiUsageBar.style.width = `${usagePercentage}%`;
    
    // Change color based on usage
    if (usagePercentage > 80) {
        apiUsageBar.style.backgroundColor = 'var(--error-color)';
    } else if (usagePercentage > 60) {
        apiUsageBar.style.backgroundColor = 'var(--warning-color)';
    } else {
        apiUsageBar.style.backgroundColor = 'var(--primary-color)';
    }
}

/**
 * Update the activity list with recent activities
 * @param {Array} activities - List of recent activities
 */
function updateActivityList(activities) {
    const activityList = document.getElementById('activity-list');
    
    // Clear existing items
    activityList.innerHTML = '';
    
    // Add new items
    if (activities && activities.length > 0) {
        activities.forEach(activity => {
            const activityItem = document.createElement('li');
            activityItem.className = `activity-item ${activity.status}`;
            
            // Choose icon based on status
            let icon = '';
            switch (activity.status) {
                case 'success':
                    icon = 'fas fa-check-circle';
                    break;
                case 'error':
                    icon = 'fas fa-exclamation-circle';
                    break;
                case 'warning':
                    icon = 'fas fa-exclamation-triangle';
                    break;
                default:
                    icon = 'fas fa-info-circle';
            }
            
            // Format date
            const activityDate = new Date(activity.timestamp);
            const timeAgo = getTimeAgo(activityDate);
            
            // Create activity HTML
            activityItem.innerHTML = `
                <span class="activity-icon"><i class="${icon}"></i></span>
                <div class="activity-content">
                    <p class="activity-message">${activity.message}</p>
                    <span class="activity-time">${timeAgo}</span>
                </div>
            `;
            
            activityList.appendChild(activityItem);
        });
    } else {
        // Show message if no activities
        const emptyItem = document.createElement('li');
        emptyItem.className = 'activity-item';
        emptyItem.innerHTML = `
            <div class="activity-content">
                <p class="activity-message">No recent activity</p>
            </div>
        `;
        activityList.appendChild(emptyItem);
    }
}

/**
 * Show error message to the user
 * @param {string} message - Error message to display
 */
function showError(message) {
    // You can implement a toast notification system here
    console.error(message);
    // For now, just alert
    alert(`Error: ${message}`);
}

/**
 * Show success message to the user
 * @param {string} message - Success message to display
 */
function showSuccess(message) {
    // You can implement a toast notification system here
    console.log(message);
    // For now, just alert
    alert(message);
}

/**
 * Show confirmation dialog
 * @param {string} message - Confirmation message
 * @param {Function} onConfirm - Function to call on confirmation
 */
function showConfirmation(message, onConfirm) {
    const confirmModal = document.getElementById('confirm-modal');
    const confirmMessage = document.getElementById('confirm-message');
    const confirmBtn = document.getElementById('confirm-btn');
    const cancelBtn = document.getElementById('cancel-confirm-btn');
    
    // Set message
    confirmMessage.textContent = message;
    
    // Remove previous event listeners
    const newConfirmBtn = confirmBtn.cloneNode(true);
    confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
    
    const newCancelBtn = cancelBtn.cloneNode(true);
    cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn);
    
    // Add new event listeners
    newConfirmBtn.addEventListener('click', () => {
        onConfirm();
        confirmModal.classList.remove('active');
    });
    
    newCancelBtn.addEventListener('click', () => {
        confirmModal.classList.remove('active');
    });
    
    // Show modal
    confirmModal.classList.add('active');
}

/**
 * Format date and time for display
 * @param {Date} date - Date to format
 * @returns {string} - Formatted date string
 */
function formatDateTime(date) {
    if (!date) return 'N/A';
    
    const now = new Date();
    const tomorrow = new Date(now);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    // Format time
    const timeOptions = { hour: 'numeric', minute: 'numeric' };
    const timeString = date.toLocaleTimeString(undefined, timeOptions);
    
    // If today
    if (date.toDateString() === now.toDateString()) {
        return `Today at ${timeString}`;
    }
    
    // If tomorrow
    if (date.toDateString() === tomorrow.toDateString()) {
        return `Tomorrow at ${timeString}`;
    }
    
    // Otherwise show full date
    const dateOptions = { month: 'short', day: 'numeric' };
    const dateString = date.toLocaleDateString(undefined, dateOptions);
    return `${dateString} at ${timeString}`;
}

/**
 * Get time ago string from date
 * @param {Date} date - Date to calculate time ago from
 * @returns {string} - Time ago string
 */
function getTimeAgo(date) {
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) {
        return 'Just now';
    }
    
    const diffInMinutes = Math.floor(diffInSeconds / 60);
    if (diffInMinutes < 60) {
        return `${diffInMinutes} minute${diffInMinutes !== 1 ? 's' : ''} ago`;
    }
    
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) {
        return `${diffInHours} hour${diffInHours !== 1 ? 's' : ''} ago`;
    }
    
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) {
        return `${diffInDays} day${diffInDays !== 1 ? 's' : ''} ago`;
    }
    
    // Format full date for older entries
    return date.toLocaleDateString();
}

/**
 * Capitalize the first letter of a string
 * @param {string} str - String to capitalize
 * @returns {string} - Capitalized string
 */
function capitalizeFirstLetter(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}
