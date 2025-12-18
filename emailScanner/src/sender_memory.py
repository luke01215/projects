"""
Sender memory and pattern tracking for learning from past decisions.
Tracks historical decisions per sender to enable pattern-based classification.
"""
from typing import Dict, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Email, Decision, Analysis
import logging

logger = logging.getLogger(__name__)


class SenderMemory:
    """Track and analyze sender-specific decision patterns"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def get_sender_stats(self, sender: str) -> Dict:
        """
        Get decision statistics for a specific sender
        
        Returns:
            Dict with total_decisions, kept_count, deleted_count, keep_rate, 
            avg_confidence, most_common_action
        """
        # Query all decisions for this sender
        decisions = self.db_session.query(Email, Decision, Analysis).join(
            Decision, Email.id == Decision.email_id
        ).join(
            Analysis, Email.id == Analysis.email_id
        ).filter(
            Email.sender == sender
        ).all()
        
        if not decisions:
            return {
                'total_decisions': 0,
                'kept_count': 0,
                'deleted_count': 0,
                'archived_count': 0,
                'keep_rate': 0.0,
                'delete_rate': 0.0,
                'avg_confidence': 0.0,
                'most_common_action': None,
                'has_pattern': False
            }
        
        total = len(decisions)
        kept = sum(1 for _, d, _ in decisions if d.action_taken == 'kept')
        deleted = sum(1 for _, d, _ in decisions if d.action_taken == 'deleted')
        archived = sum(1 for _, d, _ in decisions if d.action_taken == 'archived')
        
        confidences = [a.confidence_score for _, _, a in decisions if a.confidence_score]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        keep_rate = kept / total if total > 0 else 0.0
        delete_rate = deleted / total if total > 0 else 0.0
        
        # Determine most common action
        action_counts = {'kept': kept, 'deleted': deleted, 'archived': archived}
        most_common = max(action_counts, key=action_counts.get)
        
        # Has pattern if 90%+ consistent and 3+ decisions
        has_pattern = total >= 3 and (keep_rate >= 0.9 or delete_rate >= 0.9)
        
        return {
            'total_decisions': total,
            'kept_count': kept,
            'deleted_count': deleted,
            'archived_count': archived,
            'keep_rate': keep_rate,
            'delete_rate': delete_rate,
            'avg_confidence': avg_confidence,
            'most_common_action': most_common if action_counts[most_common] > 0 else None,
            'has_pattern': has_pattern
        }
    
    def get_domain_stats(self, email_address: str) -> Dict:
        """
        Get decision statistics for all senders from the same domain
        
        Args:
            email_address: Full email address (will extract domain)
        """
        if '@' not in email_address:
            return self.get_sender_stats(email_address)
        
        domain = email_address.split('@')[1]
        
        # Query all decisions for senders from this domain
        decisions = self.db_session.query(Email, Decision, Analysis).join(
            Decision, Email.id == Decision.email_id
        ).join(
            Analysis, Email.id == Analysis.email_id
        ).filter(
            Email.sender.like(f'%@{domain}%')
        ).all()
        
        if not decisions:
            return self.get_sender_stats(email_address)
        
        total = len(decisions)
        kept = sum(1 for _, d, _ in decisions if d.action_taken == 'kept')
        deleted = sum(1 for _, d, _ in decisions if d.action_taken == 'deleted')
        
        return {
            'domain': domain,
            'total_decisions': total,
            'kept_count': kept,
            'deleted_count': deleted,
            'keep_rate': kept / total if total > 0 else 0.0,
            'delete_rate': deleted / total if total > 0 else 0.0
        }
    
    def get_similar_decisions(self, sender: str, category: str, limit: int = 5) -> List[Dict]:
        """
        Get past decisions for similar emails (same sender or category)
        Used for few-shot learning
        
        Returns:
            List of dicts with email details, AI recommendation, and human decision
        """
        # First try same sender
        decisions = self.db_session.query(Email, Decision, Analysis).join(
            Decision, Email.id == Decision.email_id
        ).join(
            Analysis, Email.id == Analysis.email_id
        ).filter(
            Email.sender == sender
        ).order_by(Decision.decided_at.desc()).limit(limit).all()
        
        # If not enough from sender, add same category
        if len(decisions) < limit:
            category_decisions = self.db_session.query(Email, Decision, Analysis).join(
                Decision, Email.id == Decision.email_id
            ).join(
                Analysis, Email.id == Analysis.email_id
            ).filter(
                Analysis.category == category,
                Email.sender != sender  # Different sender
            ).order_by(Decision.decided_at.desc()).limit(limit - len(decisions)).all()
            
            decisions.extend(category_decisions)
        
        results = []
        for email, decision, analysis in decisions:
            results.append({
                'sender': email.sender,
                'subject': email.subject,
                'category': analysis.category,
                'ai_recommendation': analysis.recommendation,
                'ai_confidence': analysis.confidence_score,
                'human_decision': decision.action_taken,
                'approved': decision.approved
            })
        
        return results
    
    def should_skip_llm(self, sender: str) -> Optional[Dict]:
        """
        Check if we can skip LLM analysis based on sender history
        
        Returns:
            Dict with recommendation and reason, or None if LLM needed
        """
        stats = self.get_sender_stats(sender)
        
        # Need strong pattern to skip LLM
        if not stats['has_pattern']:
            return None
        
        if stats['keep_rate'] >= 0.9:
            logger.info(f"Skipping LLM for {sender}: {stats['keep_rate']:.0%} keep rate over {stats['total_decisions']} decisions")
            return {
                'recommendation': 'keep',
                'confidence_score': stats['keep_rate'],
                'reasoning': f"Pattern detected: You've kept {stats['kept_count']}/{stats['total_decisions']} emails from this sender",
                'category': 'pattern_learned',
                'priority': 'medium',
                'skip_reason': 'sender_history'
            }
        
        if stats['delete_rate'] >= 0.9:
            logger.info(f"Skipping LLM for {sender}: {stats['delete_rate']:.0%} delete rate over {stats['total_decisions']} decisions")
            return {
                'recommendation': 'delete',
                'confidence_score': stats['delete_rate'],
                'reasoning': f"Pattern detected: You've deleted {stats['deleted_count']}/{stats['total_decisions']} emails from this sender",
                'category': 'pattern_learned',
                'priority': 'low',
                'skip_reason': 'sender_history'
            }
        
        return None
