// Global variables
let journalEntries = [];

// Initialize journal directory when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Fetch journal entries
    fetchJournalEntries();
    
    // Set up event listeners
    setupJournalEventListeners();
});

/**
 * Set up event listeners for journal management
 */
function setupJournalEventListeners() {
    const searchInput = document.getElementById('journal-search');
    
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            filterJournalEntries(searchInput.value.trim().toLowerCase());
        });
    }
}

/**
 * Fetch journal entries from API
 */
function fetchJournalEntries() {
    fetch(`${API_BASE_URL}/journal`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            journalEntries = data;
            renderJournalEntries(journalEntries);
        })
        .catch(error => {
            console.error('Error fetching journal entries:', error);
            showError('Failed to fetch journal entries. Please try again later.');
        });
}

/**
 * Render journal entries in the UI
 * @param {Array} entries - Journal entries to render
 */
function renderJournalEntries(entries) {
    const journalEntriesContainer = document.getElementById('journal-entries');
    
    // Clear existing entries
    journalEntriesContainer.innerHTML = '';
    
    // Add new entries
    if (entries && entries.length > 0) {
        entries.forEach(entry => {
            const entryElement = document.createElement('div');
            entryElement.className = 'journal-entry';
            
            // Determine entry status class
            let statusClass = 'status-updated';
            let statusText = 'Updated';
            
            if (entry.filename.includes('new')) {
                statusClass = 'status-new';
                statusText = 'New';
            } else if (entry.filename.includes('scheduled')) {
                statusClass = 'status-scheduled';
                statusText = 'Scheduled';
            }
            
            // Create entry HTML
            entryElement.innerHTML = `
                <div class="journal-entry-header">
                    <h3 class="journal-entry-title">${entry.topic_name}</h3>
                    <span class="journal-entry-date">${entry.updated}</span>
                </div>
                <div class="journal-entry-tags">
                    ${entry.tags.map(tag => `<span class="journal-entry-tag">${tag}</span>`).join('')}
                </div>
                <div class="journal-entry-footer">
                    <span class="journal-status ${statusClass}">${statusText}</span>
                    <a href="/journal/${entry.filename}" class="view-link" target="_blank">
                        View <i class="fas fa-external-link-alt"></i>
                    </a>
                </div>
            `;
            
            journalEntriesContainer.appendChild(entryElement);
        });
    } else {
        // Show message if no entries
        journalEntriesContainer.innerHTML = `
            <div class="empty-state">
                <p>No journal entries yet. Add research topics and run searches to generate entries.</p>
            </div>
        `;
    }
}

/**
 * Filter journal entries by search term
 * @param {string} searchTerm - Search term to filter by
 */
function filterJournalEntries(searchTerm) {
    if (!searchTerm) {
        // If search is empty, show all entries
        renderJournalEntries(journalEntries);
        return;
    }
    
    // Filter entries that match the search term
    const filteredEntries = journalEntries.filter(entry => {
        // Search in topic name
        if (entry.topic_name.toLowerCase().includes(searchTerm)) {
            return true;
        }
        
        // Search in tags
        if (entry.tags.some(tag => tag.toLowerCase().includes(searchTerm))) {
            return true;
        }
        
        return false;
    });
    
    renderJournalEntries(filteredEntries);
}

/**
 * Refresh journal entries (called after new entries are generated)
 */
function refreshJournalEntries() {
    fetchJournalEntries();
}
