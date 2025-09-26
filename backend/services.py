from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import Alert, User, Team, NotificationDelivery, UserAlertPreference, VisibilityType, SeverityLevel

# Strategy Pattern for Notification Channels
class NotificationChannel(ABC):
    @abstractmethod
    def send(self, user: User, alert: Alert) -> bool:
        pass

class InAppNotificationChannel(NotificationChannel):
    def send(self, user: User, alert: Alert) -> bool:
        # In-app notifications are handled by the frontend
        return True

class EmailNotificationChannel(NotificationChannel):
    def send(self, user: User, alert: Alert) -> bool:
        # Future implementation
        print(f"Email sent to {user.email}: {alert.title}")
        return True

class SMSNotificationChannel(NotificationChannel):
    def send(self, user: User, alert: Alert) -> bool:
        # Future implementation
        print(f"SMS sent to user {user.id}: {alert.title}")
        return True

class SlackNotificationChannel(NotificationChannel):
    def send(self, user: User, alert: Alert) -> bool:
        # Slack integration implementation
        print(f"Slack message sent to {user.name}: [{alert.severity.value}] {alert.title}")
        # In real implementation, would use Slack API
        return True

# Observer Pattern for Alert Management
class AlertObserver(ABC):
    @abstractmethod
    def on_alert_created(self, alert: Alert):
        pass

class NotificationObserver(AlertObserver):
    def __init__(self, db: Session, alert_service=None):
        self.db = db
        self.alert_service = alert_service
        
    def on_alert_created(self, alert: Alert):
        users = self._get_target_users(alert)
        for user in users:
            self._create_user_preference(user, alert)
            self._deliver_notification(user, alert)
    
    def _get_target_users(self, alert: Alert) -> List[User]:
        if alert.visibility_type == VisibilityType.ORGANIZATION:
            return self.db.query(User).all()
        elif alert.visibility_type == VisibilityType.TEAM:
            return self.db.query(User).filter(User.team_id == alert.target_id).all()
        elif alert.visibility_type == VisibilityType.USER:
            user = self.db.query(User).filter(User.id == alert.target_id).first()
            return [user] if user else []
        return []
    
    def _create_user_preference(self, user: User, alert: Alert):
        preference = UserAlertPreference(
            user_id=user.id,
            alert_id=alert.id,
            last_reminded=datetime.utcnow()
        )
        self.db.add(preference)
    
    def _deliver_notification(self, user: User, alert: Alert):
        # Send actual notification through channel
        if self.alert_service:
            channel = self.alert_service.notification_channels.get(alert.delivery_type.value)
            if channel:
                success = channel.send(user, alert)
                if success:
                    # Log successful delivery
                    delivery = NotificationDelivery(
                        alert_id=alert.id,
                        user_id=user.id,
                        delivery_type=alert.delivery_type
                    )
                    self.db.add(delivery)
        else:
            # Fallback - just log delivery without sending
            delivery = NotificationDelivery(
                alert_id=alert.id,
                user_id=user.id,
                delivery_type=alert.delivery_type
            )
            self.db.add(delivery)

class AlertService:
    def __init__(self, db: Session):
        self.db = db
        self.observers: List[AlertObserver] = []
        self.notification_channels = {
            'In-App': InAppNotificationChannel(),
            'Email': EmailNotificationChannel(),
            'SMS': SMSNotificationChannel()
        }
        
        # Demonstrate extensibility - add new channel
        self.notification_channels['Slack'] = SlackNotificationChannel()
    
    def add_observer(self, observer: AlertObserver):
        self.observers.append(observer)
    
    def create_alert(self, alert_data: dict, created_by: int) -> Alert:
        alert = Alert(**alert_data, created_by=created_by)
        self.db.add(alert)
        self.db.flush()
        
        for observer in self.observers:
            observer.on_alert_created(alert)
        
        self.db.commit()
        return alert
    
    def get_alerts_for_user(self, user_id: int) -> List[dict]:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        # Get alerts based on visibility
        org_alerts = self.db.query(Alert).filter(
            Alert.visibility_type == VisibilityType.ORGANIZATION,
            Alert.is_active == True
        ).all()
        
        team_alerts = self.db.query(Alert).filter(
            Alert.visibility_type == VisibilityType.TEAM,
            Alert.target_id == user.team_id,
            Alert.is_active == True
        ).all() if user.team_id else []
        
        user_alerts = self.db.query(Alert).filter(
            Alert.visibility_type == VisibilityType.USER,
            Alert.target_id == user_id,
            Alert.is_active == True
        ).all()
        
        all_alerts = org_alerts + team_alerts + user_alerts
        
        # Get user preferences
        result = []
        for alert in all_alerts:
            preference = self.db.query(UserAlertPreference).filter(
                UserAlertPreference.user_id == user_id,
                UserAlertPreference.alert_id == alert.id
            ).first()
            
            result.append({
                'alert': alert,
                'is_read': preference.is_read if preference else False,
                'is_snoozed': preference.is_snoozed if preference else False,
                'snoozed_until': preference.snoozed_until if preference else None
            })
        
        return result
    
    def snooze_alert(self, user_id: int, alert_id: int):
        preference = self.db.query(UserAlertPreference).filter(
            UserAlertPreference.user_id == user_id,
            UserAlertPreference.alert_id == alert_id
        ).first()
        
        if preference:
            preference.is_snoozed = True
            preference.snoozed_until = datetime.utcnow() + timedelta(days=1)
            self.db.commit()
    
    def mark_as_read(self, user_id: int, alert_id: int):
        preference = self.db.query(UserAlertPreference).filter(
            UserAlertPreference.user_id == user_id,
            UserAlertPreference.alert_id == alert_id
        ).first()
        
        if preference:
            preference.is_read = True
            self.db.commit()

