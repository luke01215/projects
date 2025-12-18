# Progressive Learning System

This document explains the 5-tier progressive learning system that reduces LLM usage by 70-90% over time while improving accuracy.

## Overview

The system learns from your decisions and progressively becomes more efficient:
- **Week 1**: 100% LLM usage (learning phase)
- **Week 2**: ~50% LLM usage (patterns emerging)
- **Month 1**: ~20-30% LLM usage (most patterns learned)
- **Month 2+**: ~10-20% LLM usage (highly optimized)

## 1. Sender Memory Tracking

**Location**: `src/sender_memory.py`

Tracks your keep/delete decisions for each sender and detects patterns.

### Pattern Detection
- Requires 3+ decisions for a sender
- Pattern detected when 90%+ consistent (keep or delete)
- Provides statistics: keep_rate, delete_rate, total decisions

### Usage Example
```python
from sender_memory import SenderMemory

memory = SenderMemory(db_session)

# Check if sender has a pattern
stats = memory.get_sender_stats('sender@domain.com')
# Returns: {'total_decisions': 12, 'keep_rate': 0.92, 'has_pattern': True}

# Get recommendation without LLM
result = memory.should_skip_llm('sender@domain.com')
# Returns: {'recommendation': 'keep', 'reasoning': 'Pattern detected: You've kept 11/12 emails'}
```

## 2. Three-Tier Classification

**Location**: `src/scanner.py` - `analyze_and_store_email()`

Emails are classified in order:

### TIER 1: Rules Engine (Instant)
- VIP senders → always keep
- Old events (60+ days) → delete
- Old newsletters (7+ days) → delete
- Old promotional (90+ days) → delete
- Old job offers (180+ days) → delete
- Personal emails → keep
- Event invitations → keep

If a rule matches, skip Tiers 2 and 3.

### TIER 2: Sender Memory (Pattern Detection)
- Check if sender has 90%+ pattern over 3+ emails
- If yes, use pattern recommendation (skip LLM)
- Example log: `✓ Pattern detected for sender@domain.com: keep`

If no pattern, proceed to Tier 3.

### TIER 3: LLM Analysis (AI)
- Call Ollama LLM for novel emails
- Includes few-shot learning (past similar decisions)
- Applies confidence calibration
- Example log: `→ Analyzing with LLM: sender@domain.com`

## 3. Few-Shot Learning

**Location**: `src/ollama_analyzer.py` - `_get_few_shot_examples()`

When the LLM analyzes an email, it receives 3 past similar decisions as examples.

### Example Prompt
```
Email Details:
- From: newsletter@company.com
- Subject: Weekly digest

Previous decisions you made for similar emails:
- From newsletter@company.com: "Last week's top stories..." → You deleted it (Category: newsletter)
- From digest@service.com: "Your weekly summary" → You deleted it (Category: newsletter)
- From updates@platform.com: "Monthly update" → You kept it (Category: notification)

Now analyze this new email...
```

This helps the LLM learn your preferences and stay consistent.

## 4. Pattern-Based Rule Generator

**Location**: `src/learn_patterns.py`

Analyzes your decisions and suggests automatic rules.

### Pattern Thresholds
- **Senders**: 10+ decisions, 90% consistency
- **Domains**: 8+ decisions, 90% consistency
- **Categories**: 15+ decisions, 85% consistency

### Usage
```bash
cd src
python learn_patterns.py
```

### Example Output
```
=== Email Pattern Learning ===

1. Sender Patterns:
   ✓ Add 'friend@personal.com' to VIP senders list (12 decisions, 100% kept)
   ✓ Auto-delete emails from 'spam@company.com' (15 decisions, 93% deleted)

2. Domain Patterns:
   ✓ Auto-delete all emails from domain '@spammer.net' (10 decisions, 100% deleted)

3. Category Patterns:
   ✓ Auto-delete category 'promotional' emails (25 decisions, 92% deleted)

Found 4 rule suggestions!

Next steps:
1. Review suggestions above
2. Add appropriate rules to config/config.yaml
3. Rules will be applied automatically on next scan
```

