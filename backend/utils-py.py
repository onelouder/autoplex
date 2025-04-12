import os
import re
import json
from datetime import datetime
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

logger = logging.getLogger(__name__)

def sanitize_filename(filename):
    """Sanitize a string to be used as a filename
    
    Args:
        filename (str): Input string
        
    Returns:
        str: Sanitized filename
    """
    # Replace invalid characters with underscores
    sanitized = re.sub(r'[^\w\-\.]', '_', filename)
    return sanitized

def parse_time_string(time_str):
    """Parse a time string in HH:MM format
    
    Args:
        time_str (str): Time string in HH:MM format
        
    Returns:
        tuple: (hour, minute) as integers
    """
    try:
        hour, minute = time_str.split(':')
        return int(hour), int(minute)
    except (ValueError, AttributeError):
        logger.error(f"Invalid time format: {time_str}")
        return 9, 0  # Default to 9:00 AM

def format_datetime(dt):
    """Format a datetime object for display
    
    Args:
        dt (datetime): Datetime object
        
    Returns:
        str: Formatted datetime string
    """
    if not dt:
        return "Not scheduled"
    
    now = datetime.now()
    
    # If date is today
    if dt.date() == now.date():
        return f"Today at {dt.strftime('%I:%M %p')}"
    
    # If date is tomorrow
    tomorrow = now.date().replace(day=now.day + 1)
    if dt.date() == tomorrow:
        return f"Tomorrow at {dt.strftime('%I:%M %p')}"
    
    # If date is within this week
    if (dt.date() - now.date()).days < 7:
        return dt.strftime('%A at %I:%M %p')
    
    # Otherwise return full date
    return dt.strftime('%Y-%m-%d at %I:%M %p')

def send_email_notification(recipient, subject, message, html_message=None):
    """Send an email notification
    
    Args:
        recipient (str): Email recipient address
        subject (str): Email subject
        message (str): Plain text message
        html_message (str, optional): HTML message. Defaults to None.
        
    Returns:
        bool: True if sent successfully, False otherwise
    """
    if not Config.MAIL_SERVER or not Config.MAIL_USERNAME or not Config.MAIL_PASSWORD:
        logger.warning("Email configuration incomplete, skipping notification")
        return False
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = Config.MAIL_DEFAULT_SENDER or Config.MAIL_USERNAME
    msg['To'] = recipient
    
    # Attach plain text part
    msg.attach(MIMEText(message, 'plain'))
    
    # Attach HTML part if provided
    if html_message:
        msg.attach(MIMEText(html_message, 'html'))
    
    try:
        server = smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT)
        if Config.MAIL_USE_TLS:
            server.starttls()
        server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        logger.info(f"Email notification sent to {recipient}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False

def get_journal_stats():
    """Get statistics about the journal entries
    
    Returns:
        dict: Journal statistics
    """
    journal_dir = Config.JOURNAL_DIR
    stats = {
        'total_entries': 0,
        'topics': {},
        'last_updated': None,
        'tags': {}
    }
    
    if not os.path.exists(journal_dir):
        return stats
    
    for filename in os.listdir(journal_dir):
        if filename.endswith('.html'):
            stats['total_entries'] += 1
            
            # Extract topic name from filename
            topic_name = os.path.splitext(filename)[0].replace('-', ' ').title()
            stats['topics'][topic_name] = stats['topics'].get(topic_name, 0) + 1
            
            # Get file modification time
            mod_time = os.path.getmtime(os.path.join(journal_dir, filename))
            mod_date = datetime.fromtimestamp(mod_time)
            
            # Update last updated time
            if not stats['last_updated'] or mod_date > stats['last_updated']:
                stats['last_updated'] = mod_date
            
            # Try to extract tags from file
            try:
                with open(os.path.join(journal_dir, filename), 'r', encoding='utf-8') as f:
                    content = f.read()
                    tag_matches = re.findall(r'<span class="tag">(.*?)</span>', content)
                    for tag in tag_matches:
                        stats['tags'][tag] = stats['tags'].get(tag, 0) + 1
            except Exception as e:
                logger.error(f"Error parsing file {filename}: {str(e)}")
    
    # Format last updated time
    if stats['last_updated']:
        stats['last_updated'] = stats['last_updated'].strftime('%Y-%m-%d %H:%M:%S')
    
    return stats
