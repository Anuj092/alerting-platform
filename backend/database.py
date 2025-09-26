from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Team, SeverityLevel, VisibilityType
from datetime import datetime, timedelta

DATABASE_URL = "sqlite:///./alerts.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed_data():
    """Create sample data for testing"""
    db = SessionLocal()
    
    # Check if data already exists
    if db.query(User).first():
        db.close()
        return
    
    # Create teams
    engineering = Team(name="Engineering")
    marketing = Team(name="Marketing")
    db.add_all([engineering, marketing])
    db.flush()
    
    # Create users
    admin = User(name="Admin User", email="admin@company.com", is_admin=True, team_id=engineering.id)
    john = User(name="John Doe", email="john@company.com", team_id=engineering.id)
    jane = User(name="Jane Smith", email="jane@company.com", team_id=marketing.id)
    
    db.add_all([admin, john, jane])
    db.commit()
    db.close()

if __name__ == "__main__":
    create_tables()
    seed_data()
    print("Database initialized with sample data")