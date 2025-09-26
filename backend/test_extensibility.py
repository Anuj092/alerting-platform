#!/usr/bin/env python3
"""
Test script to verify notification channel extensibility
"""

from services import AlertService, SlackNotificationChannel, NotificationChannel
from models import Alert, User, SeverityLevel, DeliveryType, VisibilityType
from database import SessionLocal
from datetime import datetime

# Test custom notification channel
class TeamsNotificationChannel(NotificationChannel):
    def send(self, user: User, alert: Alert) -> bool:
        print(f"Microsoft Teams notification sent to {user.name}: {alert.title}")
        return True

def test_extensibility():
    print("Testing Notification Channel Extensibility...")
    
    # Create AlertService instance
    db = SessionLocal()
    alert_service = AlertService(db)
    
    # Verify existing channels
    print(f"Default channels: {list(alert_service.notification_channels.keys())}")
    
    # Add new channel dynamically
    alert_service.notification_channels['Teams'] = TeamsNotificationChannel()
    
    print(f"After adding Teams: {list(alert_service.notification_channels.keys())}")
    
    # Create test user and alert
    test_user = User(id=999, name="Test User", email="test@example.com")
    test_alert = Alert(
        id=999,
        title="Test Alert",
        message="Testing extensibility",
        severity=SeverityLevel.INFO,
        delivery_type=DeliveryType.SLACK,
        visibility_type=VisibilityType.USER
    )
    
    # Test all channels
    for channel_name, channel in alert_service.notification_channels.items():
        print(f"\nTesting {channel_name} channel:")
        success = channel.send(test_user, test_alert)
        print(f"  Result: {'Success' if success else 'Failed'}")
    
    db.close()
    print("\nExtensibility test completed!")

if __name__ == "__main__":
    test_extensibility()