"""
Check labels on emails that are already in Trash
"""
from settings import load_settings
from email_client import EmailClient


def main():
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
    
    # Select Trash
    print('Selecting "[Gmail]/Trash"...')
    status, data = client.connection.select('"[Gmail]/Trash"')
    if status != 'OK':
        print(f"Failed: {data}")
        return
    
    print("✓ Selected successfully\n")
    
    # Get last 3 emails
    status, data = client.connection.search(None, 'ALL')
    if status == 'OK':
        email_ids = data[0].decode().split()
        if email_ids:
            print(f"Total emails in Trash: {len(email_ids)}")
            recent = email_ids[-3:] if len(email_ids) > 3 else email_ids
            
            for eid in recent:
                print(f"\n--- Email ID: {eid} ---")
                
                # Get X-GM-LABELS
                status, label_data = client.connection.fetch(eid, '(X-GM-LABELS)')
                if status == 'OK':
                    print(f"X-GM-LABELS: {label_data}")
                
                # Get subject
                status, subj_data = client.connection.fetch(eid, '(BODY[HEADER.FIELDS (SUBJECT)])')
                if status == 'OK' and subj_data[0]:
                    header = subj_data[0][1].decode('utf-8', errors='ignore')
                    print(f"Subject: {header.strip()}")
    
    client.disconnect()


if __name__ == '__main__':
    main()
