# Date-Based Decision Making - Implementation Summary

## Overview
The email scanner now fully incorporates email age into decision-making at multiple levels.

## Changes Made

### 1. LLM Prompt Enhancement
**File**: `src/ollama_analyzer.py`

The LLM now receives detailed age information for every email:

```
Email Details:
- From: sender@example.com
- Subject: Holiday Sale!
- Date: 2025-10-15
- Age: 2 months old          ← NEW
- Has attachments: false
- Body preview: ...
```

Age is described in human-friendly terms:
- "Today" or "Yesterday" for very recent
- "X days old" for < 1 week
- "X weeks old" for < 1 month  
- "X months old" for < 1 year
- "X years old" for older

### 2. Age-Based Guidelines in Prompt
The LLM is instructed to consider email age:

**Recent emails (< 7 days)**: Be more conservative, might still be relevant
**Medium age (7-30 days)**: Normal evaluation
**Old emails (30-60 days)**: More aggressive deletion for promotional/newsletter content
**Very old emails (60+ days)**: Very aggressive deletion unless personal/important

Specific guidance:
- Old newsletters (> 7 days) → delete
- Promotional emails older than 30-60 days → delete
- Old transactional emails (receipts, confirmations > 90 days) → delete
- Job offers (old or unsolicited) → delete

### 3. Rules Engine (Already Had Date Logic)
**File**: `src/rules.py`

The rules engine already had sophisticated age-based rules:

#### Rule 1: Old Events
- **Trigger**: Event-related keywords + older than `old_event_days` (60 days)
- **Action**: Delete (even from VIP senders)
- **Reason**: Events older than 2 months are no longer relevant

#### Rule 5: Old Job Offers  
- **Trigger**: Job keywords + older than `old_job_days` (180 days)
- **Action**: Delete
- **Reason**: Job offers older than 6 months are likely filled

#### Rule 6: Old Newsletters
- **Trigger**: Newsletter senders + older than `old_newsletter_days` (7 days)
- **Action**: Delete
- **Reason**: News content is time-sensitive

#### Rule 7: Old Promotional Emails
- **Trigger**: Promotional keywords + older than `old_promotional_days` (**NOW 60 days**)
- **Action**: Delete
- **Reason**: Sales/promotions expire, older ones have no value

### 4. Configuration Update
**File**: `config/config.yaml`

Changed promotional email threshold:
```yaml
old_promotional_days: 60  # Changed from 90 to 60 days
```

This means promotional emails with keywords like "sale", "discount", "% off", "limited time", "deal", etc. will be automatically deleted if they're older than 60 days.

## How It Works

### Decision Flow
1. **Rules Engine First** (instant)
   - Checks if email matches age-based rules
   - Example: "Sale ends soon!" email from 65 days ago → deleted by Rule 7

2. **Sender Memory** (pattern detection)
   - Patterns may include implicit age preferences
   - Example: If you always delete promotional emails from a sender

3. **LLM Analysis** (only if needed)
   - Receives age information and guidelines
   - Makes nuanced decisions considering both content AND age
   - Example: "20% off" from 45 days ago → LLM sees it's old and promotional → delete

### Example Scenarios

#### Scenario 1: Recent Promotional (5 days old)
- Rules: No match (< 60 days)
- LLM receives: "Age: 5 days old"
- LLM decision: Might keep if interesting sale, considers recency

#### Scenario 2: Old Promotional (70 days old)
- Rules: **MATCHED** - Rule 7 (old promotional)
- Action: Deleted immediately (confidence: 94%)
- Reason: "Old promotional/sale email (older than 60 days)"
- LLM: Never called (saved API cost)

#### Scenario 3: Medium Age Promotional (35 days old)
- Rules: No match (< 60 days)
- LLM receives: "Age: 1 month old"
- LLM sees guideline: "Old emails (30-60 days): More aggressive deletion for promotional content"
- LLM decision: Likely delete (sale expired, not relevant)

#### Scenario 4: Old Personal Email (80 days old)
- Rules: No match (no promotional keywords)
- LLM receives: "Age: 2 months old"
- LLM sees guideline: "Very old emails (60+ days): Very aggressive deletion unless personal/important"
- LLM decision: Keep (personal correspondence stays valuable)

#### Scenario 5: Old Receipt (120 days old)
- Rules: Might match promotional keywords if contains "discount"
- LLM receives: "Age: 4 months old"
- LLM sees guideline: "Old transactional emails (receipts, confirmations older than 90 days)"
- LLM decision: Delete (already filed/processed)

## Configuration Options

You can adjust these thresholds in `config/config.yaml`:

```yaml
rules:
  old_event_days: 60          # Events older than this → delete
  old_job_days: 180           # Job offers older than this → delete
  old_newsletter_days: 7      # Newsletters older than this → delete
  old_promotional_days: 60    # Promotional emails older than this → delete
```

**Recommendations**:
- **Aggressive cleanup**: Reduce promotional to 30 days, newsletters to 3 days
- **Conservative**: Increase promotional to 90 days, keep others as-is
- **Balanced** (current): 60 days promotional, 7 days newsletters

## Benefits

1. **Automatic Age-Based Deletion**: Promotional emails older than 60 days are automatically removed
2. **Context-Aware AI**: LLM sees age and adjusts recommendations accordingly
3. **Configurable Thresholds**: Easy to tune for your preferences
4. **Efficient**: Rules catch most old emails before expensive LLM call
5. **Consistent**: Same age logic across rules and AI analysis

## Testing

To see it in action:
```bash
cd src
python scanner.py --limit 50
```

Watch the logs for:
- `✓ Rule matched: old_promotional` - caught by rules
- `→ Analyzing with LLM` - AI receives age information
- Check reasoning includes age mentions like "2 months old, likely expired"

## Stats

After next scan, check rule stats:
```python
from rules import EmailRules
rules.get_stats()
# {'old_promotional_deleted': 150, 'old_newsletter_deleted': 200, ...}
```

This shows how many emails were automatically deleted by each age-based rule.
