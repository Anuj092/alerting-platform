#!/usr/bin/env python3
"""
Test script to verify notifications and reminders work
"""

from database import SessionLocal, create_tables, seed_data
from services import AlertService, NotificationObserver, ReminderService
from models import Alert, User, SeverityLevel, DeliveryType, VisibilityType
from datetime import datetime, timedelta

def test_notifications_and_reminders():
    print("Testing Notifications and Reminders...")
    
    # Setup database
    create_tables()
    seed_data()
    
    db = SessionLocal()
    
    # Create alert service with observer
    alert_service = AlertService(db)
    notification_observer = NotificationObserver(db, alert_service)
    alert_service.add_observer(notification_observer)
    
    print("\n1. Creating a test alert...")
    alert_data = {
        'title': 'Test Notification Alert',
        'message': 'This is a test alert to verify notifications work',
        'severity': SeverityLevel.WARNING,
        'delivery_type': DeliveryType.SLACK,
        'visibility_type': VisibilityType.ORGANIZATION,
        'reminder_frequency': 2
    }
    
    alert = alert_service.create_alert(alert_data, created_by=1)
    print(f"Alert created with ID: {alert.id}")
    
    print("\n2. Testing reminder processing...")
    reminder_service = ReminderService(db, alert_service)
    reminder_service.process_reminders()
    
    print("\n3. Checking notification deliveries...")
    from models import NotificationDelivery
    deliveries = db.query(NotificationDelivery).filter(
        NotificationDelivery.alert_id == alert.id
    ).all()
    
    print(f"Total deliveries logged: {len(deliveries)}")
    for delivery in deliveries:
        print(f"  - Delivered to user {delivery.user_id} via {delivery.delivery_type.value}")
    
    db.close()
    print("\nNotification and reminder test completed!")

if __name__ == "__main__":
    test_notifications_and_reminders()