"""
Rescan specific email(s) by ID - re-analyze with current rules without fetching from IMAP
"""
import sys
import argparse
from datetime import datetime, UTC
from models import Email, Analysis, init_db, get_session
from settings import load_settings
from rules import EmailRules
from ollama_analyzer import OllamaAnalyzer

def rescan_email(email_identifier: str, config):
    """Re-analyze a specific email with current rules"""
    
    # Initialize database
    engine = init_db(config.database_url)
    session = get_session(engine)
    
    # Find email
    email = None
    if email_identifier.isdigit():
        email = session.query(Email).filter(Email.id == int(email_identifier)).first()
    if not email:
        email = session.query(Email).filter(Email.email_id == email_identifier).first()
    
    if not email:
        print(f"❌ Email not found: {email_identifier}")
        session.close()
        return False
    
    print(f"🔄 Rescanning email: {email.subject}")
    print(f"   From: {email.sender}")
    print(f"   Date: {email.received_date}")
    
    # Initialize rules engine
    rules = EmailRules(
        vip_senders=config.vip_senders,
        event_keywords=config.event_keywords,
        job_keywords=config.job_keywords,
        old_event_days=config.old_event_days,
        old_job_days=config.old_job_days,
        newsletter_senders=config.newsletter_senders,
        old_newsletter_days=config.old_newsletter_days,
        promotional_keywords=config.promotional_keywords,
        old_promotional_days=config.old_promotional_days
    )
    
    # Build email_data dict for analysis
    email_data = {
        'email_id': email.email_id,
        'sender': email.sender,
        'recipient': email.recipient,
        'subject': email.subject,
        'body_preview': email.body_preview,
        'body_full': email.body_full,
        'date': email.received_date,
        'size_bytes': email.size_bytes,
        'has_attachments': email.has_attachments,
    }
    
    # Check rules first
    rule_result = rules.check_email(email_data)
    
    if rule_result:
        print(f"✓ Rule matched: {rule_result['rule_matched']}")
        analysis_result = rule_result
        analysis_result['model_name'] = 'rules_engine'
        analysis_result['model_version'] = '1.0'
    else:
        # No rule - analyze with AI
        print("⏳ No rule matched, analyzing with AI...")
        analyzer = OllamaAnalyzer(
            base_url=config.ollama_base_url,
            model=config.ollama_model
        )
        
        if not analyzer.check_connection():
            print("❌ Cannot connect to Ollama")
            session.close()
            return False
        
        analysis_result = analyzer.analyze_email(email_data)
        
        if not analysis_result:
            print("❌ AI analysis failed")
            session.close()
            return False
    
    # Update or create analysis
    analysis = session.query(Analysis).filter(Analysis.email_id == email.id).first()
    
    if analysis:
        # Update existing
        old_rec = analysis.recommendation
        analysis.recommendation = analysis_result['recommendation']
        analysis.confidence_score = analysis_result['confidence_score']
        analysis.reasoning = analysis_result['reasoning']
        analysis.category = analysis_result['category']
        analysis.priority = analysis_result['priority']
        analysis.model_name = analysis_result['model_name']
        analysis.model_version = analysis_result['model_version']
        analysis.status = 'pending_review'
        analysis.analyzed_at = datetime.now(UTC)
        
        print(f"\n✅ Updated analysis:")
        print(f"   Old: {old_rec.upper()}")
        print(f"   New: {analysis.recommendation.upper()}")
    else:
        # Create new
        analysis = Analysis(
            email_id=email.id,
            recommendation=analysis_result['recommendation'],
            confidence_score=analysis_result['confidence_score'],
            reasoning=analysis_result['reasoning'],
            category=analysis_result['category'],
            priority=analysis_result['priority'],
            model_name=analysis_result['model_name'],
            model_version=analysis_result['model_version'],
            status='pending_review',
            analyzed_at=datetime.now(UTC)
        )
        session.add(analysis)
        print(f"\n✅ Created analysis: {analysis.recommendation.upper()}")
    
    print(f"   Confidence: {analysis.confidence_score:.2%}")
    print(f"   Category: {analysis.category}")
    print(f"   Reasoning: {analysis.reasoning}")
    
    session.commit()
    session.close()
    
    return True


def main():
    parser = argparse.ArgumentParser(description='Rescan specific emails by ID or all emails')
    parser.add_argument('email_ids', nargs='*', help='One or more email IDs to rescan (database ID or IMAP ID). Leave empty to rescan all.')
    parser.add_argument('--all', action='store_true', help='Rescan all emails in database')
    
    args = parser.parse_args()
    
    # Load config
    config = load_settings()
    
    # Get email IDs to rescan
    email_ids_to_rescan = []
    
    if args.all or not args.email_ids:
        # Rescan all emails
        print("🔄 Rescanning ALL emails in database...")
        engine = init_db(config.database_url)
        session = get_session(engine)
        
        all_emails = session.query(Email).order_by(Email.received_date.desc()).all()
        email_ids_to_rescan = [str(email.id) for email in all_emails]
        
        print(f"   Found {len(email_ids_to_rescan)} emails to rescan")
        print()
        
        session.close()
    else:
        email_ids_to_rescan = args.email_ids
    
    success_count = 0
    fail_count = 0
    total = len(email_ids_to_rescan)
    
    for idx, email_id in enumerate(email_ids_to_rescan, 1):
        print(f"[{idx}/{total}] ", end='')
        if rescan_email(email_id, config):
            success_count += 1
        else:
            fail_count += 1
        print()  # Blank line between emails
    
    print("=" * 80)
    print(f"✅ Rescanned {success_count} emails successfully")
    if fail_count > 0:
        print(f"❌ Failed to rescan {fail_count} emails")
    
    return 0 if fail_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
