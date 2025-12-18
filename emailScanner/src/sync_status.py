"""
Sync script to reconcile database state with actual Gmail state.
Checks if emails in the database still exist on the server and updates accordingly.
"""
import logging
import argparse
from datetime import datetime, UTC
from typing import List, Set
from sqlalchemy.orm import Session
from sqlalchemy import func

from models import Email, Analysis, Decision, init_db, get_session
from email_client import EmailClient
from settings import load_settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmailSync:
    """Synchronize database state with Gmail server state"""
    
    def __init__(self, config):
        """Initialize sync handler"""
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
            logger.info(f"Connecting to {self.config.email_server} as {self.config.email_address}")
            self.email_client = EmailClient(
                server=self.config.email_server,
                email_address=self.config.email_address,
                password=self.config.email_password,
                port=self.config.email_port
            )
            
            if not self.email_client.connect():
                logger.error("Cannot connect to email server")
                logger.error("If you see 'Not enough arguments' error, try:")
                logger.error("  1. Regenerating your Gmail app password")
                logger.error("  2. Checking for spaces in password in config.yaml")
                logger.error("  3. Ensuring scanner.py works with same credentials")
                return False
            
            if not self.email_client.select_folder(self.config.scan_folder):
                logger.error(f"Cannot select folder: {self.config.scan_folder}")
                return False
            
            logger.info("Sync initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False
    
    def get_server_uids(self) -> Set[str]:
        """
        Get all UIDs currently on the server
        
        Returns:
            Set of email UIDs as strings
        """
        try:
            # Search for all emails
            status, messages = self.email_client.connection.uid('search', None, 'ALL')
            
            if status != 'OK':
                logger.error("Failed to search emails on server")
                return set()
            
            # Parse UIDs
            uids = messages[0].split()
            uid_set = {uid.decode('utf-8') if isinstance(uid, bytes) else str(uid) for uid in uids}
            
            logger.info(f"Found {len(uid_set)} emails on server")
            return uid_set
            
        except Exception as e:
            logger.error(f"Error getting server UIDs: {e}")
            return set()
    
    def sync_deleted_emails(self, mark_only: bool = False, remove_from_db: bool = False) -> dict:
        """
        Check which emails in database no longer exist on server (and vice versa)
        
        Args:
            mark_only: If True, only mark as deleted without removing from database
            remove_from_db: If True, remove emails from database (use with caution!)
        
        Returns:
            Dictionary with sync statistics
        """
        try:
            # Get all UIDs from server
            server_uids = self.get_server_uids()
            
            if not server_uids:
                logger.warning("No emails found on server or error occurred")
                return {'error': 'Could not retrieve server emails'}
            
            stats = {
                'checked_active': 0,
                'checked_deleted': 0,
                'missing_on_server': 0,
                'marked_deleted': 0,
                'removed_from_db': 0,
                'restored_to_inbox': 0,
                'errors': 0
            }
            
            # DIRECTION 1: Check active emails in DB - mark as deleted if missing from Gmail
            db_active_emails = self.db_session.query(Email).filter(
                Email.deleted_at.is_(None)
            ).all()
            
            logger.info(f"Checking {len(db_active_emails)} active emails in database against server")
            stats['checked_active'] = len(db_active_emails)
            
            for email in db_active_emails:
                try:
                    # Check if email UID exists on server
                    if email.email_id not in server_uids:
                        stats['missing_on_server'] += 1
                        logger.info(f"Email missing on server: {email.email_id} - {email.subject[:50]}")
                        
                        if remove_from_db:
                            # Remove completely from database
                            self.db_session.query(Decision).filter(
                                Decision.email_id == email.id
                            ).delete()
                            self.db_session.query(Analysis).filter(
                                Analysis.email_id == email.id
                            ).delete()
                            self.db_session.delete(email)
                            stats['removed_from_db'] += 1
                            logger.info(f"  ✓ Removed from database")
                            
                        elif mark_only:
                            # Mark as deleted in database
                            email.deleted_at = datetime.now(UTC)
                            stats['marked_deleted'] += 1
                            logger.info(f"  ✓ Marked as deleted")
                
                except Exception as e:
                    stats['errors'] += 1
                    logger.error(f"Error processing active email {email.email_id}: {e}")
            
            # DIRECTION 2: Check deleted emails in DB - restore if they came back to Gmail
            db_deleted_emails = self.db_session.query(Email).filter(
                Email.deleted_at.isnot(None)
            ).all()
            
            logger.info(f"Checking {len(db_deleted_emails)} deleted emails in database for restoration")
            stats['checked_deleted'] = len(db_deleted_emails)
            
            for email in db_deleted_emails:
                try:
                    # Check if email UID is back on server
                    if email.email_id in server_uids:
                        stats['restored_to_inbox'] += 1
                        logger.info(f"Email restored to inbox: {email.email_id} - {email.subject[:50]}")
                        
                        # Unmark as deleted
                        email.deleted_at = None
                        
                        # Reset analysis status to pending_review so it shows in web UI
                        analysis = self.db_session.query(Analysis).filter(
                            Analysis.email_id == email.id
                        ).first()
                        if analysis:
                            analysis.status = 'pending_review'
                        
                        logger.info(f"  ✓ Restored to pending review")
                
                except Exception as e:
                    stats['errors'] += 1
                    logger.error(f"Error processing deleted email {email.email_id}: {e}")
            
            # Commit all changes
            self.db_session.commit()
            
            logger.info("=" * 60)
            logger.info("Sync Summary:")
            logger.info(f"  Active emails checked: {stats['checked_active']}")
            logger.info(f"  Missing on server: {stats['missing_on_server']}")
            if mark_only:
                logger.info(f"    → Marked as deleted: {stats['marked_deleted']}")
            if remove_from_db:
                logger.info(f"    → Removed from database: {stats['removed_from_db']}")
            logger.info(f"  Deleted emails checked: {stats['checked_deleted']}")
            logger.info(f"  Restored to inbox: {stats['restored_to_inbox']}")
            logger.info(f"  Errors: {stats['errors']}")
            logger.info("=" * 60)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error during sync: {e}")
            self.db_session.rollback()
            return {'error': str(e)}
    
    def cleanup_old_deleted_emails(self, days_old: int = 30) -> int:
        """
        Remove emails from database that were marked as deleted more than X days ago
        
        Args:
            days_old: Remove emails deleted more than this many days ago
        
        Returns:
            Number of emails removed
        """
        try:
            from datetime import timedelta
            
            cutoff_date = datetime.now(UTC) - timedelta(days=days_old)
            
            # Find old deleted emails
            old_deleted = self.db_session.query(Email).filter(
                Email.deleted_at.isnot(None),
                Email.deleted_at < cutoff_date
            ).all()
            
            if not old_deleted:
                logger.info(f"No deleted emails older than {days_old} days found")
                return 0
            
            logger.info(f"Found {len(old_deleted)} deleted emails older than {days_old} days")
            
            removed_count = 0
            for email in old_deleted:
                try:
                    # Remove related records
                    self.db_session.query(Decision).filter(
                        Decision.email_id == email.id
                    ).delete()
                    self.db_session.query(Analysis).filter(
                        Analysis.email_id == email.id
                    ).delete()
                    self.db_session.delete(email)
                    removed_count += 1
                    
                except Exception as e:
                    logger.error(f"Error removing email {email.email_id}: {e}")
            
            self.db_session.commit()
            logger.info(f"Removed {removed_count} old deleted emails from database")
            
            return removed_count
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            self.db_session.rollback()
            return 0
    
    def show_stats(self):
        """Show database statistics"""
        try:
            total = self.db_session.query(func.count(Email.id)).scalar()
            deleted = self.db_session.query(func.count(Email.id)).filter(
                Email.deleted_at.isnot(None)
            ).scalar()
            active = total - deleted
            
            pending = self.db_session.query(func.count(Analysis.id)).filter(
                Analysis.status == 'pending_review'
            ).scalar()
            
            logger.info("=" * 60)
            logger.info("Database Statistics:")
            logger.info(f"  Total emails: {total}")
            logger.info(f"  Active emails: {active}")
            logger.info(f"  Deleted emails: {deleted}")
            logger.info(f"  Pending review: {pending}")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Error showing stats: {e}")
    
    def close(self):
        """Close connections"""
        if self.email_client and hasattr(self.email_client, 'connection') and self.email_client.connection:
            self.email_client.disconnect()
        if self.db_session:
            self.db_session.close()


def main():
    parser = argparse.ArgumentParser(
        description='Synchronize email database with Gmail server state'
    )
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to configuration file (default: auto-detect config/config.yaml)'
    )
    parser.add_argument(
        '--sync',
        action='store_true',
        help='Sync database with Gmail (bidirectional: mark missing emails as deleted, restore emails that came back)'
    )
    parser.add_argument(
        '--mark-deleted',
        action='store_true',
        help='(Deprecated: use --sync) Mark emails missing from server as deleted in database'
    )
    parser.add_argument(
        '--remove',
        action='store_true',
        help='Remove emails missing from server from database (DESTRUCTIVE!)'
    )
    parser.add_argument(
        '--cleanup-old',
        type=int,
        metavar='DAYS',
        help='Remove emails marked as deleted more than DAYS days ago'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show database statistics only'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    if args.config:
        logger.info(f"Loading configuration from {args.config}")
    else:
        logger.info("Auto-detecting configuration file")
    config = load_settings(args.config)
    
    # Debug: Check if email address loaded
    logger.info(f"Config loaded - Email: {config.email_address}, Server: {config.email_server}")
    if not config.email_address:
        logger.error("Email address is empty in configuration!")
        logger.error("Check config/config.yaml has: email: address: 'your@email.com'")
        return 1
    
    # Initialize sync
    sync = EmailSync(config)
    
    try:
        if args.stats:
            # Just show stats
            if not sync.initialize():
                return 1
            sync.show_stats()
            return 0
        
        if not sync.initialize():
            logger.error("Failed to initialize sync")
            return 1
        
        # Show current stats
        sync.show_stats()
        
        # Perform sync
        if args.sync or args.mark_deleted:
            if args.mark_deleted:
                logger.warning("--mark-deleted is deprecated, use --sync instead")
            
            logger.info("\nStarting bidirectional sync...")
            
            if args.remove:
                logger.warning("⚠️  REMOVE MODE - emails will be permanently removed from database!")
                response = input("Are you sure? Type 'yes' to confirm: ")
                if response.lower() != 'yes':
                    logger.info("Sync cancelled")
                    return 0
            
            stats = sync.sync_deleted_emails(
                mark_only=True,
                remove_from_db=args.remove
            )
            
            if 'error' in stats:
                logger.error(f"Sync failed: {stats['error']}")
                return 1
        
        # Cleanup old deleted emails if requested
        if args.cleanup_old:
            logger.info(f"\nCleaning up emails deleted more than {args.cleanup_old} days ago...")
            removed = sync.cleanup_old_deleted_emails(args.cleanup_old)
            logger.info(f"Cleanup complete: {removed} emails removed")
        
        # Show final stats
        logger.info("\nFinal state:")
        sync.show_stats()
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("\nSync interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Sync failed: {e}", exc_info=True)
        return 1
    finally:
        sync.close()


if __name__ == '__main__':
    exit(main())
