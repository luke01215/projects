"""
Check what's actually in the Trash folder
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
    
    # Check Trash folder
    print("Selecting [Gmail]/Trash folder...")
    if not client.select_folder('[Gmail]/Trash'):
        print("Failed to select Trash")
        return
    
    # Get all emails in Trash
    status, data = client.connection.search(None, 'ALL')
    if status == 'OK':
        email_ids = data[0].decode().split()
        print(f"\nTotal emails in Trash: {len(email_ids)}")
        
        if email_ids:
            print("\nMost recent 5 emails in Trash:")
            # Get last 5
            recent_ids = email_ids[-5:] if len(email_ids) >= 5 else email_ids
            
            for eid in recent_ids:
                status, msg_data = client.connection.fetch(eid, '(BODY[HEADER.FIELDS (FROM SUBJECT DATE)])')
                if status == 'OK' and msg_data[0]:
                    header = msg_data[0][1].decode('utf-8', errors='ignore')
                    print(f"\n  Trash ID: {eid}")
                    for line in header.split('\n'):
                        line = line.strip()
                        if line:
                            print(f"    {line}")
    
    client.disconnect()


if __name__ == '__main__':
    main()
