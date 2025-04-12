// Global variables
let topics = [];
let editingTopicId = null;

// Initialize topic management when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Fetch topics from API
    fetchTopics();
    
    // Set up event listeners
    setupTopicEventListeners();
});

/**
 * Set up event listeners for topic management
 */
function setupTopicEventListeners() {
    // Add topic button
    const addTopicBtn = document.getElementById('add-topic-btn');
    const newTopicInput = document.getElementById('new-topic-input');
    
    if (addTopicBtn) {
        addTopicBtn.addEventListener('click', () => {
            const topicName = newTopicInput.value.trim();
            if (topicName) {
                showTopicModal(topicName);
                newTopicInput.value = '';
            } else {
                showTopicModal();
            }
        });
    }
    
    // Enter key on input field
    if (newTopicInput) {
        newTopicInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const topicName = newTopicInput.value.trim();
                if (topicName) {
                    showTopicModal(topicName);
                    newTopicInput.value = '';
                }
            }
        });
    }
    
    // Topic form submission
    const topicForm = document.getElementById('topic-form');
    if (topicForm) {
        topicForm.addEventListener('submit', (e) => {
            e.preventDefault();
            saveTopicFromForm();
        });
    }
    
    // Cancel button
    const cancelTopicBtn = document.getElementById('cancel-topic-btn');
    if (cancelTopicBtn) {
        cancelTopicBtn.addEventListener('click', () => {
            const topicModal = document.getElementById('topic-modal');
            topicModal.classList.remove('active');
        });
    }
}

/**
 * Fetch topics from the API
 */
function fetchTopics() {
    fetch(`${API_BASE_URL}/topics`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            topics = data;
            renderTopicsList();
        })
        .catch(error => {
            console.error('Error fetching topics:', error);
            showError('Failed to fetch research topics. Please try again later.');
        });
}

/**
 * Render the topics list in the UI
 */
function renderTopicsList() {
    const topicsList = document.getElementById('topics-list');
    
    // Clear existing items
    topicsList.innerHTML = '';
    
    // Add new items
    if (topics && topics.length > 0) {
        topics.forEach(topic => {
            const topicItem = document.createElement('div');
            topicItem.className = 'topic-item';
            
            // Create topic HTML
            topicItem.innerHTML = `
                <span class="topic-name">${topic.name}</span>
                <div class="topic-actions">
                    <button class="run-btn" title="Run now" data-id="${topic.id}">
                        <i class="fas fa-play"></i>
                    </button>
                    <button class="edit-btn" title="Edit" data-id="${topic.id}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="delete-btn" title="Delete" data-id="${topic.id}">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </div>
            `;
            
            topicsList.appendChild(topicItem);
        });
        
        // Add event listeners for action buttons
        addTopicActionEventListeners();
    } else {
        // Show message if no topics
        topicsList.innerHTML = `
            <div class="empty-state">
                <p>No research topics yet. Add your first topic to get started.</p>
            </div>
        `;
    }
}

/**
 * Add event listeners for topic action buttons
 */
function addTopicActionEventListeners() {
    // Run buttons
    const runButtons = document.querySelectorAll('.run-btn');
    runButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const topicId = e.currentTarget.getAttribute('data-id');
            runTopicNow(topicId);
        });
    });
    
    // Edit buttons
    const editButtons = document.querySelectorAll('.edit-btn');
    editButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const topicId = e.currentTarget.getAttribute('data-id');
            editTopic(topicId);
        });
    });
    
    // Delete buttons
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const topicId = e.currentTarget.getAttribute('data-id');
            const topic = topics.find(t => t.id == topicId);
            
            if (topic) {
                showConfirmation(`Are you sure you want to delete the topic "${topic.name}"?`, () => {
                    deleteTopic(topicId);
                });
            }
        });
    });
}

/**
 * Run a topic search immediately
 * @param {string} topicId - ID of the topic to run
 */
function runTopicNow(topicId) {
    fetch(`${API_BASE_URL}/run-now/${topicId}`, {
        method: 'POST'
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            showSuccess(data.message);
            
            // Refresh status after a short delay
            setTimeout(fetchAndUpdateStatus, 2000);
        })
        .catch(error => {
            console.error('Error running topic search:', error);
            showError('Failed to run topic search. Please try again later.');
        });
}

