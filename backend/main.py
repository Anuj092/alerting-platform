import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from database import get_db, create_tables, seed_data
from models import Alert, User, Team, SeverityLevel, VisibilityType, DeliveryType
from services import AlertService, NotificationObserver, ReminderService, AnalyticsService
from scheduler import reminder_scheduler

app = FastAPI(title="Alerting & Notification Platform")

# Configure CORS for production and development
allowed_origins = [
    "http://localhost:3000",  # Development
]

# Add environment-specific origins
if os.getenv("FRONTEND_URL"):
    allowed_origins.append(os.getenv("FRONTEND_URL"))

# For production, allow all Render origins or use wildcard
if os.getenv("RENDER"):
    allowed_origins = ["*"]  # Allow all origins in production

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class AlertCreate(BaseModel):
    title: str
    message: str
    severity: SeverityLevel
    visibility_type: VisibilityType
    target_id: Optional[int] = None
    start_time: Optional[datetime] = None
    expiry_time: Optional[datetime] = None
    reminder_frequency: Optional[int] = 2

class AlertUpdate(BaseModel):
    title: Optional[str] = None
    message: Optional[str] = None
    severity: Optional[SeverityLevel] = None
    start_time: Optional[datetime] = None
    expiry_time: Optional[datetime] = None
    reminder_frequency: Optional[int] = None

class AlertResponse(BaseModel):
    id: int
    title: str
    message: str
    severity: str
    visibility_type: str
    is_active: bool
    created_at: datetime
    is_read: bool = False
    is_snoozed: bool = False

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    is_admin: bool
    team_name: Optional[str] = None

class UserCreate(BaseModel):
    name: str
    email: str
    team_id: Optional[int] = None
    is_admin: bool = False

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    team_id: Optional[int] = None
    is_admin: Optional[bool] = None

class TeamCreate(BaseModel):
    name: str

class TeamUpdate(BaseModel):
    name: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    create_tables()
    seed_data()
    # Start automatic reminder processing
    reminder_scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    reminder_scheduler.stop()

@app.get("/")
async def root():
    return {"message": "Alerting & Notification Platform API"}

# User endpoints
@app.get("/users", response_model=List[UserResponse])
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    result = []
    for user in users:
        result.append(UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            is_admin=user.is_admin,
            team_name=user.team.name if user.team else None
        ))
    return result

@app.get("/teams")
async def get_teams(db: Session = Depends(get_db)):
    teams = db.query(Team).all()
    return [{"id": team.id, "name": team.name} for team in teams]

@app.post("/teams")
async def create_team(team_data: TeamCreate, db: Session = Depends(get_db)):
    team = Team(name=team_data.name)
    db.add(team)
    db.commit()
    db.refresh(team)
    return {"id": team.id, "name": team.name}

