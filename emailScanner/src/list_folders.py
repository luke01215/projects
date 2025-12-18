"""
List all Gmail folders to see the correct folder names
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
    
    print("Available folders:")
    folders = client.list_folders()
    for folder in folders:
        print(f"  {folder}")
    
    client.disconnect()


if __name__ == '__main__':
    main()