You can then add approved patterns to `config/config.yaml`:
```yaml
vip_senders:
  - friend@personal.com

# Or create a new rule type in rules.py for auto-delete senders
```

## 5. Confidence Calibration

**Location**: `src/confidence_calibration.py`

Tracks AI accuracy at different confidence levels and adjusts scores.

### How It Works
The AI might say "95% confident" but only be correct 70% of the time. Calibration fixes this.

**Confidence Buckets**:
- 0-50%: Very low
- 50-70%: Low
- 70-85%: Medium
- 85-95%: High
- 95-100%: Very high

For each bucket, tracks:
- How many times AI was correct
- Average stated confidence vs actual accuracy
- Calibration error

### Usage
```bash
cd src
python confidence_calibration.py
```

### Example Output
```
=== AI Confidence Calibration Report ===

Overall Performance:
  Total Decisions: 50
  Accuracy: 78%
  Avg Confidence: 85%
  Calibration Error: +7%
  ⚠ AI tends to be overconfident

Performance by Confidence Level:

  85%-95% confidence (high):
    Samples: 25
    Actual Accuracy: 72%
    Avg Stated Confidence: 88%
    Calibration Error: +16%
    ⚠ Overconfident in this range

  70%-85% confidence (medium):
    Samples: 15
    Actual Accuracy: 87%
    Avg Stated Confidence: 76%
    Calibration Error: -11%
    ⚠ Underconfident in this range
```

### Automatic Calibration
When scanner processes emails, it automatically applies calibration to LLM results:

```python
# Original AI confidence: 95%
# Historical accuracy at 95% range: 70%
# Calibrated confidence: 82% (adjusted down 50% of error)
```

This appears in logs:
```
→ Analyzing with LLM: sender@domain.com
  Confidence calibrated: 95% → 82%
  Reason: AI tends to be overconfident in this range: 70% actual vs 88% stated
```

## Workflow

1. **Initial Scan** (Day 1-7)
   - Everything goes through LLM (100% usage)
   - System builds decision history
   - No patterns detected yet

2. **Pattern Emergence** (Week 2-4)
   - Sender memory starts detecting patterns
   - ~30-50% of emails handled by patterns
   - LLM usage drops to 50-70%
   - Few-shot learning improves LLM accuracy

3. **Optimization** (Month 2+)
   - Most common senders have patterns
   - Rules refined based on learn_patterns.py suggestions
   - ~70-90% of emails handled by rules/patterns
   - LLM only for truly novel emails
   - Confidence calibration improves trust in AI scores

4. **Maintenance**
   - Run `learn_patterns.py` monthly to find new patterns
   - Review calibration report to track AI accuracy
   - Add suggested rules to config when appropriate

## Statistics Tracking

The system tracks:
- **Rules matched**: Count of emails handled by each rule
- **Patterns used**: Count of emails handled by sender memory
- **LLM calls**: Count of emails requiring AI analysis
- **Accuracy**: Percentage of AI recommendations you approved
- **Calibration error**: How overconfident/underconfident AI is

View stats in the web UI or database.

## Best Practices

1. **Week 1**: Review all decisions carefully to build clean training data
2. **Week 2-4**: Start running `learn_patterns.py` to find opportunities
3. **Monthly**: Review calibration report and add new rules
4. **Ongoing**: Trust patterns for common senders, focus review on LLM decisions

## Benefits

- **Reduced LLM costs**: 70-90% fewer API calls
- **Faster processing**: Rules/patterns are instant vs seconds for LLM
- **Improved accuracy**: Few-shot learning + calibration
- **Consistent decisions**: Same sender always handled same way
- **Transparent logic**: Know why each email was classified (rule/pattern/AI)
