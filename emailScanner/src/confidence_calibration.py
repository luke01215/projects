"""
Confidence calibration system to adjust AI confidence scores based on historical accuracy.

Tracks how often the AI is correct at different confidence levels and adjusts
future scores accordingly.
"""

import sys
from pathlib import Path
from typing import Dict, Optional, Tuple
from sqlalchemy import func, case
from models import Decision, Analysis, Email, init_db, get_session
from settings import load_settings
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)


class ConfidenceCalibrator:
    """
    Tracks AI accuracy by confidence bucket and provides calibrated scores.
    
    This helps correct for overconfident or underconfident AI predictions
    by comparing stated confidence to actual accuracy.
    """
    
    def __init__(self, db_session):
        """
        Initialize calibrator with database session
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session
        
        # Define confidence buckets
        self.buckets = [
            (0.0, 0.5, "very_low"),
            (0.5, 0.7, "low"),
            (0.7, 0.85, "medium"),
            (0.85, 0.95, "high"),
            (0.95, 1.0, "very_high")
        ]
    
    def get_bucket_stats(self) -> Dict[str, Dict]:
        """
        Calculate accuracy statistics for each confidence bucket
        
        Returns:
            Dictionary mapping bucket names to stats
        """
        stats = {}
        
        for min_conf, max_conf, bucket_name in self.buckets:
            # Query decisions in this confidence bucket
            results = self.db_session.query(
                func.count(Decision.id).label('total'),
                func.sum(
                    case(
                        (Decision.approved == True, 1),
                        else_=0
                    )
                ).label('correct'),
                func.avg(Analysis.confidence_score).label('avg_confidence')
            ).join(
                Email, Decision.email_id == Email.id
            ).join(
                Analysis, Email.id == Analysis.email_id
            ).filter(
                Analysis.confidence_score >= min_conf,
                Analysis.confidence_score < max_conf if max_conf < 1.0 else Analysis.confidence_score <= max_conf,
                Decision.action_taken.isnot(None)  # Only calibrate on human-reviewed decisions
            ).first()
            
            total = results.total or 0
            correct = results.correct or 0
            avg_confidence = results.avg_confidence or ((min_conf + max_conf) / 2)
            
            accuracy = correct / total if total > 0 else 0.0
            
            stats[bucket_name] = {
                'min_confidence': min_conf,
                'max_confidence': max_conf,
                'total_decisions': total,
                'correct_decisions': correct,
                'accuracy': accuracy,
                'avg_stated_confidence': avg_confidence,
                'calibration_error': avg_confidence - accuracy if total > 0 else 0.0,
                'sample_size_sufficient': total >= 5  # Need at least 5 samples to calibrate
            }
        
        return stats
    
    def calibrate_confidence(self, stated_confidence: float, category: str = None) -> Tuple[float, str]:
        """
        Adjust a confidence score based on historical accuracy
        
        Args:
            stated_confidence: Original confidence from AI (0.0 to 1.0)
            category: Optional email category for category-specific calibration
        
        Returns:
            Tuple of (calibrated_confidence, reasoning)
        """
        # Find which bucket this falls into
        bucket_name = None
        for min_conf, max_conf, name in self.buckets:
            if min_conf <= stated_confidence < max_conf or (max_conf == 1.0 and stated_confidence <= max_conf):
                bucket_name = name
                break
        
        if not bucket_name:
            return stated_confidence, "No calibration applied"
        
        # Get stats for this bucket
        stats = self.get_bucket_stats()
        bucket_stats = stats.get(bucket_name, {})
        
        # If not enough data, return original confidence
        if not bucket_stats.get('sample_size_sufficient', False):
            return stated_confidence, f"Insufficient data for calibration ({bucket_stats.get('total_decisions', 0)} samples)"
        
        # Calculate calibrated confidence
        accuracy = bucket_stats['accuracy']
        calibration_error = bucket_stats['calibration_error']
        
        # Apply calibration: adjust stated confidence toward actual accuracy
        # Use a conservative approach - only adjust 50% of the error
        calibrated = stated_confidence - (calibration_error * 0.5)
        
        # Clamp to valid range
        calibrated = max(0.0, min(1.0, calibrated))
        
        # Generate reasoning
        if abs(calibration_error) < 0.05:
            reasoning = f"Well-calibrated (AI accuracy: {accuracy:.1%})"
        elif calibration_error > 0:
            reasoning = f"Adjusted down (AI tends to be overconfident in this range: {accuracy:.1%} actual vs {bucket_stats['avg_stated_confidence']:.1%} stated)"
        else:
            reasoning = f"Adjusted up (AI tends to be underconfident in this range: {accuracy:.1%} actual vs {bucket_stats['avg_stated_confidence']:.1%} stated)"
        
        return calibrated, reasoning
    
    def get_overall_stats(self) -> Dict:
        """
        Get overall calibration statistics
        
        Returns:
            Dictionary with overall stats
        """
        # Query all decisions with confidence scores
        results = self.db_session.query(
            func.count(Decision.id).label('total'),
            func.sum(case((Decision.approved == True, 1), else_=0)).label('correct'),
            func.avg(Analysis.confidence_score).label('avg_confidence')
        ).join(
            Email, Decision.email_id == Email.id
        ).join(
            Analysis, Email.id == Analysis.email_id
        ).filter(
            Decision.action_taken.isnot(None)
        ).first()
        
        total = results.total or 0
        correct = results.correct or 0
        avg_confidence = results.avg_confidence or 0.0
        
        accuracy = correct / total if total > 0 else 0.0
        
        return {
            'total_decisions': total,
            'overall_accuracy': accuracy,
            'avg_confidence': avg_confidence,
            'calibration_error': avg_confidence - accuracy,
            'is_overconfident': avg_confidence > accuracy + 0.05,
            'is_underconfident': avg_confidence < accuracy - 0.05
        }
    
    def print_calibration_report(self):
        """Print a detailed calibration report"""
        print("=== AI Confidence Calibration Report ===\n")
        
        # Overall stats
        overall = self.get_overall_stats()
        print("Overall Performance:")
        print(f"  Total Decisions: {overall['total_decisions']}")
        print(f"  Accuracy: {overall['overall_accuracy']:.1%}")
        print(f"  Avg Confidence: {overall['avg_confidence']:.1%}")
        print(f"  Calibration Error: {overall['calibration_error']:+.1%}")
        
        if overall['is_overconfident']:
            print("  ⚠ AI tends to be overconfident")
        elif overall['is_underconfident']:
            print("  ⚠ AI tends to be underconfident")
        else:
            print("  ✓ AI is well-calibrated")
        
        print()
        
        # Bucket stats
        bucket_stats = self.get_bucket_stats()
        print("Performance by Confidence Level:")
        print()
        
        for bucket_name in ['very_low', 'low', 'medium', 'high', 'very_high']:
            stats = bucket_stats.get(bucket_name, {})
            
            if stats.get('total_decisions', 0) == 0:
                continue
            
            conf_range = f"{stats['min_confidence']:.0%}-{stats['max_confidence']:.0%}"
            print(f"  {conf_range} confidence ({bucket_name}):")
            print(f"    Samples: {stats['total_decisions']}")
            print(f"    Actual Accuracy: {stats['accuracy']:.1%}")
            print(f"    Avg Stated Confidence: {stats['avg_stated_confidence']:.1%}")
            print(f"    Calibration Error: {stats['calibration_error']:+.1%}")
            
            if not stats['sample_size_sufficient']:
                print(f"    ⚠ Need more data (min 5 samples)")
            elif abs(stats['calibration_error']) < 0.05:
                print(f"    ✓ Well-calibrated")
            elif stats['calibration_error'] > 0:
                print(f"    ⚠ Overconfident in this range")
            else:
                print(f"    ⚠ Underconfident in this range")
            
            print()


def main():
    """Main entry point for calibration report"""
    # Load settings
    config = load_settings()
    
    # Initialize database
    engine = init_db(config.database_url)
    db_session = get_session(engine)
    
    try:
        calibrator = ConfidenceCalibrator(db_session)
        calibrator.print_calibration_report()
        
        print("\n=== Example Calibrations ===\n")
        
        # Show example calibrations
        test_confidences = [0.95, 0.85, 0.70, 0.55]
        for conf in test_confidences:
            calibrated, reasoning = calibrator.calibrate_confidence(conf)
            print(f"Stated: {conf:.0%} → Calibrated: {calibrated:.0%}")
            print(f"  Reason: {reasoning}")
            print()
    
    finally:
        db_session.close()


if __name__ == '__main__':
    main()
