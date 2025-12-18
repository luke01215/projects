"""
Quick email viewer - View email details by ID
"""
import sys
import argparse
from datetime import datetime
from models import Email, Analysis, Decision, init_db, get_session
from settings import load_settings

def view_email(email_identifier: str):
    """Display email details"""
    # Load config and connect to database
    config = load_settings()
    engine = init_db(config.database_url)
    session = get_session(engine)
    
    # Try to find email by database ID first, then by IMAP email_id
    email = None
    
    # Try as database ID (integer)
    if email_identifier.isdigit():
        email = session.query(Email).filter(Email.id == int(email_identifier)).first()
    
    # If not found, try as IMAP email_id (string)
    if not email:
        email = session.query(Email).filter(Email.email_id == email_identifier).first()
    
    if not email:
        print(f"❌ Email not found (tried as database ID and IMAP ID): {email_identifier}")
        return 1
    
    analysis = session.query(Analysis).filter(Analysis.email_id == email.id).first()
    decision = session.query(Decision).filter(Decision.email_id == email.id).first()
    
    # Display email details
    print("=" * 80)
    print(f"📧 EMAIL #{email.id} (IMAP ID: {email.email_id})")
    print("=" * 80)
    print(f"From:     {email.sender}")
    print(f"To:       {email.recipient or 'N/A'}")
    print(f"Subject:  {email.subject}")
    print(f"Date:     {email.received_date}")
    print(f"Folder:   {email.folder}")
    print(f"Size:     {email.size_bytes} bytes")
    print(f"Attachments: {'Yes' if email.has_attachments else 'No'}")
    
    if analysis:
        print("\n" + "-" * 80)
        print("🤖 AI ANALYSIS")
        print("-" * 80)
        print(f"Recommendation: {analysis.recommendation.upper()}")
        print(f"Confidence:     {analysis.confidence_score:.2%}")
        print(f"Category:       {analysis.category or 'N/A'}")
        print(f"Priority:       {analysis.priority or 'N/A'}")
        print(f"Status:         {analysis.status}")
        print(f"Model:          {analysis.model_name}")
        print(f"\nReasoning:")
        print(f"  {analysis.reasoning or 'No reasoning provided'}")
    
    if decision:
        print("\n" + "-" * 80)
        print("👤 HUMAN DECISION")
        print("-" * 80)
        print(f"Approved:      {'Yes' if decision.approved else 'No'}")
        print(f"Action Taken:  {decision.action_taken or 'N/A'}")
        print(f"Decided At:    {decision.decided_at}")
        if decision.notes:
            print(f"Notes:         {decision.notes}")
    
    print("\n" + "-" * 80)
    print("📄 EMAIL BODY PREVIEW")
    print("-" * 80)
    preview = email.body_preview or "(empty)"
    print(preview[:500])
    if len(preview) > 500:
        print(f"\n... (showing first 500 of {len(preview)} characters)")
    
    print("\n" + "=" * 80)
    
    session.close()
    return 0


def main():
    parser = argparse.ArgumentParser(description='View email details by ID')
    parser.add_argument('email_id', type=str, help='Email ID to view (database ID or IMAP message ID)')
    parser.add_argument('--full-body', action='store_true', help='Show full email body (not just preview)')
    
    args = parser.parse_args()
    
    if args.full_body:
        # TODO: Implement full body view
        print("Full body view not yet implemented. Use web UI for full content.")
        return 1
    
    return view_email(args.email_id)


if __name__ == '__main__':
    sys.exit(main())
