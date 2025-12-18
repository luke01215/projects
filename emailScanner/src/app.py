"""
FastAPI web application for reviewing and approving AI email recommendations.
Provides REST API and simple web interface.
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime, UTC
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from models import Email, Analysis, Decision, Rule, SystemStats, init_db, get_session
from settings import load_settings

# Initialize FastAPI app
app = FastAPI(
    title="Email Scanner Review Interface",
    description="Review and approve AI email deletion recommendations",
    version="1.0.0"
)

# Database dependency
def get_db():
    """Database session dependency"""
    settings = load_settings()
    engine = init_db(settings.database_url)
    db = get_session(engine)
    try:
        yield db
    finally:
        db.close()


# Request/Response Models
class EmailSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email_id: str
    sender: str
    subject: str
    received_date: datetime
    recommendation: str
    confidence_score: float
    category: Optional[str] = None
    priority: Optional[str] = None
    status: str


class EmailDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email_id: str
    sender: str
    recipient: str
    subject: str
    body_preview: str
    received_date: datetime
    size_bytes: int
    has_attachments: bool
    recommendation: str
    confidence_score: float
    reasoning: str
    category: Optional[str] = None
    priority: Optional[str] = None
    status: str


class DecisionRequest(BaseModel):
    approved: bool
    action_taken: str  # 'deleted', 'kept', 'archived'
    notes: Optional[str] = None


class StatsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    total_emails_processed: int
    total_pending_review: int
    total_approved: int
    total_rejected: int
    ai_accuracy_rate: float
    last_scan_at: Optional[datetime]


class SenderGroup(BaseModel):
    sender: str
    email_count: int
    most_common_recommendation: str
    most_common_category: str
    avg_confidence: float
    oldest_date: datetime
    newest_date: datetime
    sample_subject: str


class BulkDecisionRequest(BaseModel):
    sender: str
    approved: bool
    action_taken: str  # 'deleted', 'kept', 'archived'
    notes: Optional[str] = None


class CategoryGroup(BaseModel):
    category: str
    email_count: int
    most_common_recommendation: str
    avg_confidence: float
    oldest_date: datetime
    newest_date: datetime
    sample_sender: str
    sample_subject: str


class DateRangeGroup(BaseModel):
    date_range: str
    email_count: int
    most_common_recommendation: str
    most_common_category: str
    avg_confidence: float
    start_date: datetime
    end_date: datetime
    sample_sender: str
    sample_subject: str


class BulkCategoryDecisionRequest(BaseModel):
    category: str
    approved: bool
    action_taken: str
    notes: Optional[str] = None


class BulkDateRangeDecisionRequest(BaseModel):
    start_date: str  # ISO format
    end_date: str  # ISO format
    approved: bool
    action_taken: str
    notes: Optional[str] = None


class CategoryGroup(BaseModel):
    category: str
    email_count: int
    most_common_recommendation: str
    avg_confidence: float
    oldest_date: datetime
    newest_date: datetime
    sample_sender: str
    sample_subject: str


class DateRangeGroup(BaseModel):
    date_range: str
    email_count: int
    most_common_recommendation: str
    most_common_category: str
    avg_confidence: float
    start_date: datetime
    end_date: datetime
    sample_sender: str
    sample_subject: str


class BulkCategoryDecisionRequest(BaseModel):
    category: str
    approved: bool
    action_taken: str
    notes: Optional[str] = None


class BulkDateRangeDecisionRequest(BaseModel):
    start_date: str  # ISO format
    end_date: str  # ISO format
    approved: bool
    action_taken: str
    notes: Optional[str] = None


# API Routes

@app.get("/")
async def root():
    """Root endpoint with welcome message"""
    return {
        "message": "Email Scanner Review API",
        "version": "1.0.0",
        "endpoints": {
            "pending": "/api/emails/pending",
            "email_detail": "/api/emails/{email_id}",
            "decide": "/api/emails/{email_id}/decide",
            "stats": "/api/stats"
        }
    }


@app.get("/api/emails/pending", response_model=List[EmailSummary])
async def get_pending_emails(
    limit: int = 50,
    skip: int = 0,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all emails pending review with optional search filter"""
    try:
        query = db.query(Email, Analysis).join(Analysis).filter(
            Analysis.status == 'pending_review'
        )
        
        # Apply search filter if provided
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Email.sender.ilike(search_term)) |
                (Email.subject.ilike(search_term)) |
                (Email.body_preview.ilike(search_term))
            )
        
        emails = query.order_by(desc(Email.received_date)).limit(limit).offset(skip).all()
        
        results = []
        for email, analysis in emails:
            results.append(EmailSummary(
                id=email.id,
                email_id=email.email_id,
                sender=email.sender,
                subject=email.subject or "(no subject)",
                received_date=email.received_date,
                recommendation=analysis.recommendation,
                confidence_score=analysis.confidence_score,
                category=analysis.category or "unknown",
                priority=analysis.priority or "medium",
                status=analysis.status
            ))
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/emails/{email_id}", response_model=EmailDetail)
async def get_email_detail(email_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific email"""
    try:
        result = db.query(Email, Analysis).join(Analysis).filter(
            Email.id == email_id
        ).first()
        
        if not result:
            raise HTTPException(status_code=404, detail="Email not found")
        
        email, analysis = result
        
        return EmailDetail(
            id=email.id,
            email_id=email.email_id,
            sender=email.sender,
            recipient=email.recipient or "",
            subject=email.subject or "(no subject)",
            body_preview=email.body_preview or "",
            received_date=email.received_date,
            size_bytes=email.size_bytes,
            has_attachments=email.has_attachments,
            recommendation=analysis.recommendation,
            confidence_score=analysis.confidence_score,
            reasoning=analysis.reasoning or "",
            category=analysis.category or "unknown",
            priority=analysis.priority or "medium",
            status=analysis.status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/emails/{email_id}/decide")
async def make_decision(
    email_id: int,
    decision: DecisionRequest,
    db: Session = Depends(get_db)
):
    """Record human decision on an email recommendation"""
    try:
        # Get email and analysis
        email = db.query(Email).filter(Email.id == email_id).first()
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        
        analysis = db.query(Analysis).filter(Analysis.email_id == email_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Check if decision already exists
        existing_decision = db.query(Decision).filter(Decision.email_id == email_id).first()
        
        if existing_decision:
            # Update existing decision
            existing_decision.approved = decision.approved
            existing_decision.action_taken = decision.action_taken
            existing_decision.notes = decision.notes
            existing_decision.decided_at = datetime.now(UTC)
        else:
            # Create new decision record
            decision_record = Decision(
                email_id=email_id,
                approved=decision.approved,
                action_taken=decision.action_taken,
                notes=decision.notes,
                decided_at=datetime.now(UTC)
            )
            db.add(decision_record)
        
        # Update analysis status
        if decision.approved:
            analysis.status = 'approved'
        else:
            analysis.status = 'rejected'
        
        db.commit()
        
        # Update statistics
        _update_accuracy_stats(db)
        
        return {
            "message": "Decision recorded successfully",
            "email_id": email_id,
            "approved": decision.approved,
            "action_taken": decision.action_taken
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats", response_model=StatsResponse)
async def get_statistics(db: Session = Depends(get_db)):
    """Get system statistics and metrics"""
    try:
        # Get or create stats
        stats = db.query(SystemStats).first()
        if not stats:
            stats = SystemStats(
                total_emails_processed=0,
                total_emails_deleted=0,
                total_emails_kept=0,
                ai_accuracy_rate=0.0
            )
            db.add(stats)
            db.commit()
        
        # Count pending reviews
        pending_count = db.query(Analysis).filter(
            Analysis.status == 'pending_review'
        ).count()
        
        # Count approved/rejected
        approved_count = db.query(Analysis).filter(
            Analysis.status == 'approved'
        ).count()
        
        rejected_count = db.query(Analysis).filter(
            Analysis.status == 'rejected'
        ).count()
        
        return StatsResponse(
            total_emails_processed=stats.total_emails_processed or 0,
            total_pending_review=pending_count,
            total_approved=approved_count,
            total_rejected=rejected_count,
            ai_accuracy_rate=stats.ai_accuracy_rate or 0.0,
            last_scan_at=stats.last_scan_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/emails/history", response_model=List[EmailSummary])
async def get_email_history(
    status: Optional[str] = None,
    limit: int = 50,
    skip: int = 0,
    db: Session = Depends(get_db)
):
    """Get historical emails with optional status filter"""
    try:
        query = db.query(Email, Analysis).join(Analysis)
        
        if status:
            query = query.filter(Analysis.status == status)
        
        emails = query.order_by(desc(Email.received_date)).limit(limit).offset(skip).all()
        
        results = []
        for email, analysis in emails:
            results.append(EmailSummary(
                id=email.id,
                email_id=email.email_id,
                sender=email.sender,
                subject=email.subject or "(no subject)",
                received_date=email.received_date,
                recommendation=analysis.recommendation,
                confidence_score=analysis.confidence_score,
                category=analysis.category,
                priority=analysis.priority,
                status=analysis.status
            ))
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _update_accuracy_stats(db: Session):
    """Calculate and update AI accuracy statistics"""
    try:
        # Count total decisions
        total_decisions = db.query(Decision).count()
        
        if total_decisions == 0:
            return
        
        # Count approved decisions
        approved_decisions = db.query(Decision).filter(
            Decision.approved == True
        ).count()
        
        # Calculate accuracy rate
        accuracy_rate = (approved_decisions / total_decisions) * 100
        
        # Update stats
        stats = db.query(SystemStats).first()
        if not stats:
            stats = SystemStats()
            db.add(stats)
        
        stats.ai_accuracy_rate = accuracy_rate
        stats.updated_at = datetime.now(UTC)
        
        db.commit()
        
    except Exception as e:
        print(f"Error updating accuracy stats: {e}")


@app.get("/api/senders/pending", response_model=List[SenderGroup])
async def get_pending_senders(db: Session = Depends(get_db)):
    """Get emails grouped by sender for bulk review"""
    try:
        # Query emails pending review grouped by sender
        # Using a more efficient query with single pass through data
        from sqlalchemy import case
        
        results = db.query(
            Email.sender,
            func.count(Email.id).label('email_count'),
            func.min(Email.received_date).label('oldest_date'),
            func.max(Email.received_date).label('newest_date'),
            func.avg(Analysis.confidence_score).label('avg_confidence'),
            func.max(Email.subject).label('sample_subject'),  # Get any subject as sample
            # Get most common recommendation using conditional aggregation
            func.sum(case((Analysis.recommendation == 'delete', 1), else_=0)).label('delete_count'),
            func.sum(case((Analysis.recommendation == 'keep', 1), else_=0)).label('keep_count'),
            # Get most common category
            func.max(Analysis.category).label('sample_category')  # Simplified: just take one
        ).join(Analysis).filter(
            Analysis.status == 'pending_review'
        ).group_by(Email.sender).order_by(func.count(Email.id).desc()).all()
        
        sender_groups = []
        for result in results:
            # Determine most common recommendation from counts
            most_common_rec = 'delete' if result.delete_count > result.keep_count else 'keep'
            
            sender_groups.append(SenderGroup(
                sender=result.sender,
                email_count=result.email_count,
                most_common_recommendation=most_common_rec,
                most_common_category=result.sample_category or 'unknown',
                avg_confidence=float(result.avg_confidence),
                oldest_date=result.oldest_date,
                newest_date=result.newest_date,
                sample_subject=result.sample_subject or '(no subject)'
            ))
        
        return sender_groups
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/senders/{sender}/emails", response_model=List[EmailSummary])
async def get_sender_emails(sender: str, db: Session = Depends(get_db)):
    """Get all pending emails from a specific sender"""
    try:
        emails = db.query(Email, Analysis).join(Analysis).filter(
            Email.sender == sender,
            Analysis.status == 'pending_review'
        ).order_by(desc(Email.received_date)).all()
        
        results = []
        for email, analysis in emails:
            results.append(EmailSummary(
                id=email.id,
                email_id=email.email_id,
                sender=email.sender,
                subject=email.subject or "(no subject)",
                received_date=email.received_date,
                recommendation=analysis.recommendation,
                confidence_score=analysis.confidence_score,
                category=analysis.category or "unknown",
                priority=analysis.priority or "medium",
                status=analysis.status
            ))
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/senders/decide-bulk")
async def make_bulk_decision(
    decision: BulkDecisionRequest,
    db: Session = Depends(get_db)
):
    """Make a decision for all pending emails from a specific sender"""
    try:
        # Get all pending emails from this sender
        emails = db.query(Email, Analysis).join(Analysis).filter(
            Email.sender == decision.sender,
            Analysis.status == 'pending_review'
        ).all()
        
        if not emails:
            raise HTTPException(status_code=404, detail="No pending emails from this sender")
        
        updated_count = 0
        
        for email, analysis in emails:
            # Check if decision already exists
            existing_decision = db.query(Decision).filter(Decision.email_id == email.id).first()
            
            if existing_decision:
                # Update existing decision
                existing_decision.approved = decision.approved
                existing_decision.action_taken = decision.action_taken
                existing_decision.notes = decision.notes
                existing_decision.decided_at = datetime.now(UTC)
            else:
                # Create new decision record
                decision_record = Decision(
                    email_id=email.id,
                    approved=decision.approved,
                    action_taken=decision.action_taken,
                    notes=decision.notes,
                    decided_at=datetime.now(UTC)
                )
                db.add(decision_record)
            
            # Update analysis status
            if decision.approved:
                analysis.status = 'approved'
            else:
                analysis.status = 'rejected'
            
            updated_count += 1
        
        db.commit()
        
        # Update statistics
        _update_accuracy_stats(db)
        
        return {
            "message": f"Bulk decision recorded for {updated_count} emails",
            "sender": decision.sender,
            "emails_updated": updated_count,
            "approved": decision.approved,
            "action_taken": decision.action_taken
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/senders/apply-recommendations")
async def apply_sender_recommendations(
    request: dict,
    db: Session = Depends(get_db)
):
    """Apply individual AI recommendations for all pending emails from a specific sender"""
    try:
        sender = request.get('sender')
        if not sender:
            raise HTTPException(status_code=400, detail="Sender is required")
        
        # Get all pending emails from this sender
        emails = db.query(Email, Analysis).join(Analysis).filter(
            Email.sender == sender,
            Analysis.status == 'pending_review'
        ).all()
        
        if not emails:
            raise HTTPException(status_code=404, detail="No pending emails from this sender")
        
        updated_count = 0
        stats = {'kept': 0, 'deleted': 0, 'archived': 0}
        
        for email, analysis in emails:
            # Determine action based on AI recommendation
            if analysis.recommendation == 'keep':
                action_taken = 'kept'
                approved = True
            elif analysis.recommendation == 'delete':
                action_taken = 'deleted'
                approved = True
            elif analysis.recommendation == 'archive':
                action_taken = 'archived'
                approved = True
            else:
                continue  # Skip if no clear recommendation
            
            stats[action_taken] += 1
            
            # Check if decision already exists
            existing_decision = db.query(Decision).filter(Decision.email_id == email.id).first()
            
            if existing_decision:
                # Update existing decision
                existing_decision.approved = approved
                existing_decision.action_taken = action_taken
                existing_decision.notes = "Applied AI recommendation"
                existing_decision.decided_at = datetime.now(UTC)
            else:
                # Create new decision record
                decision_record = Decision(
                    email_id=email.id,
                    approved=approved,
                    action_taken=action_taken,
                    notes="Applied AI recommendation",
                    decided_at=datetime.now(UTC)
                )
                db.add(decision_record)
            
            # Update analysis status
            analysis.status = 'approved'
            updated_count += 1
        
        db.commit()
        
        # Update statistics
        _update_accuracy_stats(db)
        
        summary = f"Applied recommendations: {stats['kept']} kept, {stats['deleted']} deleted, {stats['archived']} archived"
        
        return {
            "message": summary,
            "sender": sender,
            "emails_updated": updated_count,
            "stats": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/categories/pending", response_model=List[CategoryGroup])
async def get_pending_categories(db: Session = Depends(get_db)):
    """Get emails grouped by category for bulk review"""
    try:
        # Query emails pending review grouped by category
        from sqlalchemy import case
        
        results = db.query(
            Analysis.category,
            func.count(Email.id).label('email_count'),
            func.min(Email.received_date).label('oldest_date'),
            func.max(Email.received_date).label('newest_date'),
            func.avg(Analysis.confidence_score).label('avg_confidence'),
            func.max(Email.sender).label('sample_sender'),
            func.max(Email.subject).label('sample_subject'),
            # Get most common recommendation using conditional aggregation
            func.sum(case((Analysis.recommendation == 'delete', 1), else_=0)).label('delete_count'),
            func.sum(case((Analysis.recommendation == 'keep', 1), else_=0)).label('keep_count')
        ).join(Email).filter(
            Analysis.status == 'pending_review'
        ).group_by(Analysis.category).order_by(func.count(Email.id).desc()).all()
        
        category_groups = []
        for result in results:
            category = result.category or 'unknown'
            
            # Determine most common recommendation from counts
            most_common_rec = 'delete' if result.delete_count > result.keep_count else 'keep'
            
            category_groups.append(CategoryGroup(
                category=category,
                email_count=result.email_count,
                most_common_recommendation=most_common_rec,
                avg_confidence=float(result.avg_confidence),
                oldest_date=result.oldest_date,
                newest_date=result.newest_date,
                sample_sender=result.sample_sender or '(unknown)',
                sample_subject=result.sample_subject or '(no subject)'
            ))
        
        return category_groups
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/categories/{category}/emails", response_model=List[EmailSummary])
async def get_category_emails(category: str, db: Session = Depends(get_db)):
    """Get all pending emails from a specific category"""
    try:
        emails = db.query(Email, Analysis).join(Analysis).filter(
            Analysis.category == category,
            Analysis.status == 'pending_review'
        ).order_by(desc(Email.received_date)).all()
        
        results = []
        for email, analysis in emails:
            results.append(EmailSummary(
                id=email.id,
                email_id=email.email_id,
                sender=email.sender,
                subject=email.subject or "(no subject)",
                received_date=email.received_date,
                recommendation=analysis.recommendation,
                confidence_score=analysis.confidence_score,
                category=analysis.category or "unknown",
                priority=analysis.priority or "medium",
                status=analysis.status
            ))
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/categories/decide-bulk")
async def make_bulk_category_decision(
    decision: BulkCategoryDecisionRequest,
    db: Session = Depends(get_db)
):
    """Make a decision for all pending emails in a specific category"""
    try:
        # Get all pending emails in this category
        emails = db.query(Email, Analysis).join(Analysis).filter(
            Analysis.category == decision.category,
            Analysis.status == 'pending_review'
        ).all()
        
        if not emails:
            raise HTTPException(status_code=404, detail="No pending emails in this category")
        
        updated_count = 0
        
        for email, analysis in emails:
            # Check if decision already exists
            existing_decision = db.query(Decision).filter(Decision.email_id == email.id).first()
            
            if existing_decision:
                # Update existing decision
                existing_decision.approved = decision.approved
                existing_decision.action_taken = decision.action_taken
                existing_decision.notes = decision.notes
                existing_decision.decided_at = datetime.now(UTC)
            else:
                # Create new decision record
                decision_record = Decision(
                    email_id=email.id,
                    approved=decision.approved,
                    action_taken=decision.action_taken,
                    notes=decision.notes,
                    decided_at=datetime.now(UTC)
                )
                db.add(decision_record)
            
            # Update analysis status
            if decision.approved:
                analysis.status = 'approved'
            else:
                analysis.status = 'rejected'
            
            updated_count += 1
        
        db.commit()
        
        # Update statistics
        _update_accuracy_stats(db)
        
        return {
            "message": f"Bulk decision recorded for {updated_count} emails",
            "category": decision.category,
            "emails_updated": updated_count,
            "approved": decision.approved,
            "action_taken": decision.action_taken
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/categories/apply-recommendations")
async def apply_category_recommendations(
    request: dict,
    db: Session = Depends(get_db)
):
    """Apply individual AI recommendations for all pending emails in a specific category"""
    try:
        category = request.get('category')
        if not category:
            raise HTTPException(status_code=400, detail="Category is required")
        
        # Get all pending emails in this category
        emails = db.query(Email, Analysis).join(Analysis).filter(
            Analysis.category == category,
            Analysis.status == 'pending_review'
        ).all()
        
        if not emails:
            raise HTTPException(status_code=404, detail="No pending emails in this category")
        
        updated_count = 0
        stats = {'kept': 0, 'deleted': 0, 'archived': 0}
        
        for email, analysis in emails:
            # Determine action based on AI recommendation
            if analysis.recommendation == 'keep':
                action_taken = 'kept'
                approved = True
            elif analysis.recommendation == 'delete':
                action_taken = 'deleted'
                approved = True
            elif analysis.recommendation == 'archive':
                action_taken = 'archived'
                approved = True
            else:
                continue  # Skip if no clear recommendation
            
            stats[action_taken] += 1
            
            # Check if decision already exists
            existing_decision = db.query(Decision).filter(Decision.email_id == email.id).first()
            
            if existing_decision:
                # Update existing decision
                existing_decision.approved = approved
                existing_decision.action_taken = action_taken
                existing_decision.notes = "Applied AI recommendation"
                existing_decision.decided_at = datetime.now(UTC)
            else:
                # Create new decision record
                decision_record = Decision(
                    email_id=email.id,
                    approved=approved,
                    action_taken=action_taken,
                    notes="Applied AI recommendation",
                    decided_at=datetime.now(UTC)
                )
                db.add(decision_record)
            
            # Update analysis status
            analysis.status = 'approved'
            updated_count += 1
        
        db.commit()
        
        # Update statistics
        _update_accuracy_stats(db)
        
        summary = f"Applied recommendations: {stats['kept']} kept, {stats['deleted']} deleted, {stats['archived']} archived"
        
        return {
            "message": summary,
            "category": category,
            "emails_updated": updated_count,
            "stats": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/date-ranges/pending", response_model=List[DateRangeGroup])
async def get_pending_date_ranges(db: Session = Depends(get_db)):
    """Get emails grouped by date ranges for bulk review"""
    try:
        from datetime import timedelta
        from sqlalchemy import case
        
        now = datetime.now(UTC)
        date_ranges = [
            ('Last 7 days', now - timedelta(days=7), now),
            ('Last 30 days', now - timedelta(days=30), now - timedelta(days=7)),
            ('Last 3 months', now - timedelta(days=90), now - timedelta(days=30)),
            ('Last 6 months', now - timedelta(days=180), now - timedelta(days=90)),
            ('Last year', now - timedelta(days=365), now - timedelta(days=180)),
            ('Over a year old', datetime(2000, 1, 1, tzinfo=UTC), now - timedelta(days=365))
        ]
        
        range_groups = []
        
        for range_name, start_date, end_date in date_ranges:
            # Query emails in this date range with single query
            results = db.query(
                func.count(Email.id).label('email_count'),
                func.avg(Analysis.confidence_score).label('avg_confidence'),
                func.min(Email.received_date).label('oldest_date'),
                func.max(Email.received_date).label('newest_date'),
                func.max(Email.sender).label('sample_sender'),
                func.max(Email.subject).label('sample_subject'),
                func.max(Analysis.category).label('sample_category'),
                # Get most common recommendation using conditional aggregation
                func.sum(case((Analysis.recommendation == 'delete', 1), else_=0)).label('delete_count'),
                func.sum(case((Analysis.recommendation == 'keep', 1), else_=0)).label('keep_count')
            ).join(Analysis).filter(
                Analysis.status == 'pending_review',
                Email.received_date >= start_date,
                Email.received_date < end_date
            ).first()
            
            if not results or results.email_count == 0:
                continue
            
            # Determine most common recommendation from counts
            most_common_rec = 'delete' if results.delete_count > results.keep_count else 'keep'
            
            range_groups.append(DateRangeGroup(
                date_range=range_name,
                email_count=results.email_count,
                most_common_recommendation=most_common_rec,
                most_common_category=results.sample_category or 'unknown',
                avg_confidence=float(results.avg_confidence),
                start_date=start_date,
                end_date=end_date,
                sample_sender=results.sample_sender or '(unknown)',
                sample_subject=results.sample_subject or '(no subject)'
            ))
        
        return range_groups
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/date-ranges/emails")
async def get_date_range_emails(
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db)
):
    """Get all pending emails in a specific date range"""
    try:
        # Parse ISO format dates
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        emails = db.query(Email, Analysis).join(Analysis).filter(
            Analysis.status == 'pending_review',
            Email.received_date >= start,
            Email.received_date < end
        ).order_by(desc(Email.received_date)).all()
        
        results = []
        for email, analysis in emails:
            results.append(EmailSummary(
                id=email.id,
                email_id=email.email_id,
                sender=email.sender,
                subject=email.subject or "(no subject)",
                received_date=email.received_date,
                recommendation=analysis.recommendation,
                confidence_score=analysis.confidence_score,
                category=analysis.category or "unknown",
                priority=analysis.priority or "medium",
                status=analysis.status
            ))
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/date-ranges/decide-bulk")
async def make_bulk_date_range_decision(
    decision: BulkDateRangeDecisionRequest,
    db: Session = Depends(get_db)
):
    """Make a decision for all pending emails in a specific date range"""
    try:
        # Parse ISO format dates
        start_date = datetime.fromisoformat(decision.start_date.replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(decision.end_date.replace('Z', '+00:00'))
        
        # Get all pending emails in this date range
        emails = db.query(Email, Analysis).join(Analysis).filter(
            Analysis.status == 'pending_review',
            Email.received_date >= start_date,
            Email.received_date < end_date
        ).all()
        
        if not emails:
            raise HTTPException(status_code=404, detail="No pending emails in this date range")
        
        updated_count = 0
        
        for email, analysis in emails:
            # Check if decision already exists
            existing_decision = db.query(Decision).filter(Decision.email_id == email.id).first()
            
            if existing_decision:
                # Update existing decision
                existing_decision.approved = decision.approved
                existing_decision.action_taken = decision.action_taken
                existing_decision.notes = decision.notes
                existing_decision.decided_at = datetime.now(UTC)
            else:
                # Create new decision record
                decision_record = Decision(
                    email_id=email.id,
                    approved=decision.approved,
                    action_taken=decision.action_taken,
                    notes=decision.notes,
                    decided_at=datetime.now(UTC)
                )
                db.add(decision_record)
            
            # Update analysis status
            if decision.approved:
                analysis.status = 'approved'
            else:
                analysis.status = 'rejected'
            
            updated_count += 1
        
        db.commit()
        
        # Update statistics
        _update_accuracy_stats(db)
        
        return {
            "message": f"Bulk decision recorded for {updated_count} emails",
            "date_range": f"{decision.start_date} to {decision.end_date}",
            "emails_updated": updated_count,
            "approved": decision.approved,
            "action_taken": decision.action_taken
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/date-ranges/apply-recommendations")
async def apply_date_range_recommendations(
    request: dict,
    db: Session = Depends(get_db)
):
    """Apply individual AI recommendations for all pending emails in a specific date range"""
    try:
        start_date_str = request.get('start_date')
        end_date_str = request.get('end_date')
        
        if not start_date_str or not end_date_str:
            raise HTTPException(status_code=400, detail="Start and end dates are required")
        
        # Parse ISO format dates
        start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
        
        # Get all pending emails in this date range
        emails = db.query(Email, Analysis).join(Analysis).filter(
            Email.received_date >= start_date,
            Email.received_date <= end_date,
            Analysis.status == 'pending_review'
        ).all()
        
        if not emails:
            raise HTTPException(status_code=404, detail="No pending emails in this date range")
        
        updated_count = 0
        stats = {'kept': 0, 'deleted': 0, 'archived': 0}
        
        for email, analysis in emails:
            # Determine action based on AI recommendation
            if analysis.recommendation == 'keep':
                action_taken = 'kept'
                approved = True
            elif analysis.recommendation == 'delete':
                action_taken = 'deleted'
                approved = True
            elif analysis.recommendation == 'archive':
                action_taken = 'archived'
                approved = True
            else:
                continue  # Skip if no clear recommendation
            
            stats[action_taken] += 1
            
            # Check if decision already exists
            existing_decision = db.query(Decision).filter(Decision.email_id == email.id).first()
            
            if existing_decision:
                # Update existing decision
                existing_decision.approved = approved
                existing_decision.action_taken = action_taken
                existing_decision.notes = "Applied AI recommendation"
                existing_decision.decided_at = datetime.now(UTC)
            else:
                # Create new decision record
                decision_record = Decision(
                    email_id=email.id,
                    approved=approved,
                    action_taken=action_taken,
                    notes="Applied AI recommendation",
                    decided_at=datetime.now(UTC)
                )
                db.add(decision_record)
            
            # Update analysis status
            analysis.status = 'approved'
            updated_count += 1
        
        db.commit()
        
        # Update statistics
        _update_accuracy_stats(db)
        
        summary = f"Applied recommendations: {stats['kept']} kept, {stats['deleted']} deleted, {stats['archived']} archived"
        
        return {
            "message": summary,
            "date_range": f"{start_date_str} to {end_date_str}",
            "emails_updated": updated_count,
            "stats": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# Simple HTML interface
@app.get("/ui")
async def web_interface():
    """Serve the static HTML interface"""
    static_file = Path(__file__).parent / "static" / "index.html"
    return FileResponse(static_file)


if __name__ == '__main__':
    import uvicorn
    from settings import load_settings
    
    config = load_settings()
    host = config.web_host
    port = config.web_port
    
    print("\n" + "=" * 80)
    print("📧 EMAIL SCANNER - WEB INTERFACE")
    print("=" * 80)
    print(f"\n🌐 Web UI:        http://localhost:{port}/ui")
    print(f"📚 API Docs:      http://localhost:{port}/docs")
    print(f"🔍 API Endpoints:")
    print(f"   - GET  /api/emails/pending        List emails pending review")
    print(f"   - GET  /api/emails/{{id}}           Get email details")
    print(f"   - POST /api/emails/{{id}}/decide    Record decision")
    print(f"   - GET  /api/senders/pending       Group emails by sender")
    print(f"   - POST /api/senders/decide-bulk   Bulk decision by sender")
    print(f"   - GET  /api/stats                 System statistics")
    print(f"\n💡 Tip: Use 'By Sender' view for faster bulk review")
    print(f"💡 Tip: Press Ctrl+C to stop the server")
    print("=" * 80 + "\n")
    
    uvicorn.run(app, host=host, port=port)
