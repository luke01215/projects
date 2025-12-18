"""
Pattern learning script to auto-generate rules from consistent user decisions.

Analyzes historical decisions and suggests rules that can be added to the
rules engine to automate future classifications.
"""

import sys
from pathlib import Path
from typing import List, Dict
from sqlalchemy import func, case
from models import Decision, Email, Analysis, init_db, get_session
from settings import load_settings

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def get_sender_patterns(db_session, min_decisions: int = 10, pattern_threshold: float = 0.9) -> List[Dict]:
    """
    Find senders with consistent decision patterns
    
    Args:
        db_session: Database session
        min_decisions: Minimum number of decisions required
        pattern_threshold: Minimum consistency rate (0.9 = 90%)
    
    Returns:
        List of sender patterns with statistics
    """
    # Query decisions grouped by sender
    results = db_session.query(
        Email.sender,
        func.count(Decision.id).label('total'),
        func.sum(case((Decision.action_taken == 'kept', 1), else_=0)).label('keep_count'),
        func.sum(case((Decision.action_taken == 'deleted', 1), else_=0)).label('delete_count')
    ).join(
        Email, Decision.email_id == Email.id
    ).group_by(
        Email.sender
    ).having(
        func.count(Decision.id) >= min_decisions
    ).all()
    
    patterns = []
    for sender, total, keep_count, delete_count in results:
        keep_rate = keep_count / total if total > 0 else 0
        delete_rate = delete_count / total if total > 0 else 0
        
        # Check if pattern is consistent enough
        if keep_rate >= pattern_threshold:
            patterns.append({
                'sender': sender,
                'action': 'keep',
                'total_decisions': total,
                'consistency_rate': keep_rate,
                'rule_type': 'vip_sender'
            })
        elif delete_rate >= pattern_threshold:
            patterns.append({
                'sender': sender,
                'action': 'delete',
                'total_decisions': total,
                'consistency_rate': delete_rate,
                'rule_type': 'auto_delete'
            })
    
    return patterns


def get_category_patterns(db_session, min_decisions: int = 15, pattern_threshold: float = 0.85) -> List[Dict]:
    """
    Find categories with consistent decision patterns
    
    Args:
        db_session: Database session
        min_decisions: Minimum number of decisions required
        pattern_threshold: Minimum consistency rate (0.85 = 85%)
    
    Returns:
        List of category patterns with statistics
    """
    # Query decisions grouped by category
    results = db_session.query(
        Analysis.category,
        func.count(Decision.id).label('total'),
        func.sum(case((Decision.action_taken == 'kept', 1), else_=0)).label('keep_count'),
        func.sum(case((Decision.action_taken == 'deleted', 1), else_=0)).label('delete_count')
    ).join(
        Email, Decision.email_id == Email.id
    ).join(
        Analysis, Email.id == Analysis.email_id
    ).group_by(
        Analysis.category
    ).having(
        func.count(Decision.id) >= min_decisions
    ).all()
    
    patterns = []
    for category, total, keep_count, delete_count in results:
        keep_rate = keep_count / total if total > 0 else 0
        delete_rate = delete_count / total if total > 0 else 0
        
        # Check if pattern is consistent enough
        if delete_rate >= pattern_threshold:
            patterns.append({
                'category': category,
                'action': 'delete',
                'total_decisions': total,
                'consistency_rate': delete_rate,
                'rule_type': f'category_{category}'
            })
    
    return patterns


