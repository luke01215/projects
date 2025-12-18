"""
Quick test script to verify where deleted emails actually go
"""
import sys
import socket
from settings import load_settings
from email_client import EmailClient


def test_connection(server: str, port: int):
    """Test basic TCP connection to IMAP server"""
    try:
        print(f"Testing TCP connection to {server}:{port}...")
        sock = socket.create_connection((server, port), timeout=10)
        sock.close()
        print("✓ TCP connection successful")
        return True
    except socket.gaierror as e:
        print(f"✗ DNS resolution failed: {e}")
        return False
    except socket.timeout:
        print("✗ Connection timed out")
        return False
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False


def test_delete(email_id: str):
    """Test deleting a specific email and report where it goes"""
    print(f"Testing deletion of email ID: {email_id}")
    
    # Load settings and connect
    config = load_settings()
    print(f"Connecting to {config.email_server}:{config.email_port} as {config.email_address}")
    
    # Test basic connection first
    if not test_connection(config.email_server, config.email_port):
        print("\nCannot proceed - basic network connection failed")
        print("Check: VPN status, firewall, network connectivity")
        return
    
    client = EmailClient(
        server=config.email_server,
        email_address=config.email_address,
        password=config.email_password,
        port=config.email_port
    )
    
    try:
        if not client.connect():
            print("Failed to connect to email server")
            return
    except Exception as e:
        print(f"Connection error: {e}")
        print(f"Server: {config.email_server}")
        print(f"Port: {config.email_port}")
        return
    
    # Select inbox to find the email
    client.select_folder('INBOX')
    
    # Get the Message-ID header so we can track it across folders
    print(f"\nFetching email {email_id} metadata...")
    status, data = client.connection.fetch(email_id, '(BODY[HEADER.FIELDS (MESSAGE-ID SUBJECT)])')
    message_id = None
    subject = None
    if status == 'OK' and data and data[0]:
        header_data = data[0][1].decode('utf-8', errors='ignore')
        for line in header_data.split('\n'):
            if line.startswith('Message-ID:'):
                message_id = line.split(':', 1)[1].strip()
            elif line.startswith('Subject:'):
                subject = line.split(':', 1)[1].strip()
        print(f"  Message-ID: {message_id}")
        print(f"  Subject: {subject}")
    
    # Get Trash count before deletion
    print(f"\nGetting Trash count before deletion...")
    client.connection.select('"[Gmail]/Trash"')
    status, data = client.connection.search(None, 'ALL')
    before_count = len(data[0].split()) if status == 'OK' else 0
    print(f"  Trash has {before_count} emails")
    
    # Return to INBOX for deletion
    client.select_folder('INBOX')
    
    # Delete the email
    print(f"\nDeleting email {email_id}...")
    result = client.delete_email(email_id)
    print(f"  Delete result: {result}")
    
    # Wait for Gmail to sync
    print(f"\nWaiting 3 seconds for Gmail to sync...")
    import time
    time.sleep(3)
    
    # Get Trash count after deletion
    print(f"\nGetting Trash count after deletion...")
    client.connection.select('"[Gmail]/Trash"')
    status, data = client.connection.search(None, 'ALL')
    after_count = len(data[0].split()) if status == 'OK' else 0
    print(f"  Trash now has {after_count} emails")
    if after_count > before_count:
        print(f"  ✓ Trash count increased by {after_count - before_count}!")
    else:
        print(f"  ✗ Trash count did not increase")
    
    # Check various folders to see where it ended up
    folders_to_check = [
        ('INBOX', 'INBOX'),
        ('[Gmail]/Trash', '"[Gmail]/Trash"'),
        ('[Gmail]/All Mail', '"[Gmail]/All Mail"'),
        ('[Gmail]/Spam', '"[Gmail]/Spam"')
    ]
    
    for display_name, folder_name in folders_to_check:
        print(f"\nChecking {display_name}...")
        try:
            status, messages = client.connection.select(folder_name)
            if status != 'OK':
                print(f"  Failed to select folder: {messages}")
                continue
            
            if message_id:
                # Search by Message-ID header
                status, search_data = client.connection.search(None, f'HEADER Message-ID "{message_id}"')
                if status == 'OK' and search_data[0]:
                    email_ids = search_data[0].decode().split()
                    if email_ids:
                        print(f"  ✓ Email FOUND in {display_name} with ID(s): {email_ids}")
                    else:
                        print(f"  ✗ Email NOT in {display_name}")
                else:
                    print(f"  ✗ Email NOT in {display_name}")
            else:
                # Fallback: check if original ID exists
                status, data = client.connection.search(None, 'ALL')
                if status == 'OK':
                    email_ids = data[0].split()
                    if email_id.encode() in email_ids:
                        print(f"  ✓ Email FOUND in {display_name}")
                    else:
                        print(f"  ✗ Email NOT in {display_name}")
        except Exception as e:
            print(f"  Error checking {display_name}: {e}")
    
    client.disconnect()
    print("\nTest complete!")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python test_delete.py <email_id>")
        print("Example: python test_delete.py 12345")
        sys.exit(1)
    
    test_delete(sys.argv[1])
