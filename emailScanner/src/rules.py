"""
Rules engine for pre-filtering emails before AI analysis.
Allows setting up automatic keep/delete decisions based on sender, content, age, etc.
"""
import logging
import re
from datetime import datetime, timedelta, UTC
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class EmailRules:
    """Email filtering rules engine"""
    
    # Default VIP senders (if not configured)
    DEFAULT_VIP_SENDERS = [
        'cdarling926@gmail.com',
        'grace0614@gmail.com',
    ]
    
    # Default event keywords
    DEFAULT_EVENT_KEYWORDS = [
        'calendar',
        'meeting',
        'appointment',
        'rsvp',
        'invite',
        'invitation',
        'event',
        'reminder',
        'scheduled',
        'webinar',
        'conference',
    ]
    
    # Default job keywords
    DEFAULT_JOB_KEYWORDS = [
        'job opportunity',
        'job alert',
        'career opportunity',
        'now hiring',
        'we\'re hiring',
        'position available',
        'job opening',
        'apply now',
        'recruitment',
        'recruiter',
    ]
    
    # Default newsletter/news senders to auto-delete if old
    DEFAULT_NEWSLETTER_SENDERS = [
        'thedaily@theskimm.com',
        '@newsletters.',
        'noreply@',
        'news@',
    ]
    
    # Promotional/sale keywords for auto-delete
    DEFAULT_PROMOTIONAL_KEYWORDS = [
        'sale',
        'discount',
        '% off',
        'limited time',
        'deal',
        'offer',
        'promotion',
        'exclusive',
        'flash sale',
        'clearance',
        'save now',
        'shop now',
        'buy now',
        'order now',
    ]
    
    # Newsletter/promotional patterns (potential auto-delete)
    PROMOTIONAL_PATTERNS = [
        r'unsubscribe',
        r'click here',
        r'\d+% off',
        r'limited time',
        r'don\'t miss',
        r'exclusive offer',
    ]
    
    def __init__(self, vip_senders=None, event_keywords=None, job_keywords=None, old_event_days=60,
                 old_job_days=180, newsletter_senders=None, old_newsletter_days=7, 
                 promotional_keywords=None, old_promotional_days=90):
        """
        Initialize rules engine
        
        Args:
            vip_senders: List of VIP email addresses (uses defaults if None)
            event_keywords: List of event-related keywords (uses defaults if None)
            job_keywords: List of job-related keywords (uses defaults if None)
            old_event_days: Days threshold for old events (default: 60)
            old_job_days: Days threshold for old job offers (default: 180)
            newsletter_senders: List of newsletter sender patterns (uses defaults if None)
            old_newsletter_days: Days threshold for old newsletters (default: 7)
            promotional_keywords: List of promotional/sale keywords (uses defaults if None)
            old_promotional_days: Days threshold for old promotional emails (default: 90)
        """
        self.vip_senders = [s.lower() for s in (vip_senders or self.DEFAULT_VIP_SENDERS)]
        self.event_keywords = [k.lower() for k in (event_keywords or self.DEFAULT_EVENT_KEYWORDS)]
        self.job_keywords = [k.lower() for k in (job_keywords or self.DEFAULT_JOB_KEYWORDS)]
        self.old_event_days = old_event_days
        self.old_job_days = old_job_days
        self.newsletter_senders = [s.lower() for s in (newsletter_senders or self.DEFAULT_NEWSLETTER_SENDERS)]
        self.old_newsletter_days = old_newsletter_days
        self.promotional_keywords = [k.lower() for k in (promotional_keywords or self.DEFAULT_PROMOTIONAL_KEYWORDS)]
        self.old_promotional_days = old_promotional_days
        
        self.stats = {
            'vip_kept': 0,
            'event_kept': 0,
            'old_event_deleted': 0,
            'old_job_deleted': 0,
            'old_newsletter_deleted': 0,
            'old_promotional_deleted': 0,
            'personal_kept': 0,
            'auto_deleted': 0,
        }
    
    def check_email(self, email_data: Dict) -> Optional[Dict]:
        """
        Check if email matches any pre-filtering rules.
        
        Args:
            email_data: Email data dictionary with sender, subject, body, date
        
        Returns:
            Dictionary with 'action' (keep/delete), 'reason', 'confidence' if rule matches,
            None if no rule matches (should proceed to AI analysis)
        """
        sender = email_data.get('sender', '').lower()
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body_preview', '').lower()
        received_date = email_data.get('date')
        
        # Rule 1: Old events - delete even from VIP senders if older than threshold
        if received_date and self._is_old_event(subject, body, received_date):
            self.stats['old_event_deleted'] += 1
            return {
                'recommendation': 'delete',
                'confidence_score': 0.93,
                'reasoning': f'Old event notification (older than {self.old_event_days} days) - no longer relevant',
                'category': 'event',
                'priority': 'low',
                'rule_matched': 'old_event'
            }
        
        # Rule 2: VIP senders - always keep
        if self._is_vip_sender(sender):
            self.stats['vip_kept'] += 1
            return {
                'recommendation': 'keep',
                'confidence_score': 0.99,
                'reasoning': f'VIP sender: {sender}',
                'category': 'personal',
                'priority': 'high',
                'rule_matched': 'vip_sender'
            }
        
        # Rule 3: Event-related emails - always keep
        if self._is_event(subject, body):
            self.stats['event_kept'] += 1
            return {
                'recommendation': 'keep',
                'confidence_score': 0.95,
                'reasoning': 'Email appears to be event/calendar related',
                'category': 'event',
                'priority': 'high',
                'rule_matched': 'event'
            }
        
        # Rule 4: Personal contacts detection (heuristic)
        if self._looks_like_personal(sender, subject, body):
            self.stats['personal_kept'] += 1
            return {
                'recommendation': 'keep',
                'confidence_score': 0.90,
                'reasoning': 'Email appears to be from a personal contact',
                'category': 'personal',
                'priority': 'medium',
                'rule_matched': 'personal_contact'
            }
        
        # Rule 5: Old job offers (6+ months old) - auto delete
        if received_date and self._is_old_job_offer(subject, body, received_date):
            self.stats['old_job_deleted'] += 1
            return {
                'recommendation': 'delete',
                'confidence_score': 0.92,
                'reasoning': 'Old job offer (6+ months) - likely no longer relevant',
                'category': 'job',
                'priority': 'low',
                'rule_matched': 'old_job_offer'
            }
        
        # Rule 6: Old newsletters/news (7+ days old by default) - auto delete
        if received_date and self._is_old_newsletter(sender, subject, received_date):
            self.stats['old_newsletter_deleted'] += 1
            return {
                'recommendation': 'delete',
                'confidence_score': 0.93,
                'reasoning': f'Old newsletter/news source (older than {self.old_newsletter_days} days)',
                'category': 'newsletter',
                'priority': 'low',
                'rule_matched': 'old_newsletter'
            }
        
        # Rule 7: Old promotional/sale emails (90+ days old by default) - auto delete
        if received_date and self._is_old_promotional(subject, body, received_date):
            self.stats['old_promotional_deleted'] += 1
            return {
                'recommendation': 'delete',
                'confidence_score': 0.94,
                'reasoning': f'Old promotional/sale email (older than {self.old_promotional_days} days)',
                'category': 'promotional',
                'priority': 'low',
                'rule_matched': 'old_promotional'
            }
        
        # No rule matched - proceed to AI analysis
        return None
    
    def _is_vip_sender(self, sender: str) -> bool:
        """Check if sender is in VIP list"""
        for vip in self.vip_senders:
            if vip in sender:
                return True
        return False
    
    def _is_event(self, subject: str, body: str) -> bool:
        """Check if email is event-related"""
        text = f"{subject} {body}".lower()
        
        for keyword in self.event_keywords:
            if keyword in text:
                return True
        
        return False
    
    def _is_old_event(self, subject: str, body: str, received_date: datetime) -> bool:
        """Check if email is an old event notification"""
        # First check if it's an event
        if not self._is_event(subject, body):
            return False
        
        # Then check age
        # Handle both timezone-aware and naive datetimes
        now = datetime.now(UTC)
        if received_date.tzinfo is None:
            # If received_date is naive, assume UTC
            received_date = received_date.replace(tzinfo=UTC)
        
        age = now - received_date
        return age.days > self.old_event_days
    
    def _looks_like_personal(self, sender: str, subject: str, body: str) -> bool:
        """
        Heuristic to detect personal emails:
        - Short subject line
        - No promotional patterns
        - Sender looks like a person (not company/noreply)
        """
        # Skip automated senders
        automated_patterns = [
            'noreply',
            'no-reply',
            'donotreply',
            'notifications',
            'alerts',
            'info@',
            'support@',
            'news@',
            'marketing@',
        ]
        
        for pattern in automated_patterns:
            if pattern in sender.lower():
                return False
        
        # Check for promotional content
        text = f"{subject} {body}".lower()
        for pattern in self.PROMOTIONAL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        
        # Personal emails often have:
        # - Real names in sender
        # - Short, conversational subject lines
        # - No HTML templates
        if '@gmail.com' in sender or '@yahoo.com' in sender or '@hotmail.com' in sender:
            # Free email providers suggest personal
            if len(subject.split()) <= 6 and 'unsubscribe' not in text:
                return True
        
        return False
    
    def _is_old_job_offer(self, subject: str, body: str, received_date: datetime) -> bool:
        """Check if email is an old job offer"""
        # Check if email is old enough
        # Handle both timezone-aware and naive datetimes
        now = datetime.now(UTC)
        if received_date.tzinfo is None:
            # If received_date is naive, assume UTC
            received_date = received_date.replace(tzinfo=UTC)
        
        age = now - received_date
        if age.days < self.old_job_days:
            return False
        
        # Check for job-related keywords
        text = f"{subject} {body}".lower()
        
        for keyword in self.job_keywords:
            if keyword in text:
                logger.info(f"Detected old job offer (age: {age.days} days, threshold: {self.old_job_days})")
                return True
        
        return False
    
    def _is_old_newsletter(self, sender: str, subject: str, received_date: datetime) -> bool:
        """Check if email is from a known newsletter/news source and is old"""
        # Handle both timezone-aware and naive datetimes
        now = datetime.now(UTC)
        if received_date.tzinfo is None:
            received_date = received_date.replace(tzinfo=UTC)
        
        age = now - received_date
        if age.days < self.old_newsletter_days:
            return False
        
        # Check if sender matches any newsletter patterns
        sender_lower = sender.lower()
        for pattern in self.newsletter_senders:
            if pattern in sender_lower:
                logger.info(f"Detected old newsletter from {sender} (age: {age.days} days, threshold: {self.old_newsletter_days})")
                return True
        
        return False
    
    def _is_old_promotional(self, subject: str, body: str, received_date: datetime) -> bool:
        """Check if email is a promotional/sale email and is old"""
        # Handle both timezone-aware and naive datetimes
        now = datetime.now(UTC)
        if received_date.tzinfo is None:
            received_date = received_date.replace(tzinfo=UTC)
        
        age = now - received_date
        if age.days < self.old_promotional_days:
            return False
        
        # Check for promotional keywords
        text = f"{subject} {body}".lower()
        
        for keyword in self.promotional_keywords:
            if keyword in text:
                logger.info(f"Detected old promotional email (age: {age.days} days, threshold: {self.old_promotional_days})")
                return True
        
        return False
    
    def get_stats(self) -> Dict:
        """Get statistics on rule matches"""
        return self.stats.copy()
    
    def add_vip_sender(self, email: str):
        """Add a new VIP sender"""
        email_lower = email.lower()
        if email_lower not in self.vip_senders:
            self.vip_senders.append(email_lower)
            logger.info(f"Added VIP sender: {email}")
    
    def remove_vip_sender(self, email: str):
        """Remove a VIP sender"""
        email_lower = email.lower()
        if email_lower in self.vip_senders:
            self.vip_senders.remove(email_lower)
            logger.info(f"Removed VIP sender: {email}")
