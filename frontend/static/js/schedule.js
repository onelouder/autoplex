// Initialize schedule management when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Fetch current schedule settings
    fetchSchedule();
    
    // Set up event listeners
    setupScheduleEventListeners();
});

/**
 * Set up event listeners for schedule management
 */
function setupScheduleEventListeners() {
    const scheduleForm = document.getElementById('schedule-form');
    
    if (scheduleForm) {
        scheduleForm.addEventListener('submit', (e) => {
            e.preventDefault();
            saveSchedule();
        });
    }
}

/**
 * Fetch current schedule settings from API
 */
function fetchSchedule() {
    fetch(`${API_BASE_URL}/schedule`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            updateScheduleForm(data);
        })
        .catch(error => {
            console.error('Error fetching schedule:', error);
            showError('Failed to fetch schedule settings. Please try again later.');
        });
}

/**
 * Update schedule form with current settings
 * @param {Object} scheduleData - Schedule data from API
 */
function updateScheduleForm(scheduleData) {
    const frequencySelect = document.getElementById('frequency');
    const timeInput = document.getElementById('time');
    const emailCheckbox = document.getElementById('email-notifications');
    
    if (frequencySelect && scheduleData.frequency) {
        frequencySelect.value = scheduleData.frequency;
    }
    
    if (timeInput && scheduleData.time_of_day) {
        timeInput.value = scheduleData.time_of_day;
    }
    
    if (emailCheckbox) {
        emailCheckbox.checked = scheduleData.email_notifications || false;
    }
}

/**
 * Save schedule settings to API
 */
function saveSchedule() {
    const frequencySelect = document.getElementById('frequency');
    const timeInput = document.getElementById('time');
    const emailCheckbox = document.getElementById('email-notifications');
    
    const scheduleData = {
        frequency: frequencySelect.value,
        time_of_day: timeInput.value,
        email_notifications: emailCheckbox.checked
    };
    
    fetch(`${API_BASE_URL}/schedule`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(scheduleData)
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            showSuccess('Schedule updated successfully.');
            
            // Refresh status to show updated next run time
            fetchAndUpdateStatus();
        })
        .catch(error => {
            console.error('Error saving schedule:', error);
            showError('Failed to save schedule settings. Please try again later.');
        });
}

/**
 * Format frequency for display
 * @param {string} frequency - Frequency value
 * @returns {string} - Formatted frequency string
 */
function formatFrequency(frequency) {
    switch (frequency) {
        case 'daily':
            return 'Daily';
        case 'weekly':
            return 'Weekly (Monday)';
        case 'monthly':
            return 'Monthly (1st day)';
        default:
            return capitalizeFirstLetter(frequency);
    }
}
