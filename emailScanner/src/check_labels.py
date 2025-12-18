"""
Check the actual labels on a specific email
"""
import sys
from settings import load_settings
from email_client import EmailClient


def main(email_id: str):
    config = load_settings()
    
    client = EmailClient(
        server=config.email_server,
        email_address=config.email_address,
        password=config.email_password,
        port=config.email_port
    )
    
    if not client.connect():
        print("Failed to connect")
        return
    
    # Select All Mail
    print('Selecting "[Gmail]/All Mail"...')
    status, data = client.connection.select('"[Gmail]/All Mail"')
    if status != 'OK':
        print(f"Failed: {data}")
        return
    
    print(f"\nFetching labels for email {email_id}...")
    
    # Get X-GM-LABELS
    status, data = client.connection.fetch(email_id, '(X-GM-LABELS)')
    if status == 'OK':
        print(f"X-GM-LABELS result: {data}")
    
    # Also get FLAGS
    status, data = client.connection.fetch(email_id, '(FLAGS)')
    if status == 'OK':
        print(f"FLAGS result: {data}")
    
    # Get subject for reference
    status, data = client.connection.fetch(email_id, '(BODY[HEADER.FIELDS (SUBJECT)])')
    if status == 'OK' and data[0]:
        header = data[0][1].decode('utf-8', errors='ignore')
        print(f"\nSubject: {header.strip()}")
    
    client.disconnect()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python check_labels.py <email_id>")
        sys.exit(1)
    
    main(sys.argv[1])
