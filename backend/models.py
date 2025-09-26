from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class SeverityLevel(enum.Enum):
    INFO = "Info"
    WARNING = "Warning"
    CRITICAL = "Critical"

class DeliveryType(enum.Enum):
    IN_APP = "In-App"
    EMAIL = "Email"
    SMS = "SMS"
    SLACK = "Slack"

class VisibilityType(enum.Enum):
    ORGANIZATION = "Organization"
    TEAM = "Team"
    USER = "User"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"))
    is_admin = Column(Boolean, default=False)
    
    team = relationship("Team", back_populates="members")
    alert_preferences = relationship("UserAlertPreference", back_populates="user")

class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    
    members = relationship("User", back_populates="team")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(Enum(SeverityLevel), nullable=False)
    delivery_type = Column(Enum(DeliveryType), default=DeliveryType.IN_APP)
    visibility_type = Column(Enum(VisibilityType), nullable=False)
    target_id = Column(Integer)  # team_id or user_id based on visibility_type
    
    start_time = Column(DateTime, default=datetime.utcnow)
    expiry_time = Column(DateTime)
    reminder_frequency = Column(Integer, default=2)  # hours
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    creator = relationship("User")
    deliveries = relationship("NotificationDelivery", back_populates="alert")
    preferences = relationship("UserAlertPreference", back_populates="alert")

class NotificationDelivery(Base):
    __tablename__ = "notification_deliveries"
    
    id = Column(Integer, primary_key=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    delivered_at = Column(DateTime, default=datetime.utcnow)
    delivery_type = Column(Enum(DeliveryType))
    
    alert = relationship("Alert", back_populates="deliveries")
    user = relationship("User")

class UserAlertPreference(Base):
    __tablename__ = "user_alert_preferences"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    alert_id = Column(Integer, ForeignKey("alerts.id"))
    is_read = Column(Boolean, default=False)
    is_snoozed = Column(Boolean, default=False)
    snoozed_until = Column(DateTime)
    last_reminded = Column(DateTime)
    
    user = relationship("User", back_populates="alert_preferences")
    alert = relationship("Alert", back_populates="preferences")