class ReminderService:
    def __init__(self, db: Session, alert_service: AlertService):
        self.db = db
        self.alert_service = alert_service
    
    def process_reminders(self):
        """Process all pending reminders"""
        now = datetime.utcnow()
        
        # Reset expired snoozes (next day)
        expired_snoozes = self.db.query(UserAlertPreference).filter(
            UserAlertPreference.is_snoozed == True,
            UserAlertPreference.snoozed_until < now
        ).all()
        
        for pref in expired_snoozes:
            pref.is_snoozed = False
            pref.snoozed_until = None
        
        # Find preferences that need reminders
        preferences = self.db.query(UserAlertPreference).join(Alert).filter(
            Alert.is_active == True,
            Alert.reminder_frequency > 0,  # Only alerts with reminders enabled
            UserAlertPreference.is_snoozed == False,
            UserAlertPreference.is_read == False
        ).all()
        
        for preference in preferences:
            alert = preference.alert
            
            # Check if alert has started
            if alert.start_time and alert.start_time > now:
                continue
                
            # Check if alert is still valid
            if alert.expiry_time and alert.expiry_time < now:
                continue
            
            # Check if reminder is due
            if preference.last_reminded:
                time_since_last = now - preference.last_reminded
                if time_since_last < timedelta(hours=alert.reminder_frequency):
                    continue
                
            # Send reminder
            user = preference.user
            channel = self.alert_service.notification_channels.get(alert.delivery_type.value)
            if channel and channel.send(user, alert):
                # Log delivery
                delivery = NotificationDelivery(
                    alert_id=alert.id,
                    user_id=user.id,
                    delivery_type=alert.delivery_type
                )
                self.db.add(delivery)
                
                # Update last reminded
                preference.last_reminded = now
        
        self.db.commit()

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_dashboard_metrics(self) -> dict:
        total_alerts = self.db.query(Alert).count()
        active_alerts = self.db.query(Alert).filter(Alert.is_active == True).count()
        
        total_deliveries = self.db.query(NotificationDelivery).count()
        total_preferences = self.db.query(UserAlertPreference).count()
        read_count = self.db.query(UserAlertPreference).filter(
            UserAlertPreference.is_read == True
        ).count()
        
        snoozed_count = self.db.query(UserAlertPreference).filter(
            UserAlertPreference.is_snoozed == True
        ).count()
        
        # Severity breakdown
        severity_counts = {}
        for severity in SeverityLevel:
            count = self.db.query(Alert).filter(
                Alert.severity == severity,
                Alert.is_active == True
            ).count()
            severity_counts[severity.value] = count
        
        # Snoozed counts per alert
        snoozed_per_alert = []
        alerts = self.db.query(Alert).all()
        for alert in alerts:
            alert_snoozed = self.db.query(UserAlertPreference).filter(
                UserAlertPreference.alert_id == alert.id,
                UserAlertPreference.is_snoozed == True
            ).count()
            
            alert_delivered = self.db.query(UserAlertPreference).filter(
                UserAlertPreference.alert_id == alert.id
            ).count()
            
            alert_read = self.db.query(UserAlertPreference).filter(
                UserAlertPreference.alert_id == alert.id,
                UserAlertPreference.is_read == True
            ).count()
            
            snoozed_per_alert.append({
                'alert_id': alert.id,
                'title': alert.title,
                'severity': alert.severity.value,
                'delivered': alert_delivered,
                'read': alert_read,
                'snoozed': alert_snoozed,
                'read_rate': round((alert_read / alert_delivered * 100) if alert_delivered > 0 else 0, 1)
            })
        
        return {
            'total_alerts': total_alerts,
            'active_alerts': active_alerts,
            'total_deliveries': total_deliveries,
            'total_preferences': total_preferences,
            'read_count': read_count,
            'snoozed_count': snoozed_count,
            'delivered_vs_read_rate': round((read_count / total_preferences * 100) if total_preferences > 0 else 0, 1),
            'severity_breakdown': severity_counts,
            'snoozed_per_alert': snoozed_per_alert
        }