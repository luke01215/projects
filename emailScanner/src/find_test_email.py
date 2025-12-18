"""
Find an email to use for testing deletion
"""
from models import Email, init_db, get_session
from settings import load_settings

def find_test_candidate():
    """Find a good candidate email for testing deletion"""
    config = load_settings()
    engine = init_db(config.database_url)
    session = get_session(engine)
    
    # Find a few recent emails from inbox
    emails = session.query(Email).filter_by(folder='INBOX').order_by(Email.received_date.desc()).limit(10).all()
    
    print("Recent emails in database (good candidates for testing):\n")
    print(f"{'ID':<6} {'Email ID':<12} {'Sender':<40} {'Subject':<50}")
    print("=" * 110)
    
    for email in emails:
        print(f"{email.id:<6} {email.email_id:<12} {email.sender[:40]:<40} {email.subject[:50] if email.subject else '(no subject)'}")
    
    print("\nUsage: python test_delete.py <Email ID from above>")
    print("Example: python test_delete.py", emails[0].email_id if emails else "12345")
    
    session.close()

if __name__ == '__main__':
    find_test_candidate()
