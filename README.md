<<<<<<< HEAD
# Research Journal

An automated research journal system that generates and manages research topics, schedules research tasks, and creates formatted journal entries using the Perplexity API.

## Project Structure

```
research_journal/
│
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── config.py              # Configuration settings
│   ├── models.py              # Database models
│   ├── perplexity_api.py      # Perplexity API integration
│   ├── scheduler.py           # Task scheduling
│   ├── journal_generator.py   # HTML generation
│   └── utils.py               # Utility functions
│
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css      # Main stylesheet
│   │   ├── js/
│   │   │   ├── main.js        # Main JavaScript file
│   │   │   ├── topics.js      # Topic management
│   │   │   ├── schedule.js    # Schedule management
│   │   │   └── journal.js     # Journal browsing
│   │   └── img/               # Images and icons
│   ├── templates/
│   │   ├── index.html         # Main application page
│   │   └── journal_entry.html # Template for journal entries
│   └── journal_html/          # Generated journal entries
│
├── .env                       # Environment variables (API keys)
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

## Features

- Automated research topic generation and management
- Task scheduling and progress tracking
- Integration with Perplexity API for research assistance
- Web-based interface for managing research activities
- Automated journal entry generation
- Responsive and modern UI

## Prerequisites

- Python 3.8 or higher
- Flask
- Perplexity API key
- Modern web browser

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd research_journal
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your API keys:
```
PERPLEXITY_API_KEY=your_api_key_here
```

## Usage

1. Start the Flask server:
```bash
python backend/app.py
```

2. Open your web browser and navigate to `http://localhost:5000`

3. Use the web interface to:
   - Generate and manage research topics
   - Schedule research tasks
   - View and manage journal entries

## Configuration

The application can be configured through:
- `backend/config.py` - Application settings
- `.env` - Environment variables and API keys

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Specify your license here]

## Contact

[Your contact information] 
=======
# autoplex
Automated research agent with journal and stateful queries and cross-discipline graph
>>>>>>> c7688ddd35b919a54a88359e15737c44424f468c