@app.put("/teams/{team_id}")
async def update_team(team_id: int, team_data: TeamUpdate, db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    if team_data.name:
        team.name = team_data.name
    
    db.commit()
    return {"id": team.id, "name": team.name}

@app.delete("/teams/{team_id}")
async def delete_team(team_id: int, db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    db.delete(team)
    db.commit()
    return {"message": "Team deleted successfully"}

@app.post("/users")
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    user = User(
        name=user_data.name,
        email=user_data.email,
        team_id=user_data.team_id,
        is_admin=user_data.is_admin
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        is_admin=user.is_admin,
        team_name=user.team.name if user.team else None
    )

@app.put("/users/{user_id}")
async def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        is_admin=user.is_admin,
        team_name=user.team.name if user.team else None
    )

@app.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

# Admin endpoints
@app.post("/admin/alerts")
async def create_alert(alert_data: AlertCreate, created_by: int = 1, db: Session = Depends(get_db)):
    alert_service = AlertService(db)
    notification_observer = NotificationObserver(db, alert_service)
    alert_service.add_observer(notification_observer)
    
    alert = alert_service.create_alert(alert_data.dict(), created_by)
    return {"id": alert.id, "message": "Alert created successfully"}

@app.get("/admin/alerts")
async def get_all_alerts(
    severity: Optional[SeverityLevel] = None,
    status: Optional[str] = None,  # active, expired, inactive
    audience: Optional[VisibilityType] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Alert)
    
    # Apply filters
    if severity:
        query = query.filter(Alert.severity == severity)
    if audience:
        query = query.filter(Alert.visibility_type == audience)
    
    alerts = query.all()
    now = datetime.utcnow()
    result = []
    
    for alert in alerts:
        # Determine status
        alert_status = "inactive"
        if alert.is_active:
            if alert.expiry_time and alert.expiry_time < now:
                alert_status = "expired"
            else:
                alert_status = "active"
        
        # Filter by status if specified
        if status and alert_status != status:
            continue
        
        # Get user engagement stats
        total_users = len(get_target_users_for_alert(alert, db))
        preferences = db.query(UserAlertPreference).filter(
            UserAlertPreference.alert_id == alert.id
        ).all()
        
        snoozed_count = sum(1 for p in preferences if p.is_snoozed)
        read_count = sum(1 for p in preferences if p.is_read)
        
        # Determine if still recurring
        is_recurring = (
            alert.is_active and 
            alert.reminder_frequency > 0 and
            (not alert.expiry_time or alert.expiry_time > now) and
            snoozed_count < total_users * 0.8  # Less than 80% snoozed
        )
        
        result.append({
            "id": alert.id,
            "title": alert.title,
            "message": alert.message,
            "severity": alert.severity.value,
            "visibility_type": alert.visibility_type.value,
            "target_id": alert.target_id,
            "is_active": alert.is_active,
            "status": alert_status,
            "created_at": alert.created_at,
            "start_time": alert.start_time,
            "expiry_time": alert.expiry_time,
            "reminder_frequency": alert.reminder_frequency,
            "total_users": total_users,
            "snoozed_count": snoozed_count,
            "read_count": read_count,
            "is_recurring": is_recurring,
            "engagement_rate": round((read_count / total_users * 100) if total_users > 0 else 0, 1)
        })
    
    return result

def get_target_users_for_alert(alert: Alert, db: Session) -> List[User]:
    """Helper function to get target users for an alert"""
    if alert.visibility_type == VisibilityType.ORGANIZATION:
        return db.query(User).all()
    elif alert.visibility_type == VisibilityType.TEAM:
        return db.query(User).filter(User.team_id == alert.target_id).all()
    elif alert.visibility_type == VisibilityType.USER:
        user = db.query(User).filter(User.id == alert.target_id).first()
        return [user] if user else []
    return []

@app.put("/admin/alerts/{alert_id}")
async def update_alert(alert_id: int, alert_data: AlertUpdate, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    for field, value in alert_data.dict(exclude_unset=True).items():
        setattr(alert, field, value)
    
    db.commit()
    return {"message": "Alert updated successfully"}

@app.delete("/admin/alerts/{alert_id}")
async def archive_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.is_active = False
    db.commit()
    return {"message": "Alert archived successfully"}

@app.put("/admin/alerts/{alert_id}/toggle")
async def toggle_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.is_active = not alert.is_active
    db.commit()
    return {"message": f"Alert {'activated' if alert.is_active else 'deactivated'}"}

@app.put("/admin/alerts/{alert_id}/reminders")
async def toggle_reminders(alert_id: int, enabled: bool, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.reminder_frequency = 2 if enabled else 0
    db.commit()
    return {"message": f"Reminders {'enabled' if enabled else 'disabled'}"}

# User endpoints
@app.get("/users/{user_id}/alerts", response_model=List[AlertResponse])
async def get_user_alerts(user_id: int, db: Session = Depends(get_db)):
    alert_service = AlertService(db)
    alerts_data = alert_service.get_alerts_for_user(user_id)
    
    result = []
    for data in alerts_data:
        alert = data['alert']
        result.append(AlertResponse(
            id=alert.id,
            title=alert.title,
            message=alert.message,
            severity=alert.severity.value,
            visibility_type=alert.visibility_type.value,
            is_active=alert.is_active,
            created_at=alert.created_at,
            is_read=data['is_read'],
            is_snoozed=data['is_snoozed']
        ))
    
    return result

@app.post("/users/{user_id}/alerts/{alert_id}/snooze")
async def snooze_alert(user_id: int, alert_id: int, db: Session = Depends(get_db)):
    alert_service = AlertService(db)
    alert_service.snooze_alert(user_id, alert_id)
    return {"message": "Alert snoozed for 24 hours"}

@app.post("/users/{user_id}/alerts/{alert_id}/read")
async def mark_alert_read(user_id: int, alert_id: int, db: Session = Depends(get_db)):
    alert_service = AlertService(db)
    alert_service.mark_as_read(user_id, alert_id)
    return {"message": "Alert marked as read"}

@app.post("/users/{user_id}/alerts/{alert_id}/unread")
async def mark_alert_unread(user_id: int, alert_id: int, db: Session = Depends(get_db)):
    preference = db.query(UserAlertPreference).filter(
        UserAlertPreference.user_id == user_id,
        UserAlertPreference.alert_id == alert_id
    ).first()
    
    if preference:
        preference.is_read = False
        db.commit()
    return {"message": "Alert marked as unread"}

@app.get("/users/{user_id}/alerts/snoozed")
async def get_snoozed_alerts(user_id: int, db: Session = Depends(get_db)):
    preferences = db.query(UserAlertPreference).join(Alert).filter(
        UserAlertPreference.user_id == user_id,
        UserAlertPreference.is_snoozed == True
    ).all()
    
    result = []
    for pref in preferences:
        alert = pref.alert
        result.append({
            "id": alert.id,
            "title": alert.title,
            "message": alert.message,
            "severity": alert.severity.value,
            "snoozed_until": pref.snoozed_until,
            "created_at": alert.created_at
        })
    
    return result

# Analytics endpoint
@app.get("/analytics")
async def get_analytics(db: Session = Depends(get_db)):
    analytics_service = AnalyticsService(db)
    return analytics_service.get_dashboard_metrics()

# Reminder trigger (for demo purposes)
@app.post("/admin/trigger-reminders")
async def trigger_reminders(db: Session = Depends(get_db)):
    alert_service = AlertService(db)
    reminder_service = ReminderService(db, alert_service)
    reminder_service.process_reminders()
    return {"message": "Reminders processed"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)