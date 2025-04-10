# Autoplex Research Agent - Technical Specification

## I. Core Concepts & Goals

### Stateful System
- Maintains persistent storage of:
  - User-defined topics and associated queries
  - Schedule configurations
  - API credentials (securely stored)
  - Search history and status
- Data persistence between application runs

### Automation
- Scheduled task execution
- Automated Perplexity API queries
- Background processing of results
- Static HTML generation

### Research Curation
- Topic management system
- Query definition per topic
- Result organization and storage
- Static HTML journal generation

### User Interface
- Web-based GUI for:
  - Topic management
  - Schedule configuration
  - Status monitoring
  - Journal browsing

## II. Architecture & Technologies

### Backend / Core Logic (Python)

#### Responsibilities
- State management
- Perplexity API integration
- Result processing
- Static HTML generation
- Task scheduling
- Frontend API provision

#### Core Dependencies
```python
# Primary dependencies
requests          # HTTP client for API calls
schedule          # Task scheduling
sqlite3          # Local database
Jinja2           # HTML templating
Flask            # Web framework
python-dotenv    # Environment management
```

### Frontend / GUI

#### Responsibilities
- User interface rendering
- Topic management interface
- Schedule configuration
- Status display
- Journal browsing
- Backend communication

#### Technologies
- HTML5
- CSS3 (with Bootstrap/Tailwind)
- JavaScript (Vanilla or Vue.js/React/Svelte)

### Data Storage Architecture

#### SQLite Database Schema
```sql
-- topics table
CREATE TABLE topics (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    perplexity_query TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP
);

-- schedule table
CREATE TABLE schedule (
    id INTEGER PRIMARY KEY,
    frequency TEXT NOT NULL,
    time_of_day TEXT NOT NULL,
    email_notifications_enabled BOOLEAN DEFAULT FALSE
);

-- status table
CREATE TABLE status (
    id INTEGER PRIMARY KEY,
    last_run_time TIMESTAMP,
    next_run_time TIMESTAMP,
    api_calls_this_month INTEGER DEFAULT 0
);

-- logs table
CREATE TABLE logs (
    id INTEGER PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    topic_id INTEGER,
    status TEXT,
    message TEXT,
    FOREIGN KEY (topic_id) REFERENCES topics(id)
);
```

#### File Structure
- `.env`: API credentials (excluded from version control)
- `journal_html/`: Generated static content
- `static/`: Frontend assets
- `templates/`: HTML templates

## III. Development Implementation

### 1. Project Setup
```bash
# Directory structure
research_journal/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── models.py
│   ├── perplexity_api.py
│   ├── scheduler.py
│   ├── journal_generator.py
│   └── utils.py
├── frontend/
│   ├── static/
│   ├── templates/
│   └── journal_html/
├── .env
├── requirements.txt
└── README.md
```

### 2. Core Components

#### State Management
```python
# Database initialization
def init_db():
    # Create tables if they don't exist
    # Set up initial configuration

# Topic management
def add_topic(name, query):
    # Add new topic to database
    # Return topic ID

def get_topics():
    # Retrieve all topics
    # Return formatted list
```

#### Perplexity API Integration
```python
def call_perplexity(query):
    # Make API request
    # Handle errors
    # Process response
    # Return formatted result
```

#### HTML Generation
```python
def generate_html_summary(topic, perplexity_data):
    # Process API response
    # Apply template
    # Save to journal_html/
```

#### Scheduling System
```python
def run_scheduled_update():
    # Get active topics
    # Process each topic
    # Update status
    # Log results
```

### 3. API Endpoints

```python
# Flask routes
@app.route('/api/topics', methods=['GET', 'POST'])
def topics():
    # Handle topic management

@app.route('/api/schedule', methods=['GET', 'POST'])
def schedule():
    # Handle schedule management

@app.route('/api/status', methods=['GET'])
def status():
    # Return system status

@app.route('/api/journal', methods=['GET'])
def journal():
    # List generated entries
```

## IV. Key Considerations

### Error Handling
- API error management
- Network failure handling
- File system error recovery
- Input validation

### Security
- API key protection
- Environment variable usage
- Input sanitization
- Access control

### Performance
- Concurrent processing
- API rate limiting
- Database optimization
- Caching strategy

### User Experience
- Loading indicators
- Error messaging
- Success confirmations
- Responsive design

## V. Future Enhancements

1. Email notifications
2. Advanced search functionality
3. Topic categorization
4. Export capabilities
5. API usage analytics
6. User authentication
7. Multi-user support 