from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import json
import datetime
import logging
from models import db, Topic, Schedule, Status, Log
from perplexity_api import PerplexityAPIManager
from scheduler import SchedulerManager
from journal_generator import generate_journal_entry
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__, 
            static_folder='../frontend/static',
            template_folder='../frontend/templates')
CORS(app)  # Enable Cross-Origin Resource Sharing

# Load configuration
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Initialize API manager
api_manager = PerplexityAPIManager(app.config['PERPLEXITY_API_KEY'], app.config['DAILY_BUDGET'])

# Initialize scheduler manager
scheduler_manager = SchedulerManager(api_manager, generate_journal_entry)

@app.before_first_request
def initialize_database():
    """Create tables and initialize data if needed"""
    with app.app_context():
        db.create_all()
        
        # Check if Status table is empty and initialize it
        if Status.query.count() == 0:
            status = Status(
                last_run_time=None,
                next_run_time=None,
                api_calls_this_month=0
            )
            db.session.add(status)
            db.session.commit()
            logger.info("Initialized Status in database")
        
        # Check if Schedule table is empty and initialize it
        if Schedule.query.count() == 0:
            schedule = Schedule(
                frequency='daily',
                time_of_day='09:00',
                email_notifications=False
            )
            db.session.add(schedule)
            db.session.commit()
            logger.info("Initialized Schedule in database")
        
        # Start the scheduler
        scheduler_manager.start_scheduler(app)
        logger.info("Started scheduler")

# Routes for the frontend
@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/journal/<path:filename>')
def journal_entry(filename):
    """Serve generated journal entries"""
    return send_from_directory('../frontend/journal_html', filename)

# API endpoints
@app.route('/api/topics', methods=['GET'])
def get_topics():
    """Get all research topics"""
    topics = Topic.query.all()
    return jsonify([topic.to_dict() for topic in topics])

@app.route('/api/topics', methods=['POST'])
def add_topic():
    """Add a new research topic"""
    data = request.json
    topic = Topic(
        name=data['name'],
        query=data['query'],
        created_at=datetime.datetime.now()
    )
    db.session.add(topic)
    db.session.commit()
    logger.info(f"Added new topic: {data['name']}")
    return jsonify(topic.to_dict()), 201

@app.route('/api/topics/<int:topic_id>', methods=['PUT'])
def update_topic(topic_id):
    """Update an existing research topic"""
    topic = Topic.query.get_or_404(topic_id)
    data = request.json
    topic.name = data['name']
    topic.query = data['query']
    db.session.commit()
    logger.info(f"Updated topic: {data['name']}")
    return jsonify(topic.to_dict())

@app.route('/api/topics/<int:topic_id>', methods=['DELETE'])
def delete_topic(topic_id):
    """Delete a research topic"""
    topic = Topic.query.get_or_404(topic_id)
    topic_name = topic.name
    db.session.delete(topic)
    db.session.commit()
    logger.info(f"Deleted topic: {topic_name}")
    return jsonify({"message": "Topic deleted successfully"})

@app.route('/api/schedule', methods=['GET'])
def get_schedule():
    """Get current schedule settings"""
    schedule = Schedule.query.first()
    return jsonify(schedule.to_dict())

@app.route('/api/schedule', methods=['POST'])
def update_schedule():
    """Update schedule settings"""
    data = request.json
    schedule = Schedule.query.first()
    schedule.frequency = data['frequency']
    schedule.time_of_day = data['time_of_day']
    schedule.email_notifications = data.get('email_notifications', False)
    db.session.commit()
    
    # Update the scheduler
    scheduler_manager.update_schedule(app)
    
    logger.info(f"Updated schedule: {data}")
    return jsonify(schedule.to_dict())

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current application status"""
    status = Status.query.first()
    recent_logs = Log.query.order_by(Log.timestamp.desc()).limit(10).all()
    
    return jsonify({
        "status": status.to_dict(),
        "recent_activity": [log.to_dict() for log in recent_logs]
    })

@app.route('/api/journal', methods=['GET'])
def get_journal_entries():
    """Get list of generated journal entries"""
    journal_dir = os.path.join('..', 'frontend', 'journal_html')
    entries = []
    
    if os.path.exists(journal_dir):
        for filename in os.listdir(journal_dir):
            if filename.endswith('.html'):
                # Extract metadata from the file (if available)
                filepath = os.path.join(journal_dir, filename)
                # Get file modification time
                mod_time = os.path.getmtime(filepath)
                mod_date = datetime.datetime.fromtimestamp(mod_time)
                
                # Extract topic name from filename (remove .html extension)
                topic_name = os.path.splitext(filename)[0].replace('-', ' ').title()
                
                # Find the corresponding topic in database for additional info
                topic = Topic.query.filter_by(name=topic_name).first()
                
                entries.append({
                    "filename": filename,
                    "topic_name": topic_name,
                    "updated": mod_date.strftime('%Y-%m-%d %H:%M'),
                    "tags": topic.tags.split(',') if topic and topic.tags else []
                })
    
    return jsonify(entries)

@app.route('/api/run-now/<int:topic_id>', methods=['POST'])
def run_now(topic_id):
    """Manually run a search for a specific topic"""
    topic = Topic.query.get_or_404(topic_id)
    
    # Run the search in a background thread to avoid blocking
    scheduler_manager.run_single_topic(app, topic.id)
    
    return jsonify({"message": f"Started search for topic: {topic.name}"})

if __name__ == '__main__':
    app.run(debug=True)