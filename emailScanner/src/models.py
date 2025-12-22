"""
Database models for email scanner system.
Tracks emails, AI analysis, human decisions, and learned rules.
"""
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class Email(Base):
    """Email metadata and content"""
    __tablename__ = 'emails'
    
    id = Column(Integer, primary_key=True)
    email_id = Column(String(255), unique=True, nullable=False, index=True)  # IMAP UID (unique and persistent)
    sender = Column(String(255), nullable=False, index=True)
    recipient = Column(String(255))
    subject = Column(String(500))
    body_preview = Column(Text)  # First 500 chars for quick view
    body_full = Column(Text)  # Full body text
    received_date = Column(DateTime, nullable=False, index=True)
    size_bytes = Column(Integer)
    has_attachments = Column(Boolean, default=False)
    is_read = Column(Boolean, default=False)
    folder = Column(String(100), default='INBOX')
    
    # Timestamps
    fetched_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True, index=True)  # When email was deleted from server
    
    # Relationships
    analysis = relationship("Analysis", back_populates="email", uselist=False)
    decision = relationship("Decision", back_populates="email", uselist=False)
    
    def __repr__(self):
        return f"<Email(id={self.id}, sender={self.sender}, subject={self.subject[:30]})>"


class Analysis(Base):
    """AI analysis and recommendations for each email"""
    __tablename__ = 'analysis'
    
    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, ForeignKey('emails.id'), nullable=False, unique=True, index=True)
    
    # AI Recommendation
    recommendation = Column(String(20), nullable=False)  # 'delete', 'keep', 'archive'
    confidence_score = Column(Float, nullable=False)  # 0.0 to 1.0
    reasoning = Column(Text)  # AI explanation
    
    # Classification
    category = Column(String(50))  # 'newsletter', 'personal', 'promotional', etc.
    priority = Column(String(20))  # 'low', 'medium', 'high'
    
    # Model details
    model_name = Column(String(100))
    model_version = Column(String(50))
    
    # Status
    status = Column(String(20), default='pending_review', index=True)  # pending_review, approved, rejected, auto_deleted
    
    # Timestamps
    analyzed_at = Column(DateTime, default=datetime.utcnow, index=True)
    viewed_at = Column(DateTime, nullable=True, index=True)  # When email was first viewed by user
    
    # Relationships
    email = relationship("Email", back_populates="analysis")
    
    def __repr__(self):
        return f"<Analysis(id={self.id}, recommendation={self.recommendation}, confidence={self.confidence_score})>"


class Decision(Base):
    """Human decisions on AI recommendations - training data"""
    __tablename__ = 'decisions'
    
    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, ForeignKey('emails.id'), nullable=False, unique=True, index=True)
    
    # Human decision
    approved = Column(Boolean, nullable=False)  # True = agreed with AI, False = disagreed
    action_taken = Column(String(20))  # 'deleted', 'kept', 'archived'
    notes = Column(Text)  # Optional human notes
    
    # Timestamps
    decided_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    email = relationship("Email", back_populates="decision")
    
    def __repr__(self):
        return f"<Decision(id={self.id}, approved={self.approved}, action={self.action_taken})>"


class Rule(Base):
    """Learned patterns and rules for automated decision making"""
    __tablename__ = 'rules'
    
    id = Column(Integer, primary_key=True)
    
    # Rule definition
    rule_type = Column(String(50), nullable=False, index=True)  # 'sender_pattern', 'subject_keyword', 'category'
    pattern = Column(String(500), nullable=False)  # The pattern to match
    action = Column(String(20), nullable=False)  # 'delete', 'keep', 'archive'
    
    # Statistics
    confidence_score = Column(Float, default=0.0)  # Confidence based on training data
    times_matched = Column(Integer, default=0)
    times_approved = Column(Integer, default=0)
    times_rejected = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=False, index=True)  # Only active rules are used for auto-deletion
    requires_review = Column(Boolean, default=True)  # New rules require human review
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime)
    last_updated_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Rule(id={self.id}, type={self.rule_type}, pattern={self.pattern}, confidence={self.confidence_score})>"


class SystemStats(Base):
    """System statistics and metrics"""
    __tablename__ = 'system_stats'
    
    id = Column(Integer, primary_key=True)
    
    # Metrics
    total_emails_processed = Column(Integer, default=0)
    total_emails_deleted = Column(Integer, default=0)
    total_emails_kept = Column(Integer, default=0)
    ai_accuracy_rate = Column(Float, default=0.0)  # % of times human agreed with AI
    
    # Last run info
    last_scan_at = Column(DateTime)
    last_auto_delete_at = Column(DateTime)
    
    # Timestamps
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<SystemStats(processed={self.total_emails_processed}, accuracy={self.ai_accuracy_rate})>"


# Database initialization
def init_db(db_url='sqlite:///data/email_scanner.db'):
    """Initialize database and create all tables"""
    # If using SQLite, ensure the directory exists
    if db_url.startswith('sqlite:///'):
        # Extract the file path from the URL
        db_path = db_url.replace('sqlite:///', '')
        
        # If path is relative, make it relative to project root (parent of src)
        if not Path(db_path).is_absolute():
            project_root = Path(__file__).parent.parent
            db_path = project_root / db_path
            db_url = f'sqlite:///{db_path}'
        else:
            db_path = Path(db_path)
        
        # Create directory if it doesn't exist
        db_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"Database path: {db_path}")
    
    engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(engine)
    return engine


def get_session(engine):
    """Get a database session"""
    Session = sessionmaker(bind=engine)
    return Session()


if __name__ == '__main__':
    # Create database and tables
    engine = init_db()
    print("Database initialized successfully!")
    print(f"Tables created: {', '.join(Base.metadata.tables.keys())}")
