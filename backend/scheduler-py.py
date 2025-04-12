from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import threading
import logging
from models import db, Topic, Schedule, Status, Log

logger = logging.getLogger(__name__)

class SchedulerManager:
    """Manager for scheduling and running research updates
    
    Handles scheduling logic based on user preferences and executes
    the Perplexity API searches at the appropriate times.
    """
    
    def __init__(self, api_manager, journal_generator):
        """Initialize the scheduler manager
        
        Args:
            api_manager: Instance of PerplexityAPIManager
            journal_generator: Function to generate journal entries
        """
        self.api_manager = api_manager
        self.journal_generator = journal_generator
        self.scheduler = BackgroundScheduler()
        self.lock = threading.Lock()  # For thread safety
    
    def start_scheduler(self, app):
        """Start the scheduler with the current schedule settings
        
        Args:
            app: Flask application instance (for application context)
        """
        with app.app_context():
            schedule = Schedule.query.first()
            if not schedule:
                logger.error("No schedule settings found in database")
                return
            
            # Configure and start the scheduler
            self._configure_scheduler(schedule, app)
            
            if not self.scheduler.running:
                self.scheduler.start()
                logger.info("Scheduler started successfully")
    
    def _configure_scheduler(self, schedule, app):
        """Configure the scheduler based on schedule settings
        
        Args:
            schedule: Schedule database model instance
            app: Flask application instance
        """
        # Remove existing jobs
        self.scheduler.remove_all_jobs()
        
        # Parse the time of day
        try:
            hour, minute = schedule.time_of_day.split(':')
            hour, minute = int(hour), int(minute)
        except (ValueError, AttributeError):
            logger.error(f"Invalid time format: {schedule.time_of_day}")
            hour, minute = 9, 0  # Default to 9:00 AM
        
        # Configure trigger based on frequency
        if schedule.frequency == 'daily':
            trigger = CronTrigger(hour=hour, minute=minute)
            next_run = self._calculate_next_run(hour, minute)
            logger.info(f"Scheduled daily update at {hour:02d}:{minute:02d}")
        
        elif schedule.frequency == 'weekly':
            # Run weekly on Monday
            trigger = CronTrigger(day_of_week='mon', hour=hour, minute=minute)
            next_run = self._calculate_next_run(hour, minute, day_of_week=0)  # 0 = Monday
            logger.info(f"Scheduled weekly update on Monday at {hour:02d}:{minute:02d}")
        
        elif schedule.frequency == 'monthly':
            # Run monthly on the 1st
            trigger = CronTrigger(day=1, hour=hour, minute=minute)
            next_run = self._calculate_next_run(hour, minute, day=1)
            logger.info(f"Scheduled monthly update on the 1st at {hour:02d}:{minute:02d}")
        
        else:
            # Default to daily if unrecognized frequency
            trigger = CronTrigger(hour=hour, minute=minute)
            next_run = self._calculate_next_run(hour, minute)
            logger.warning(f"Unrecognized frequency '{schedule.frequency}', defaulting to daily")
        
        # Add job to the scheduler
        self.scheduler.add_job(
            self.run_scheduled_update,
            trigger=trigger,
            args=[app],
            id='scheduled_update',
            replace_existing=True
        )
        
        # Update next run time in database
        with app.app_context():
            status = Status.query.first()
            if status:
                status.next_run_time = next_run
                db.session.commit()
                logger.info(f"Updated next run time to {next_run}")
    
    def _calculate_next_run(self, hour, minute, day=None, day_of_week=None):
        """Calculate the next run time based on schedule parameters
        
        Args:
            hour (int): Hour of day (0-23)
            minute (int): Minute of hour (0-59)
            day (int, optional): Day of month for monthly schedule
            day_of_week (int, optional): Day of week for weekly schedule (0=Monday)
            
        Returns:
            datetime: Next scheduled run time
        """
        now = datetime.now()
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        if next_run <= now:
            # If the time is in the past, move to tomorrow
            next_run += timedelta(days=1)
        
        if day is not None:
            # For monthly schedule
            if next_run.day != day:
                # Move to the specified day in the current or next month
                if next_run.day < day:
                    # Later this month
                    next_run = next_run.replace(day=day)
                else:
                    # Next month
                    if next_run.month == 12:
                        next_run = next_run.replace(year=next_run.year + 1, month=1, day=day)
                    else:
                        next_run = next_run.replace(month=next_run.month + 1, day=day)
        
        if day_of_week is not None:
            # For weekly schedule
            days_ahead = day_of_week - next_run.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            next_run += timedelta(days=days_ahead)
        
        return next_run
    
    def update_schedule(self, app):
        """Update the scheduler with new schedule settings
        
        Args:
            app: Flask application instance
        """
        with app.app_context():
            schedule = Schedule.query.first()
            if schedule:
                self._configure_scheduler(schedule, app)
                logger.info(f"Updated scheduler with new settings: {schedule.frequency} at {schedule.time_of_day}")
    
    def run_scheduled_update(self, app):
        """Run the scheduled update task for all topics
        
        Args:
            app: Flask application instance for database context
        """
        with app.app_context():
            logger.info("Starting scheduled update")
            
            # Update the last run time
            status = Status.query.first()
            if status:
                status.last_run_time = datetime.now()
                db.session.commit()
            
            # Get all topics
            topics = Topic.query.all()
            
            if not topics:
                logger.warning("No topics found for scheduled update")
                log = Log(
                    status="warning",
                    message="No topics found for scheduled update"
                )
                db.session.add(log)
                db.session.commit()
                return
            
            # Process each topic
            for topic in topics:
                try:
                    self._process_topic(topic, app)
                except Exception as e:
                    logger.error(f"Error processing topic {topic.name}: {str(e)}")
                    log = Log(
                        topic_id=topic.id,
                        status="error",
                        message=f"Error during scheduled update: {str(e)}"
                    )
                    db.session.add(log)
                    db.session.commit()
            
            # Calculate next run time
            schedule = Schedule.query.first()
            if schedule and status:
                next_run = self._calculate_next_run(
                    *map(int, schedule.time_of_day.split(':'))
                )
                status.next_run_time = next_run
                db.session.commit()
                logger.info(f"Next scheduled update: {next_run}")
    
    def run_single_topic(self, app, topic_id):
        """Run a search for a single topic (for manual runs)
        
        Args:
            app: Flask application instance
            topic_id: ID of the topic to process
        """
        threading.Thread(
            target=self._run_single_topic_thread,
            args=(app, topic_id)
        ).start()
    
    def _run_single_topic_thread(self, app, topic_id):
        """Thread function for running a single topic search
        
        Args:
            app: Flask application instance
            topic_id: ID of the topic to process
        """
        with app.app_context():
            topic = Topic.query.get(topic_id)
            if not topic:
                logger.error(f"Topic not found: {topic_id}")
                return
            
            logger.info(f"Running manual search for topic: {topic.name}")
            
            # Create log entry for manual search
            log = Log(
                topic_id=topic.id,
                status="info",
                message=f"Manual search started for topic: {topic.name}"
            )
            db.session.add(log)
            db.session.commit()
            
            # Process the topic
            try:
                self._process_topic(topic, app)
            except Exception as e:
                logger.error(f"Error in manual search for {topic.name}: {str(e)}")
                log = Log(
                    topic_id=topic.id,
                    status="error",
                    message=f"Error in manual search: {str(e)}"
                )
                db.session.add(log)
                db.session.commit()
    
    def _process_topic(self, topic, app):
        """Process a single topic by making API call and generating journal entry
        
        Args:
            topic: Topic database model instance
            app: Flask application instance
        """
        with self.lock:  # Ensure thread safety for API calls
            logger.info(f"Processing topic: {topic.name}")
            
            # Update topic status
            topic.status = "processing"
            db.session.commit()
            
            # Prepare system message for this topic
            system_message = (
                f"You are a research assistant specializing in {topic.name}. "
                f"Provide a comprehensive summary of the latest developments, research, "
                f"and important information on this topic. Include citations to reliable "
                f"sources. Be factual, objective, and thorough."
            )
            
            # Make the API call
            response = self.api_manager.query(
                topic.query,
                system_message=system_message,
                max_tokens=1500  # Adjust based on needs
            )
            
            # Update API call count
            status = Status.query.first()
            if status:
                status.api_calls_this_month += 1
                db.session.commit()
            
            # Check for errors
            if "error" in response:
                topic.status = "error"
                db.session.commit()
                
                log = Log(
                    topic_id=topic.id,
                    status="error",
                    message=f"API error: {response['error']}"
                )
                db.session.add(log)
                db.session.commit()
                
                logger.error(f"API error for topic {topic.name}: {response['error']}")
                return
            
            # Generate journal entry
            try:
                filename = self.journal_generator(topic, response)
                
                # Update topic status
                topic.status = "completed"
                topic.last_updated = datetime.now()
                db.session.commit()
                
                # Log success
                log = Log(
                    topic_id=topic.id,
                    status="success",
                    message=f"Successfully updated research for {topic.name}"
                )
                db.session.add(log)
                db.session.commit()
                
                logger.info(f"Successfully processed topic: {topic.name}")
                return filename
            
            except Exception as e:
                topic.status = "error"
                db.session.commit()
                
                logger.error(f"Error generating journal for {topic.name}: {str(e)}")
                raise
