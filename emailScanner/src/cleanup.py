"""
Cleanup script for batch deleting approved emails.
Run this after reviewing emails to actually delete them from the server.
"""
import logging
import argparse
from datetime import datetime, UTC
from typing import List
from sqlalchemy.orm import Session

from models import Email, Analysis, Decision, SystemStats, init_db, get_session
from email_client import EmailClient
from settings import load_settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmailCleanup:
    """Handle batch deletion of approved emails"""
    
    def __init__(self, config):
        """Initialize cleanup handler"""
        self.config = config
        self.email_client = None
        self.db_session = None
        
    def initialize(self) -> bool:
        """Initialize email client and database"""
        try:
            # Initialize database
            engine = init_db(self.config.database_url)
            self.db_session = get_session(engine)
            
            # Initialize email client
            self.email_client = EmailClient(
                server=self.config.email_server,
                email_address=self.config.email_address,
                password=self.config.email_password,
                port=self.config.email_port
            )
            
            if not self.email_client.connect():
                logger.error("Cannot connect to email server")
                return False
            
            logger.info("Cleanup initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False
    
    def get_approved_deletions(self) -> List[tuple]:
        """
        Get all emails that have been approved for deletion
        
        Returns:
            List of (email_id, email.id, subject) tuples
        """
        # Get emails where user approved the AI recommendation to delete
        query = self.db_session.query(Email, Decision, Analysis).join(
            Decision, Email.id == Decision.email_id
        ).join(
            Analysis, Email.id == Analysis.email_id
        ).filter(
            Decision.approved == True,  # User approved the recommendation
            Analysis.recommendation == 'delete',  # AI recommended deletion
            Email.deleted_at.is_(None)  # Not already deleted
        )
        
        results = [(e.email_id, e.id, e.subject) for e, d, a in query.all()]
        return results
    
    def delete_approved_emails(self, dry_run: bool = False) -> int:
        """
        Delete all approved emails from server and mark in database
        
        Args:
            dry_run: If True, only show what would be deleted without actually deleting
        
        Returns:
            Number of emails deleted
        """
        try:
            approved = self.get_approved_deletions()
            
            if not approved:
                logger.info("No approved emails to delete")
                return 0
            
            logger.info(f"Found {len(approved)} emails approved for deletion")
            
            if dry_run:
                logger.info("DRY RUN - Would delete:")
                for email_id, db_id, subject in approved:
                    logger.info(f"  - {email_id}: {subject}")
                return len(approved)
            
            # Select INBOX folder before deleting
            if not self.email_client.select_folder('INBOX'):
                logger.error("Failed to select INBOX folder")
                return 0
            
            # email_id stored in database is the IMAP UID (unique and persistent)
            
            # Delete each email
            deleted_count = 0
            failed_count = 0
            
            for email_id, db_id, subject in approved:
                try:
                    logger.info(f"Deleting: {subject[:50]}...")
                    
                    # Delete from server
                    if self.email_client.delete_email(email_id):
                        # Mark as deleted in database
                        email = self.db_session.query(Email).get(db_id)
                        email.deleted_at = datetime.now(UTC)
                        self.db_session.commit()
                        
                        deleted_count += 1
                        logger.info(f"  ✓ Deleted successfully")
                    else:
                        failed_count += 1
                        logger.warning(f"  ✗ Failed to delete from server")
                
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Error deleting email {email_id}: {e}")
                    self.db_session.rollback()
            
            # Update system stats
            self._update_stats(deleted_count)
            
            logger.info(f"Cleanup complete: {deleted_count} deleted, {failed_count} failed")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return 0
    
    def auto_delete_high_confidence(self, min_confidence: float = 0.95, dry_run: bool = False) -> int:
        """
        Automatically delete emails with high-confidence AI recommendations (no manual review)
        
        Args:
            min_confidence: Minimum confidence score (0.0-1.0) to auto-delete
            dry_run: If True, only show what would be deleted
        
        Returns:
            Number of emails deleted
        """
        try:
            # Find high-confidence delete recommendations with no decision yet
            query = self.db_session.query(Email, Analysis).join(
                Analysis, Email.id == Analysis.email_id
            ).outerjoin(
                Decision, Email.id == Decision.email_id
            ).filter(
                Analysis.recommendation == 'delete',
                Analysis.confidence_score >= min_confidence,
                Decision.id.is_(None),  # No decision made yet
                Email.deleted_at.is_(None)  # Not already deleted
            )
            
            results = [(e.email_id, e.id, e.subject, a.confidence_score, a.reasoning) 
                      for e, a in query.all()]
            
            if not results:
                logger.info("No high-confidence emails to auto-delete")
                return 0
            
            logger.info(f"Found {len(results)} high-confidence emails for auto-deletion")
            
            if dry_run:
                logger.info(f"DRY RUN - Would auto-delete (confidence >= {min_confidence}):")
                for email_id, db_id, subject, confidence, reasoning in results:
                    logger.info(f"  - [{confidence:.2f}] {subject[:50]} - {reasoning}")
                return len(results)
            
            # Select INBOX folder before deleting
            if not self.email_client.select_folder('INBOX'):
                logger.error("Failed to select INBOX folder")
                return 0
            
            # email_id stored in database is the IMAP UID (unique and persistent)
            
            # Delete each email
            deleted_count = 0
            
            for email_id, db_id, subject, confidence, reasoning in results:
                try:
                    logger.info(f"Auto-deleting [{confidence:.2f}]: {subject[:50]}...")
                    
                    # Delete from server
                    if self.email_client.delete_email(email_id):
                        # Mark as deleted in database
                        email = self.db_session.query(Email).get(db_id)
                        email.deleted_at = datetime.now(UTC)
                        
                        # Create decision record (auto-approved)
                        decision = Decision(
                            email_id=db_id,
                            action='approve',
                            approved_recommendation='delete',
                            notes=f'Auto-deleted (confidence: {confidence:.2f})',
                            decided_at=datetime.now(UTC)
                        )
                        self.db_session.add(decision)
                        self.db_session.commit()
                        
                        deleted_count += 1
                        logger.info(f"  ✓ Auto-deleted successfully")
                    else:
                        logger.warning(f"  ✗ Failed to delete from server")
                
                except Exception as e:
                    logger.error(f"Error auto-deleting email {email_id}: {e}")
                    self.db_session.rollback()
            
            # Update system stats
            self._update_stats(deleted_count)
            
            logger.info(f"Auto-delete complete: {deleted_count} emails deleted")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error during auto-delete: {e}")
            return 0
    
    def _update_stats(self, deleted_count: int):
        """Update system statistics"""
        try:
            stats = self.db_session.query(SystemStats).first()
            if stats:
                stats.total_emails_deleted += deleted_count
                stats.updated_at = datetime.now(UTC)
                self.db_session.commit()
        except Exception as e:
            logger.error(f"Failed to update stats: {e}")
    
    def cleanup(self):
        """Clean up resources"""
        if self.email_client:
            self.email_client.disconnect()
        if self.db_session:
            self.db_session.close()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Clean up approved emails')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be deleted without actually deleting')
    parser.add_argument('--auto-delete', action='store_true',
                       help='Auto-delete high-confidence recommendations without manual review')
    parser.add_argument('--min-confidence', type=float, default=0.95,
                       help='Minimum confidence score for auto-delete (default: 0.95)')
    
    args = parser.parse_args()
    
    # Load settings
    config = load_settings()
    
    # Initialize cleanup
    cleanup = EmailCleanup(config)
    
    if not cleanup.initialize():
        logger.error("Failed to initialize cleanup")
        return 1
    
    try:
        if args.auto_delete:
            # Auto-delete high-confidence emails
            deleted = cleanup.auto_delete_high_confidence(
                min_confidence=args.min_confidence,
                dry_run=args.dry_run
            )
        else:
            # Delete manually approved emails
            deleted = cleanup.delete_approved_emails(dry_run=args.dry_run)
        
        if args.dry_run:
            logger.info(f"DRY RUN: Would have deleted {deleted} emails")
        else:
            logger.info(f"Successfully deleted {deleted} emails")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("\nCleanup interrupted by user")
        return 130
    finally:
        cleanup.cleanup()


if __name__ == '__main__':
    exit(main())
