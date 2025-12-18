"""
Email scanner orchestration - coordinates email fetching, analysis, and storage.
Main entry point for scanning new emails.
"""
import logging
import argparse
from datetime import datetime, timedelta, UTC
from typing import Optional, List
from sqlalchemy.orm import Session

from models import Email, Analysis, SystemStats, init_db, get_session
from email_client import EmailClient
from ollama_analyzer import OllamaAnalyzer
from settings import load_settings
from rules import EmailRules
from sender_memory import SenderMemory
from confidence_calibration import ConfidenceCalibrator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmailScanner:
    """Main scanner class that coordinates the email analysis pipeline"""
    
    def __init__(self, config: Settings):
        """
        Initialize email scanner
        
        Args:
            config: Application settings
        """
        self.config = config
        self.email_client = None
        self.analyzer = None
        self.db_session = None
        # Initialize rules engine with config
        self.rules = EmailRules(
            vip_senders=config.vip_senders,
            event_keywords=config.event_keywords,
            job_keywords=config.job_keywords,
            old_event_days=config.old_event_days,
            old_job_days=config.old_job_days,
            newsletter_senders=config.newsletter_senders,
            old_newsletter_days=config.old_newsletter_days,
            promotional_keywords=config.promotional_keywords,
            old_promotional_days=config.old_promotional_days
        )
        
    def initialize(self) -> bool:
        """Initialize all components"""
        try:
            # Initialize database
            logger.info("Initializing database...")
            engine = init_db(self.config.database_url)
            self.db_session = get_session(engine)
            
            # Initialize Ollama analyzer with database session for few-shot learning
            logger.info("Initializing Ollama analyzer...")
            self.analyzer = OllamaAnalyzer(
                base_url=self.config.ollama_base_url,
                model=self.config.ollama_model,
                db_session=self.db_session
            )
            
            if not self.analyzer.check_connection():
                logger.error("Cannot connect to Ollama. Make sure it's running.")
                return False
            
            # Initialize email client
            logger.info("Initializing email client...")
            self.email_client = EmailClient(
                server=self.config.email_server,
                email_address=self.config.email_address,
                password=self.config.email_password,
                port=self.config.email_port
            )
            
            if not self.email_client.connect():
                logger.error("Cannot connect to email server")
                return False
            
            logger.info("All components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False
    
    def scan_new_emails(self, folder: str = 'INBOX', limit: Optional[int] = None, 
                        since_date: Optional[datetime] = None, before_date: Optional[datetime] = None,
                        newest_first: bool = False, rescan: bool = False) -> int:
        """
        Scan and analyze new emails
        
        Args:
            folder: Email folder to scan
            limit: Maximum number of emails to process
            since_date: Only fetch emails since this date
            before_date: Only fetch emails before this date
            newest_first: If True, process newest emails first; if False, process oldest first
            rescan: If True, re-analyze emails that have already been processed
        
        Returns:
            Number of emails processed
        """
        try:
            logger.info(f"Starting email scan in folder: {folder}")
            
            # Select folder
            if not self.email_client.select_folder(folder):
                logger.error(f"Failed to select folder: {folder}")
                return 0
            
            # Search for emails to process
            search_criteria = self._build_search_criteria(since_date, before_date)
            email_ids = self.email_client.search_emails(search_criteria, limit=limit, newest_first=newest_first)
            
            if not email_ids:
                logger.info("No new emails to process")
                return 0
            
            logger.info(f"Found {len(email_ids)} emails to process")
            
            # Filter email IDs before fetching (unless rescanning)
            if rescan:
                logger.info("Rescan mode: will fetch and re-analyze all emails")
                email_ids_to_fetch = email_ids
            else:
                # Check which email IDs are already in database
                new_email_ids = []
                skipped_count = 0
                
                for email_id in email_ids:
                    existing = self.db_session.query(Email).filter_by(email_id=email_id).first()
                    if not existing:
                        new_email_ids.append(email_id)
                    else:
                        skipped_count += 1
                
                if skipped_count > 0:
                    logger.info(f"Skipped {skipped_count} already-processed emails")
                
                email_ids_to_fetch = new_email_ids
            
            if not email_ids_to_fetch:
                logger.info("No new emails to fetch and process")
                return 0
            
            logger.info(f"Fetching {len(email_ids_to_fetch)} emails from IMAP")
            
            # Fetch only new emails
            emails = self.email_client.fetch_emails_batch(email_ids_to_fetch)
            
            total_emails = len(emails)
            logger.info(f"Processing {total_emails} emails")
            
            # Process each email with progress updates
            processed_count = 0
            for idx, email_data in enumerate(emails, 1):
                sender = email_data.get('sender', 'Unknown')
                subject = email_data.get('subject', 'No Subject')
                
                # Show progress
                logger.info(f"[{idx}/{total_emails}] Processing: {sender[:40]} - {subject[:60]}")
                
                if self._process_email(email_data, folder):
                    processed_count += 1
                    logger.info(f"  ✓ Success ({processed_count} processed so far)")
                else:
                    logger.warning(f"  ✗ Failed to process")
            
            # Update system stats
            self._update_stats(processed_count)
            
            logger.info(f"Scan complete. Processed {processed_count}/{total_emails} emails")
            return processed_count
            
        except Exception as e:
            logger.error(f"Error during email scan: {e}")
            return 0
    
    def _build_search_criteria(self, since_date: Optional[datetime] = None, 
                               before_date: Optional[datetime] = None) -> str:
        """Build IMAP search criteria based on date filters"""
        criteria = []
        
        if since_date:
            # IMAP date format: DD-Mon-YYYY (e.g., 01-Jan-2024)
            date_str = since_date.strftime('%d-%b-%Y')
            criteria.append(f'SINCE {date_str}')
            logger.info(f"Filtering emails since: {date_str}")
        
        if before_date:
            date_str = before_date.strftime('%d-%b-%Y')
            criteria.append(f'BEFORE {date_str}')
            logger.info(f"Filtering emails before: {date_str}")
        
        if criteria:
            return ' '.join(criteria)
        
        return 'ALL'
    
    def _filter_new_emails(self, emails: List[dict], rescan: bool = False) -> List[dict]:
        """Filter out emails that have already been processed (unless rescanning)"""
        if rescan:
            logger.info("Rescan mode: will re-analyze all emails")
            return emails
        
        new_emails = []
        skipped_count = 0
        
        for email_data in emails:
            email_id = email_data.get('email_id')
            
            # Check if email already exists in database
            existing = self.db_session.query(Email).filter_by(email_id=email_id).first()
            
            if not existing:
                new_emails.append(email_data)
            else:
                skipped_count += 1
                logger.debug(f"Skipping already processed email: {email_id}")
        
        if skipped_count > 0:
            logger.info(f"Skipped {skipped_count} already-processed emails")
        
        return new_emails
    
    def _process_email(self, email_data: dict, folder: str) -> bool:
        """
        Process a single email: store, analyze, and save results
        
        Args:
            email_data: Email data dictionary
            folder: Email folder name
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Store email in database (or get existing)
            email_record = self.db_session.query(Email).filter_by(email_id=email_data['email_id']).first()
            
            if not email_record:
                # New email - create record
                email_record = Email(
                    email_id=email_data['email_id'],
                    sender=email_data['sender'],
                    recipient=email_data['recipient'],
                    subject=email_data['subject'],
                    body_preview=email_data['body_preview'],
                    body_full=email_data['body_full'],
                    received_date=email_data['date'],
                    size_bytes=email_data['size_bytes'],
                    has_attachments=email_data['has_attachments'],
                    folder=folder,
                    fetched_at=datetime.now(UTC)
                )
                self.db_session.add(email_record)
                self.db_session.flush()  # Get the ID
            
            # Check rules first before AI analysis
            rule_result = self.rules.check_email(email_data)
            
            if rule_result:
                # TIER 1: Rule matched - use rule decision instead of AI
                logger.info(f"✓ Rule matched: {rule_result['rule_matched']} - {rule_result['recommendation']}")
                analysis_result = rule_result
                analysis_result['model_name'] = 'rules_engine'
                analysis_result['model_version'] = '1.0'
            else:
                # TIER 2: Check sender history patterns
                sender_memory = SenderMemory(self.db_session)
                pattern_result = sender_memory.should_skip_llm(email_data['sender'])
                
                if pattern_result:
                    # Pattern detected - skip LLM
                    logger.info(f"✓ Pattern detected for {email_data['sender']}: {pattern_result['recommendation']}")
                    analysis_result = pattern_result
                    analysis_result['model_name'] = 'pattern_memory'
                    analysis_result['model_version'] = '1.0'
                else:
                    # TIER 3: No rule or pattern - analyze with LLM
                    logger.info(f"→ Analyzing with LLM: {email_data['sender']}")
                    analysis_result = self.analyzer.analyze_email(email_data)
                    
                    if not analysis_result:
                        logger.warning(f"Failed to analyze email {email_data['email_id']}")
                        self.db_session.rollback()
                        return False
                    
                    # Apply confidence calibration for LLM results
                    calibrator = ConfidenceCalibrator(self.db_session)
                    original_confidence = analysis_result['confidence_score']
                    calibrated_confidence, calibration_reason = calibrator.calibrate_confidence(
                        original_confidence,
                        analysis_result.get('category')
                    )
                    
                    if abs(calibrated_confidence - original_confidence) > 0.05:
                        logger.info(f"  Confidence calibrated: {original_confidence:.1%} → {calibrated_confidence:.1%}")
                        logger.info(f"  Reason: {calibration_reason}")
                        analysis_result['confidence_score'] = calibrated_confidence
                        analysis_result['reasoning'] += f" (Confidence calibrated: {calibration_reason})"
            
            # Store or update analysis
            analysis_record = self.db_session.query(Analysis).filter_by(email_id=email_record.id).first()
            
            if analysis_record:
                # Update existing analysis (rescan mode)
                analysis_record.recommendation = analysis_result['recommendation']
                analysis_record.confidence_score = analysis_result['confidence_score']
                analysis_record.reasoning = analysis_result['reasoning']
                analysis_record.category = analysis_result['category']
                analysis_record.priority = analysis_result['priority']
                analysis_record.model_name = analysis_result['model_name']
                analysis_record.model_version = analysis_result['model_version']
                analysis_record.status = 'pending_review'
                analysis_record.analyzed_at = datetime.now(UTC)
                logger.info("Updated existing analysis")
            else:
                # Create new analysis
                analysis_record = Analysis(
                    email_id=email_record.id,
                    recommendation=analysis_result['recommendation'],
                    confidence_score=analysis_result['confidence_score'],
                    reasoning=analysis_result['reasoning'],
                    category=analysis_result['category'],
                    priority=analysis_result['priority'],
                    model_name=analysis_result['model_name'],
                    model_version=analysis_result['model_version'],
                    status='pending_review',
                    analyzed_at=datetime.now(UTC)
                )
                self.db_session.add(analysis_record)
            self.db_session.commit()
            
            logger.info(f"Successfully processed email from {email_data['sender']} - {analysis_result['recommendation']}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing email: {e}")
            self.db_session.rollback()
            return False
    
    def _update_stats(self, processed_count: int):
        """Update system statistics"""
        try:
            stats = self.db_session.query(SystemStats).first()
            
            if not stats:
                stats = SystemStats(
                    total_emails_processed=0,
                    total_emails_deleted=0,
                    total_emails_kept=0,
                    ai_accuracy_rate=0.0
                )
                self.db_session.add(stats)
            
            stats.total_emails_processed += processed_count
            stats.last_scan_at = datetime.now(UTC)
            stats.updated_at = datetime.now(UTC)
            
            self.db_session.commit()
            
        except Exception as e:
            logger.error(f"Failed to update stats: {e}")
            self.db_session.rollback()
    
    def cleanup(self):
        """Clean up resources"""
        if self.email_client:
            self.email_client.disconnect()
        
        if self.db_session:
            self.db_session.close()
        
        # Log rules statistics
        rule_stats = self.rules.get_stats()
        if any(rule_stats.values()):
            logger.info(f"Rules engine stats: {rule_stats}")
        
        logger.info("Scanner cleanup complete")


def main():
    """Main entry point for email scanner"""
    try:
        # Parse command-line arguments
        parser = argparse.ArgumentParser(description='Email Scanner - Analyze emails with AI')
        parser.add_argument('--folder', default='INBOX', help='Email folder to scan (default: INBOX)')
        parser.add_argument('--limit', type=int, help='Maximum number of emails to process')
        parser.add_argument('--days', type=int, help='Scan emails from the last N days (e.g., --days 30)')
        parser.add_argument('--since', help='Scan emails since date (format: YYYY-MM-DD)')
        parser.add_argument('--before', help='Scan emails before date (format: YYYY-MM-DD)')
        parser.add_argument('--newest-first', action='store_true', help='Process newest emails first (default: oldest first)')
        parser.add_argument('--oldest-first', action='store_true', help='Process oldest emails first (default behavior)')
        parser.add_argument('--rescan', action='store_true', help='Re-analyze already processed emails with current rules')
        args = parser.parse_args()
        
        # Determine sort order (default is oldest first for archiving old emails)
        newest_first = args.newest_first
        
        # Parse date arguments
        since_date = None
        before_date = None
        
        if args.days:
            since_date = datetime.now() - timedelta(days=args.days)
            logger.info(f"Scanning emails from the last {args.days} days")
        
        if args.since:
            since_date = datetime.strptime(args.since, '%Y-%m-%d')
            logger.info(f"Scanning emails since: {args.since}")
        
        if args.before:
            before_date = datetime.strptime(args.before, '%Y-%m-%d')
            logger.info(f"Scanning emails before: {args.before}")
        
        # Load configuration
        config = load_settings()
        
        # Validate configuration
        if not config.validate():
            logger.error("Invalid configuration. Please check your config.yaml file.")
            return 1
        
        # Create scanner
        scanner = EmailScanner(config)
        
        # Initialize
        if not scanner.initialize():
            logger.error("Scanner initialization failed")
            return 1
        
        # Use command-line limit if provided, otherwise use config
        scan_limit = args.limit if args.limit else config.scan_limit
        
        # Scan emails
        processed = scanner.scan_new_emails(
            folder=args.folder,
            limit=scan_limit,
            since_date=since_date,
            before_date=before_date,
            newest_first=newest_first,
            rescan=args.rescan
        )
        
        logger.info(f"Scan complete: {processed} emails processed")
        
        # Cleanup
        scanner.cleanup()
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Scanner interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Scanner failed: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
