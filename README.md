# Alerting & Notification Platform

A modern, extensible alerting and notification system built with clean OOP principles, featuring a React/Next.js frontend and FastAPI backend.

## Features

### Admin Features
- ✅ Create unlimited alerts with title, message, severity (Info/Warning/Critical)
- ✅ Configure visibility (Organization/Team/User level)
- ✅ Set expiry times and manage alert lifecycle
- ✅ View all alerts with filtering and search
- ✅ Toggle alerts active/inactive
- ✅ Analytics dashboard with metrics

### End User Features
- ✅ Receive alerts based on visibility settings
- ✅ Mark alerts as read/unread
- ✅ Snooze alerts for 24 hours
- ✅ View alert history and status
- ✅ Real-time notifications (In-App)

### Technical Features
- ✅ Clean OOP design with Strategy and Observer patterns
- ✅ Extensible notification channels (In-App, Email, SMS ready)
- ✅ Reminder system (every 2 hours until snoozed/expired)
- ✅ Modern UI with dark/light mode
- ✅ Responsive design
- ✅ Type-safe APIs with TypeScript

## Architecture

### Backend (FastAPI + SQLAlchemy)
```
├── models.py          # Data models with relationships
├── services.py        # Business logic with design patterns
├── database.py        # Database setup and seed data
└── main.py           # API endpoints and FastAPI app
```

### Frontend (Next.js + Tailwind CSS)
```
├── components/        # Reusable UI components
├── lib/              # API client and utilities
└── app/              # Next.js app router pages
```

## Quick Start

### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Initialize database:**
```bash
python database.py
```

4. **Start the server:**
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start development server:**
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## API Endpoints

### User & Team Management
- `GET /users` - Get all users
- `POST /users` - Create new user
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user
- `GET /teams` - Get all teams
- `POST /teams` - Create new team
- `PUT /teams/{team_id}` - Update team
- `DELETE /teams/{team_id}` - Delete team

### User Alert Endpoints
- `GET /users/{user_id}/alerts` - Get user's active alerts
- `GET /users/{user_id}/alerts/snoozed` - Get user's snoozed alerts history
- `POST /users/{user_id}/alerts/{alert_id}/snooze` - Snooze alert for 24 hours
- `POST /users/{user_id}/alerts/{alert_id}/read` - Mark alert as read
- `POST /users/{user_id}/alerts/{alert_id}/unread` - Mark alert as unread

### Admin Endpoints
- `POST /admin/alerts` - Create new alert
- `GET /admin/alerts` - Get all alerts with optional filters (severity, status, audience)
- `PUT /admin/alerts/{alert_id}` - Update existing alert
- `DELETE /admin/alerts/{alert_id}` - Archive alert
- `PUT /admin/alerts/{alert_id}/toggle` - Toggle alert active/inactive
- `PUT /admin/alerts/{alert_id}/reminders` - Enable/disable reminders
- `POST /admin/trigger-reminders` - Trigger reminder processing

### Analytics
- `GET /analytics` - Get dashboard metrics

## Design Patterns Used

### Strategy Pattern
```python
class NotificationChannel(ABC):
    @abstractmethod
    def send(self, user: User, alert: Alert) -> bool:
        pass

class InAppNotificationChannel(NotificationChannel):
    def send(self, user: User, alert: Alert) -> bool:
        # Implementation
        return True
```

### Observer Pattern
```python
class AlertObserver(ABC):
    @abstractmethod
    def on_alert_created(self, alert: Alert):
        pass

class NotificationObserver(AlertObserver):
    def on_alert_created(self, alert: Alert):
        # Automatically notify users when alert is created
        pass
```

## Sample Data

The system comes with pre-seeded data:
- **Users**: Admin User (admin), John Doe (engineering), Jane Smith (marketing)
- **Teams**: Engineering, Marketing
- **Sample alerts** can be created through the admin interface

## Usage Examples

### Creating an Alert (Admin)
1. Login as admin user
2. Navigate to "Manage Alerts"
3. Click "Create Alert"
4. Fill in title, message, severity, and visibility
5. Set optional expiry time
6. Submit to create and automatically notify users

### Managing Alerts (User)
1. View alerts in "My Alerts" dashboard
2. Click eye icon to mark as read/unread
3. Click pause icon to snooze for 24 hours
4. Use search and filters to find specific alerts

### Analytics Dashboard
- View total alerts, active alerts, read count, and snoozed count
- See severity breakdown (Info/Warning/Critical)
- Monitor system usage and engagement

## Extensibility

### Adding New Notification Channels
```python
class SlackNotificationChannel(NotificationChannel):
    def send(self, user: User, alert: Alert) -> bool:
        # Implement Slack integration
        return True

# Register in AlertService
alert_service.notification_channels['Slack'] = SlackNotificationChannel()
```

### Adding New Visibility Types
1. Add enum value to `VisibilityType`
2. Update `_get_target_users` method in `NotificationObserver`
3. Update frontend form options

## Future Enhancements

- [ ] Email/SMS notification channels
- [ ] Custom reminder frequencies
- [ ] Scheduled alerts (cron-based)
- [ ] Alert escalations
- [ ] Role-based access control
- [ ] Push notifications
- [ ] Alert templates
- [ ] Bulk operations

## Technology Stack

**Backend:**
- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- SQLite (Database)
- Pydantic (Data validation)

**Frontend:**
- Next.js 14 (React framework)
- TypeScript (Type safety)
- Tailwind CSS (Styling)
- Lucide React (Icons)

## Contributing

1. Follow the existing code patterns and OOP principles
2. Add tests for new features
3. Update documentation for API changes
4. Ensure responsive design for UI changes

## License

MIT License - see LICENSE file for details