/**
 * Show the topic modal for adding or editing a topic
 * @param {string} topicName - Optional name for new topic
 */
function showTopicModal(topicName = '') {
    const modal = document.getElementById('topic-modal');
    const modalTitle = document.getElementById('topic-modal-title');
    const topicNameInput = document.getElementById('topic-name');
    const topicQueryInput = document.getElementById('topic-query');
    const topicIdInput = document.getElementById('topic-id');
    
    // Reset form
    topicNameInput.value = topicName;
    topicQueryInput.value = '';
    topicIdInput.value = '';
    
    // Set modal title for new topic
    modalTitle.textContent = 'Add Research Topic';
    editingTopicId = null;
    
    // Show modal
    modal.classList.add('active');
    
    // Focus on first empty field
    if (!topicName) {
        topicNameInput.focus();
    } else {
        topicQueryInput.focus();
    }
}

/**
 * Edit an existing topic
 * @param {string} topicId - ID of the topic to edit
 */
function editTopic(topicId) {
    const topic = topics.find(t => t.id == topicId);
    
    if (!topic) {
        showError('Topic not found.');
        return;
    }
    
    const modal = document.getElementById('topic-modal');
    const modalTitle = document.getElementById('topic-modal-title');
    const topicNameInput = document.getElementById('topic-name');
    const topicQueryInput = document.getElementById('topic-query');
    const topicIdInput = document.getElementById('topic-id');
    
    // Fill form with topic data
    topicNameInput.value = topic.name;
    topicQueryInput.value = topic.query;
    topicIdInput.value = topic.id;
    
    // Set modal title for editing
    modalTitle.textContent = 'Edit Research Topic';
    editingTopicId = topic.id;
    
    // Show modal
    modal.classList.add('active');
}

/**
 * Save topic from form data
 */
function saveTopicFromForm() {
    const topicNameInput = document.getElementById('topic-name');
    const topicQueryInput = document.getElementById('topic-query');
    const topicIdInput = document.getElementById('topic-id');
    
    const topicData = {
        name: topicNameInput.value.trim(),
        query: topicQueryInput.value.trim()
    };
    
    if (!topicData.name || !topicData.query) {
        showError('Please fill out all required fields.');
        return;
    }
    
    const topicId = topicIdInput.value;
    
    if (topicId) {
        // Update existing topic
        updateTopic(topicId, topicData);
    } else {
        // Create new topic
        createTopic(topicData);
    }
}

/**
 * Create a new topic
 * @param {Object} topicData - Topic data
 */
function createTopic(topicData) {
    fetch(`${API_BASE_URL}/topics`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(topicData)
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Hide modal
            const modal = document.getElementById('topic-modal');
            modal.classList.remove('active');
            
            // Refresh topics list
            fetchTopics();
            
            showSuccess(`Topic "${topicData.name}" created successfully.`);
        })
        .catch(error => {
            console.error('Error creating topic:', error);
            showError('Failed to create topic. Please try again later.');
        });
}

/**
 * Update an existing topic
 * @param {string} topicId - ID of the topic to update
 * @param {Object} topicData - Updated topic data
 */
function updateTopic(topicId, topicData) {
    fetch(`${API_BASE_URL}/topics/${topicId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(topicData)
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Hide modal
            const modal = document.getElementById('topic-modal');
            modal.classList.remove('active');
            
            // Refresh topics list
            fetchTopics();
            
            showSuccess(`Topic "${topicData.name}" updated successfully.`);
        })
        .catch(error => {
            console.error('Error updating topic:', error);
            showError('Failed to update topic. Please try again later.');
        });
}

/**
 * Delete a topic
 * @param {string} topicId - ID of the topic to delete
 */
function deleteTopic(topicId) {
    fetch(`${API_BASE_URL}/topics/${topicId}`, {
        method: 'DELETE'
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Refresh topics list
            fetchTopics();
            
            showSuccess(data.message);
        })
        .catch(error => {
            console.error('Error deleting topic:', error);
            showError('Failed to delete topic. Please try again later.');
        });
}
