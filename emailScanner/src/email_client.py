"""
Email client for connecting to IMAP servers and fetching emails.
Supports Gmail, Outlook, and other IMAP-compatible providers.
"""
import imaplib
import email
import email.policy
from email.header import decode_header
from datetime import datetime, UTC
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class EmailClient:
    """IMAP email client for fetching and managing emails"""
    
    def __init__(self, server: str, email_address: str, password: str, port: int = 993):
        """
        Initialize email client
        
        Args:
            server: IMAP server address (e.g., 'imap.gmail.com')
            email_address: Your email address
            password: Email password or app-specific password
            port: IMAP port (default 993 for SSL)
        """
        self.server = server
        self.email_address = email_address
        self.password = password
        self.port = port
        self.connection = None
        
    def connect(self) -> bool:
        """Connect to IMAP server"""
        try:
            logger.info(f"Connecting to {self.server}:{self.port}")
            self.connection = imaplib.IMAP4_SSL(self.server, self.port)
            self.connection.login(self.email_address, self.password)
            logger.info("Successfully connected to email server")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from IMAP server"""
        if self.connection:
            try:
                # Only close if a folder is selected
                if hasattr(self.connection, 'state') and self.connection.state == 'SELECTED':
                    self.connection.close()
                self.connection.logout()
                logger.info("Disconnected from email server")
            except Exception as e:
                logger.debug(f"Error during disconnect: {e}")
    
    def list_folders(self) -> List[str]:
        """List all available folders/mailboxes"""
        if not self.connection:
            return []
        
        try:
            status, folders = self.connection.list()
            if status == 'OK':
                folder_names = []
                for folder in folders:
                    # Parse folder name from response
                    parts = folder.decode().split('"')
                    if len(parts) >= 3:
                        folder_names.append(parts[-2])
                return folder_names
        except Exception as e:
            logger.error(f"Failed to list folders: {e}")
        return []
    
    def select_folder(self, folder: str = 'INBOX') -> bool:
        """Select a folder to work with"""
        try:
            status, messages = self.connection.select(folder)
            if status == 'OK':
                count = int(messages[0])
                logger.info(f"Selected folder '{folder}' with {count} messages")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to select folder '{folder}': {e}")
            return False
    
    def search_emails(self, criteria: str = 'ALL', limit: Optional[int] = None, 
                     newest_first: bool = False) -> List[str]:
        """
        Search for emails matching criteria
        
        Args:
            criteria: IMAP search criteria (e.g., 'ALL', 'UNSEEN', 'FROM "sender@example.com"')
            limit: Maximum number of emails to return
            newest_first: If True, return newest emails first; if False, return oldest first
        
        Returns:
            List of email IDs
        """
        try:
            logger.info(f"Searching emails with criteria: {criteria}")
            status, messages = self.connection.search(None, criteria)
            if status == 'OK':
                email_ids = messages[0].split()
                total_found = len(email_ids)
                
                if limit and total_found > limit:
                    if newest_first:
                        email_ids = email_ids[-limit:]  # Get most recent
                        logger.info(f"Found {total_found} emails, returning {limit} newest")
                    else:
                        email_ids = email_ids[:limit]  # Get oldest
                        logger.info(f"Found {total_found} emails, returning {limit} oldest")
                else:
                    logger.info(f"Found {total_found} emails matching criteria")
                
                return [eid.decode() for eid in email_ids]
        except Exception as e:
            logger.error(f"Failed to search emails: {e}")
        return []
    
    def fetch_email(self, email_id: str) -> Optional[Dict]:
        """
        Fetch a single email by ID
        
        Args:
            email_id: Message sequence number
        
        Returns:
            Dictionary with email data (including UID) or None if failed
        """
        try:
            # Fetch email with UID
            status, msg_data = self.connection.fetch(email_id, '(UID RFC822)')
            if status != 'OK':
                return None
            
            # Parse UID from response
            uid = None
            if msg_data[0]:
                response = msg_data[0][0].decode('utf-8', errors='ignore') if isinstance(msg_data[0][0], bytes) else str(msg_data[0][0])
                import re
                uid_match = re.search(r'UID (\d+)', response)
                if uid_match:
                    uid = uid_match.group(1)
            
            # Parse email with encoding error handling
            raw_email = msg_data[0][1]
            
            # Try standard parsing first, with lenient policy to handle encoding issues
            try:
                msg = email.message_from_bytes(raw_email, policy=email.policy.default)
            except (LookupError, UnicodeDecodeError) as e:
                # Handle unknown encoding errors with even more lenient parsing
                logger.warning(f"Email {email_id} has encoding issue ({e}), attempting recovery with relaxed policy")
                try:
                    # Try with completely lenient policy
                    msg = email.message_from_bytes(raw_email, policy=email.policy.compat32)
                except Exception as e2:
                    logger.error(f"Could not parse email {email_id} even with lenient policy: {e2}")
                    return None
            
            # Extract email data
            email_data = {
                'email_id': uid if uid else email_id,  # Store UID, fallback to sequence number
                'sender': self._decode_header(msg.get('From', '')),
                'recipient': self._decode_header(msg.get('To', '')),
                'subject': self._decode_header(msg.get('Subject', '')),
                'date': self._parse_date(msg.get('Date', '')),
                'size_bytes': len(raw_email),
                'has_attachments': False,
                'body_full': '',
                'body_preview': ''
            }
            
            # Extract body
            body = self._extract_body(msg)
            email_data['body_full'] = body
            email_data['body_preview'] = body[:500] if body else ''
            
            # Check for attachments
            email_data['has_attachments'] = self._has_attachments(msg)
            
            return email_data
            
        except Exception as e:
            logger.error(f"Failed to fetch email {email_id}: {e}")
            return None
    
    def fetch_emails_batch(self, email_ids: List[str], max_emails: Optional[int] = None) -> List[Dict]:
        """
        Fetch multiple emails in batch
        
        Args:
            email_ids: List of email IDs to fetch
            max_emails: Maximum number of emails to fetch
        
        Returns:
            List of email data dictionaries
        """
        if max_emails:
            email_ids = email_ids[:max_emails]
        
        emails = []
        for i, email_id in enumerate(email_ids, 1):
            logger.info(f"Fetching email {i}/{len(email_ids)}")
            email_data = self.fetch_email(email_id)
            if email_data:
                emails.append(email_data)
        
        logger.info(f"Successfully fetched {len(emails)} emails")
        return emails
    
    def mark_as_read(self, email_id: str) -> bool:
        """Mark an email as read"""
        try:
            self.connection.store(email_id, '+FLAGS', '\\Seen')
            return True
        except Exception as e:
            logger.error(f"Failed to mark email {email_id} as read: {e}")
            return False
    
    def delete_email(self, email_id: str) -> bool:
        """Delete an email (move to Gmail Trash)
        
        Args:
            email_id: IMAP UID (unique and persistent identifier)
        """
        try:
            # email_id is now the UID directly
            uid = email_id
            
            # Gmail IMAP requires UID COPY for proper Trash handling
            result = self.connection.uid('COPY', uid, '"[Gmail]/Trash"')
            
            if result[0] == 'OK':
                # Mark as deleted and expunge
                self.connection.uid('STORE', uid, '+FLAGS', '(\\Deleted)')
                self.connection.expunge()
                
                logger.info(f"Moved email UID {uid} to Trash")
                return True
            else:
                logger.error(f"UID COPY failed for {uid}: {result}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to delete email {email_id}: {e}")
            return False
    
    def move_to_folder(self, email_id: str, destination_folder: str) -> bool:
        """Move email to a different folder"""
        try:
            result = self.connection.copy(email_id, destination_folder)
            if result[0] == 'OK':
                self.connection.store(email_id, '+FLAGS', '\\Deleted')
                self.connection.expunge()
                logger.info(f"Moved email {email_id} to {destination_folder}")
                return True
        except Exception as e:
            logger.error(f"Failed to move email {email_id}: {e}")
        return False
    
    @staticmethod
    def _decode_header(header: str) -> str:
        """Decode email header"""
        if not header:
            return ''
        
        decoded_parts = []
        for part, encoding in decode_header(header):
            if isinstance(part, bytes):
                decoded_parts.append(part.decode(encoding or 'utf-8', errors='ignore'))
            else:
                decoded_parts.append(part)
        return ''.join(decoded_parts)
    
    @staticmethod
    def _parse_date(date_str: str) -> datetime:
        """Parse email date"""
        try:
            return email.utils.parsedate_to_datetime(date_str)
        except Exception:
            return datetime.now(UTC)
    
    @staticmethod
    def _extract_body(msg) -> str:
        """Extract email body text"""
        body = ''
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body += payload.decode('utf-8', errors='ignore')
                    except Exception:
                        pass
        else:
            try:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = payload.decode('utf-8', errors='ignore')
            except Exception:
                pass
        
        return body.strip()
    
    @staticmethod
    def _has_attachments(msg) -> bool:
        """Check if email has attachments"""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_disposition() == 'attachment':
                    return True
        return False


# Example usage
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Example configuration (replace with actual values)
    client = EmailClient(
        server='imap.gmail.com',
        email_address='your.email@gmail.com',
        password='your_app_password'
    )
    
    if client.connect():
        # List folders
        folders = client.list_folders()
        print(f"Available folders: {folders}")
        
        # Select inbox
        client.select_folder('INBOX')
        
        # Search for unread emails
        email_ids = client.search_emails('UNSEEN', limit=5)
        
        # Fetch emails
        emails = client.fetch_emails_batch(email_ids)
        for email_data in emails:
            print(f"\nFrom: {email_data['sender']}")
            print(f"Subject: {email_data['subject']}")
            print(f"Preview: {email_data['body_preview'][:100]}")
        
        client.disconnect()
