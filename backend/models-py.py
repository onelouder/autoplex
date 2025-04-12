from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Topic(db.Model):
    """Research topic model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    query = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_updated = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), default="pending")  # pending, active, completed, error
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "query": self.query,
            "tags": self.tags.split(",") if self.tags else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "status": self.status
        }

class Schedule(db.Model):
    """Schedule settings model"""
    id = db.Column(db.Integer, primary_key=True)
    frequency = db.Column(db.String(50), nullable=False, default="daily")  # daily, weekly, monthly
    time_of_day = db.Column(db.String(10), nullable=False, default="09:00")  # HH:MM format
    email_notifications = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "frequency": self.frequency,
            "time_of_day": self.time_of_day,
            "email_notifications": self.email_notifications
        }

class Status(db.Model):
    """Application status model"""
    id = db.Column(db.Integer, primary_key=True)
    last_run_time = db.Column(db.DateTime, nullable=True)
    next_run_time = db.Column(db.DateTime, nullable=True)
    api_calls_this_month = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default="active")  # active, paused, error
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "last_run_time": self.last_run_time.isoformat() if self.last_run_time else None,
            "next_run_time": self.next_run_time.isoformat() if self.next_run_time else None,
            "api_calls_this_month": self.api_calls_this_month,
            "status": self.status
        }

class Log(db.Model):
    """Application activity log model"""
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=True)
    status = db.Column(db.String(50), nullable=False)  # success, error, info, warning
    message = db.Column(db.Text, nullable=False)
    
    topic = db.relationship('Topic', backref=db.backref('logs', lazy=True))
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "topic_id": self.topic_id,
            "topic_name": self.topic.name if self.topic else None,
            "status": self.status,
            "message": self.message
        }