def get_domain_patterns(db_session, min_decisions: int = 8, pattern_threshold: float = 0.9) -> List[Dict]:
    """
    Find email domains with consistent decision patterns
    
    Args:
        db_session: Database session
        min_decisions: Minimum number of decisions required
        pattern_threshold: Minimum consistency rate (0.9 = 90%)
    
    Returns:
        List of domain patterns with statistics
    """
    # Query decisions grouped by domain (extracted from sender email)
    results = db_session.query(
        func.substr(Email.sender, func.instr(Email.sender, '@') + 1).label('domain'),
        func.count(Decision.id).label('total'),
        func.sum(case((Decision.action_taken == 'kept', 1), else_=0)).label('keep_count'),
        func.sum(case((Decision.action_taken == 'deleted', 1), else_=0)).label('delete_count')
    ).join(
        Email, Decision.email_id == Email.id
    ).group_by(
        'domain'
    ).having(
        func.count(Decision.id) >= min_decisions
    ).all()
    
    patterns = []
    for domain, total, keep_count, delete_count in results:
        if not domain or '@' in domain:  # Skip invalid domains
            continue
            
        keep_rate = keep_count / total if total > 0 else 0
        delete_rate = delete_count / total if total > 0 else 0
        
        # Check if pattern is consistent enough
        if delete_rate >= pattern_threshold:
            patterns.append({
                'domain': domain,
                'action': 'delete',
                'total_decisions': total,
                'consistency_rate': delete_rate,
                'rule_type': 'domain_auto_delete'
            })
    
    return patterns


def format_rule_suggestion(pattern: Dict) -> str:
    """Format a pattern as a human-readable rule suggestion"""
    if 'sender' in pattern:
        if pattern['action'] == 'keep':
            return (f"Add '{pattern['sender']}' to VIP senders list "
                   f"({pattern['total_decisions']} decisions, "
                   f"{pattern['consistency_rate']*100:.0f}% kept)")
        else:
            return (f"Auto-delete emails from '{pattern['sender']}' "
                   f"({pattern['total_decisions']} decisions, "
                   f"{pattern['consistency_rate']*100:.0f}% deleted)")
    
    elif 'domain' in pattern:
        return (f"Auto-delete all emails from domain '@{pattern['domain']}' "
               f"({pattern['total_decisions']} decisions, "
               f"{pattern['consistency_rate']*100:.0f}% deleted)")
    
    elif 'category' in pattern:
        return (f"Auto-delete category '{pattern['category']}' emails "
               f"({pattern['total_decisions']} decisions, "
               f"{pattern['consistency_rate']*100:.0f}% deleted)")
    
    return "Unknown pattern type"


def main():
    """Main entry point"""
    # Load settings
    config = load_settings()
    
    # Initialize database
    engine = init_db(config.database_url)
    db_session = get_session(engine)
    
    try:
        print("=== Email Pattern Learning ===\n")
        print("Analyzing your past decisions to suggest automatic rules...\n")
        
        # Find sender patterns
        print("1. Sender Patterns:")
        sender_patterns = get_sender_patterns(db_session)
        if sender_patterns:
            for pattern in sender_patterns:
                print(f"   ✓ {format_rule_suggestion(pattern)}")
        else:
            print("   No consistent sender patterns found (need 10+ decisions per sender)")
        
        print()
        
        # Find domain patterns
        print("2. Domain Patterns:")
        domain_patterns = get_domain_patterns(db_session)
        if domain_patterns:
            for pattern in domain_patterns:
                print(f"   ✓ {format_rule_suggestion(pattern)}")
        else:
            print("   No consistent domain patterns found (need 8+ decisions per domain)")
        
        print()
        
        # Find category patterns
        print("3. Category Patterns:")
        category_patterns = get_category_patterns(db_session)
        if category_patterns:
            for pattern in category_patterns:
                print(f"   ✓ {format_rule_suggestion(pattern)}")
        else:
            print("   No consistent category patterns found (need 15+ decisions per category)")
        
        print()
        
        # Summary
        total_suggestions = len(sender_patterns) + len(domain_patterns) + len(category_patterns)
        if total_suggestions > 0:
            print(f"Found {total_suggestions} rule suggestions!")
            print("\nNext steps:")
            print("1. Review suggestions above")
            print("2. Add appropriate rules to config/config.yaml")
            print("3. Rules will be applied automatically on next scan")
        else:
            print("No patterns detected yet. Keep making decisions!")
            print("Pattern detection requires:")
            print("  - 10+ decisions per sender (90% consistency)")
            print("  - 8+ decisions per domain (90% consistency)")
            print("  - 15+ decisions per category (85% consistency)")
    
    finally:
        db_session.close()


if __name__ == '__main__':
    main()
