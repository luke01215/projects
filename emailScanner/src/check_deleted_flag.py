"""
Search for emails with the \Deleted flag in All Mail
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
    
    # Select All Mail with quotes
    print('Selecting "[Gmail]/All Mail"...')
    status, data = client.connection.select('"[Gmail]/All Mail"')
    if status != 'OK':
        print(f"Failed: {data}")
        return
    
    print("✓ Selected successfully\n")
    
    # Search for emails with \Deleted flag
    print("Searching for emails with \\Deleted flag...")
    status, search_data = client.connection.search(None, 'DELETED')
    
    if status == 'OK':
        email_ids = search_data[0].decode().split()
        print(f"Found {len(email_ids)} emails with \\Deleted flag")
        
        if email_ids:
            # Show last 10
            recent = email_ids[-10:] if len(email_ids) > 10 else email_ids
            print(f"\nMost recent {len(recent)} deleted emails:")
            
            for eid in recent:
                status, msg_data = client.connection.fetch(eid, '(BODY[HEADER.FIELDS (FROM SUBJECT DATE)] FLAGS)')
                if status == 'OK' and msg_data:
                    print(f"\n  ID: {eid}")
                    # Parse response
                    for item in msg_data:
                        if isinstance(item, tuple) and len(item) >= 2:
                            header = item[1].decode('utf-8', errors='ignore')
                            for line in header.split('\n'):
                                line = line.strip()
                                if line:
                                    print(f"    {line}")
                        elif isinstance(item, bytes):
                            flags = item.decode('utf-8', errors='ignore')
                            if 'FLAGS' in flags:
                                print(f"    {flags}")
    else:
        print(f"Search failed: {search_data}")
    
    client.disconnect()


if __name__ == '__main__':
    main()
