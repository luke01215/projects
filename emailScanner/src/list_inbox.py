"""
List current emails in INBOX with their sequence numbers
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
    
    print('Selecting INBOX...')
    client.select_folder('INBOX')
    
    # Get last 10 emails
    status, data = client.connection.search(None, 'ALL')
    if status == 'OK':
        email_ids = data[0].decode().split()
        print(f"\nTotal in INBOX: {len(email_ids)}")
        
        if email_ids:
            recent = email_ids[-10:] if len(email_ids) > 10 else email_ids
            print(f"\nLast {len(recent)} emails in INBOX:\n")
            
            for eid in recent:
                # Get UID, subject, from
                status, uid_data = client.connection.fetch(eid, '(UID BODY[HEADER.FIELDS (FROM SUBJECT)])')
                if status == 'OK' and uid_data and uid_data[0]:
                    # Parse
                    response = uid_data[0]
                    if isinstance(response, tuple) and len(response) >= 2:
                        info = response[0].decode('utf-8', errors='ignore') if isinstance(response[0], bytes) else str(response[0])
                        header = response[1].decode('utf-8', errors='ignore') if isinstance(response[1], bytes) else str(response[1])
                        
                        # Extract UID
                        import re
                        uid_match = re.search(r'UID (\d+)', info)
                        uid = uid_match.group(1) if uid_match else '?'
                        
                        # Extract subject/from
                        subject = ''
                        from_addr = ''
                        for line in header.split('\n'):
                            if line.startswith('Subject:'):
                                subject = line[8:].strip()[:50]
                            elif line.startswith('From:'):
                                from_addr = line[5:].strip()[:40]
                        
                        print(f"  Msg: {eid:>5}  UID: {uid:>6}  From: {from_addr}")
                        print(f"                      Subject: {subject}")
                        print()
    
    client.disconnect()
    print("\nUse: python src\\test_delete.py <Msg number>")


if __name__ == '__main__':
    main()
