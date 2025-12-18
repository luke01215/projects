"""
Search All Mail for recent activity
"""
from settings import load_settings
from email_client import EmailClient
from datetime import datetime, timedelta


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
    
    # Try different folder name formats
    folder_names = [
        '[Gmail]/All Mail',
        '"[Gmail]/All Mail"',
        '[Gmail]/All%20Mail'
    ]
    
    for folder_name in folder_names:
        print(f"\nTrying to select: {folder_name}")
        try:
            status, data = client.connection.select(folder_name)
            if status == 'OK':
                print(f"  ✓ Successfully selected!")
                
                # Search for emails from today
                today = datetime.now().strftime("%d-%b-%Y")
                print(f"\n  Searching for emails from today ({today})...")
                status, search_data = client.connection.search(None, f'SINCE {today}')
                
                if status == 'OK' and search_data[0]:
                    email_ids = search_data[0].decode().split()
                    print(f"  Found {len(email_ids)} emails from today")
                    
                    if email_ids:
                        # Show last 5
                        recent = email_ids[-5:] if len(email_ids) > 5 else email_ids
                        print(f"\n  Most recent {len(recent)}:")
                        for eid in recent:
                            status, msg_data = client.connection.fetch(eid, '(BODY[HEADER.FIELDS (FROM SUBJECT)] FLAGS)')
                            if status == 'OK' and msg_data[0]:
                                print(f"\n    ID: {eid}")
                                header = msg_data[0][1].decode('utf-8', errors='ignore')
                                for line in header.split('\n'):
                                    line = line.strip()
                                    if line:
                                        print(f"      {line}")
                                # Get flags
                                if len(msg_data) > 1:
                                    print(f"      Flags: {msg_data[1]}")
                break
            else:
                print(f"  ✗ Failed: {data}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    client.disconnect()


if __name__ == '__main__':
    main()
