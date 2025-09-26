import threading
import time
from datetime import datetime
from database import SessionLocal
from services import AlertService, ReminderService, NotificationObserver

class ReminderScheduler:
    def __init__(self, interval_minutes=120):  # Default 2 hours
        self.interval_minutes = interval_minutes
        self.running = False
        self.thread = None
    
    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.thread.start()
            print(f"Reminder scheduler started - running every {self.interval_minutes} minutes")
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
    
    def _run_scheduler(self):
        while self.running:
            try:
                self._process_reminders()
                time.sleep(self.interval_minutes * 60)  # Convert to seconds
            except Exception as e:
                print(f"Error in reminder scheduler: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def _process_reminders(self):
        print(f"[{datetime.now()}] Processing reminders...")
        db = SessionLocal()
        try:
            alert_service = AlertService(db)
            reminder_service = ReminderService(db, alert_service)
            reminder_service.process_reminders()
            print("Reminders processed successfully")
        except Exception as e:
            print(f"Error processing reminders: {e}")
        finally:
            db.close()

# Global scheduler instance
reminder_scheduler = ReminderScheduler()