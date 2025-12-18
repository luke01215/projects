# Email Scanner - Usage Guide

## Script Reference

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `scanner.py` | Analyze new emails | Daily/weekly to process inbox |
| `app.py` | Web UI for review | Review and approve AI decisions |
| `cleanup.py` | Delete approved emails | After reviewing in web UI |
| `learn_patterns.py` | Find rule suggestions | Monthly to improve automation |
| `confidence_calibration.py` | AI accuracy report | Check AI performance quality |
| `sync_status.py` | Sync database with Gmail | Weekly/monthly maintenance |
| `rescan_email.py` | Re-analyze specific email | Debug or test updated rules |

---

## Quick Start

### Daily Workflow

1. **Scan emails** - Analyze new emails using rules, patterns, and AI
2. **Review decisions** - Check AI recommendations in web interface
3. **Cleanup** - Delete approved emails (moves to Gmail Trash for 30-day recovery)

### Basic Commands

```bash
# Navigate to project
cd G:\GIT\projects\emailScanner\src

# Step 1: Scan emails
python scanner.py --limit 100

# Step 2: Review in web interface
python app.py
# Open http://localhost:8000/ui in browser

# Step 3: Delete approved emails
python cleanup.py
```

---

## Main Scripts

### 1. `scanner.py` - Email Analysis

Fetches emails from IMAP and analyzes them using the three-tier system.

**Basic usage:**
```bash
python scanner.py --limit 100
```

**Options:**
- `--limit N` - Process up to N emails (default: 50)
- `--rescan` - Re-analyze previously scanned emails

**What it does:**
1. Connects to your IMAP server (Gmail)
2. Fetches unprocessed emails
3. Applies three-tier classification:
   - **TIER 1**: Rules engine (instant, free)
   - **TIER 2**: Sender memory patterns (instant, free)
   - **TIER 3**: LLM analysis (slow, uses API)
4. Stores recommendations in database

**Expected output:**
```
INFO - Scanning INBOX for new emails...
INFO - Found 45 emails to process
INFO - ✓ Rule matched: old_promotional (email from Amazon, 65 days old)
INFO - ✓ Pattern detected for newsletters@company.com: delete
INFO - → Analyzing with LLM: unknown-sender@example.com
INFO - Successfully processed 45 emails
INFO - Rules caught: 25, Patterns: 12, LLM: 8
```

**When to run:**
- Daily for regular cleanup
- After vacation to catch up on backlog
- Before important events to clear inbox

---

### 2. `app.py` - Web Interface

Starts a web server for reviewing and managing email decisions.

**Usage:**
```bash
python app.py
```

Then open: http://localhost:8000/ui

**Features:**
- View emails by sender, category, or date range
- Bulk approve/reject recommendations
- See AI confidence scores
- Override AI decisions
- Track approval accuracy

**Interface sections:**
- **Senders** - Group by email sender
- **Categories** - Group by type (promotional, newsletter, job, etc.)
- **Date Ranges** - Group by received date
- **Individual** - Review one by one

**Tips:**
- Use bulk actions for consistent senders (approve all from specific sender)
- Check low-confidence emails carefully
- Override when AI is wrong - this improves learning

---

### 3. `cleanup.py` - Email Deletion

Executes approved deletions by moving emails to Gmail Trash.

**Usage:**
```bash
python cleanup.py
```

**What it does:**
1. Finds emails marked for deletion with human approval
2. Connects to IMAP
3. Moves emails to [Gmail]/Trash using UID commands
4. Updates database status to 'deleted'

**Safety features:**
- Only deletes emails you explicitly approved
- Moves to Trash (30-day recovery window), not permanent deletion
- Uses persistent UIDs (works even if you delete other emails first)
- Requires INBOX selection before deletion

**Output:**
```
INFO - Found 47 approved deletions
INFO - Processing batch of 47 emails
INFO - Successfully deleted 47 emails
```

**Recovery:**
If you accidentally approved wrong emails, go to Gmail Trash within 30 days and restore them.

---

## Analysis Scripts

### 4. `learn_patterns.py` - Pattern Discovery

Analyzes your decision history and suggests automatic rules.

**Usage:**
```bash
python learn_patterns.py
```

**What it analyzes:**
- **Sender patterns**: 10+ decisions, 90% consistency
- **Domain patterns**: 8+ decisions, 90% consistency
- **Category patterns**: 15+ decisions, 85% consistency

**Output example:**
```
=== Email Pattern Learning ===

1. Sender Patterns:
   ✓ Auto-delete emails from 'newsletters@company.com' (45 decisions, 98% deleted)
   ✓ Add 'friend@personal.com' to VIP senders list (12 decisions, 100% kept)

2. Domain Patterns:
   ✓ Auto-delete all emails from domain '@spammer.net' (10 decisions, 100% deleted)

3. Category Patterns:
   ✓ Auto-delete category 'job_offer' emails (250 decisions, 99% deleted)

Found 15 rule suggestions!

Next steps:
1. Review suggestions above
2. Add appropriate rules to config/config.yaml
3. Rules will be applied automatically on next scan
```

**How to use suggestions:**
1. Review the list - make sure patterns make sense
2. Edit `config/config.yaml`:
   ```yaml
   vip_senders:
     - "friend@personal.com"  # Add VIP suggestions here
   ```
3. Next scan will apply new rules automatically

**When to run:**
- After first 50-100 decisions
- Monthly to discover new patterns
- When you notice repetitive manual decisions

---

### 5. `confidence_calibration.py` - AI Accuracy Report

Shows how accurate the AI is at different confidence levels.

**Usage:**
```bash
python confidence_calibration.py
```

**Output example:**
```
=== AI Confidence Calibration Report ===

Overall Performance:
  Total Decisions: 500
  Accuracy: 94.7%
  Avg Confidence: 92.9%
  Calibration Error: -1.8%
  ✓ AI is well-calibrated

Performance by Confidence Level:

  85%-95% confidence (high):
    Samples: 250
    Actual Accuracy: 92.3%
    Avg Stated Confidence: 91.8%
    Calibration Error: -0.5%
    ✓ Well-calibrated

  95%-100% confidence (very_high):
    Samples: 150
    Actual Accuracy: 99.1%
    Avg Stated Confidence: 98.8%
    Calibration Error: -0.3%
    ✓ Well-calibrated
```

**What it means:**
- **Calibration Error**: How far off AI confidence is from reality
  - Negative: AI is underconfident (it's better than it thinks)
  - Positive: AI is overconfident (it's worse than it thinks)
- **Accuracy**: How often AI recommendation matches your decision
- **Well-calibrated**: When AI says 90% confident, it's right 90% of the time

**When to run:**
- After 100+ decisions to check initial accuracy
- Monthly to track improvement
- When you notice AI seems consistently wrong

**System automatically applies calibration** during scanning to adjust confidence scores based on historical accuracy.

---

### 6. `sync_status.py` - Database Sync with Gmail

Synchronizes your database with Gmail's actual state (bidirectional).

**Usage:**
```bash
# Show database statistics only
python sync_status.py --stats

# Sync database with Gmail (bidirectional)
python sync_status.py --sync

# Cleanup old deleted emails from database
python sync_status.py --sync --cleanup-old 30
```

**What it does:**
- **Direction 1** (Inbox → Deleted): Marks emails in database as deleted if they no longer exist in Gmail INBOX
- **Direction 2** (Deleted → Inbox): Restores emails to pending review if they came back to INBOX (e.g., moved from trash)
- **Cleanup**: Optionally removes old deleted emails from database to keep it lean

**Output example:**
```
Sync Summary:
  Active emails checked: 1250
  Missing on server: 45
    → Marked as deleted: 45
  Deleted emails checked: 320
  Restored to inbox: 3
  Errors: 0
```

**When to run:**
- Weekly or monthly to keep database in sync
- After manually deleting/moving emails in Gmail
- Before running analytics to ensure accurate data

**Important notes:**
- Only syncs INBOX folder
- Read-only on Gmail side (never modifies Gmail)
- Safe to run anytime

---

### 7. `rescan_email.py` - Re-analyze Specific Emails

Re-analyzes a specific email with current rules and AI model.

**Usage:**
```bash
# Re-scan by email UID
python rescan_email.py --email-id 12345

# Re-scan by database ID
python rescan_email.py --db-id 678
```

**What it does:**
1. Fetches email from database (or re-fetches from Gmail)
2. Applies current rules, patterns, and AI analysis
3. Updates analysis with new recommendation
4. Preserves your original decision if you already reviewed it

**When to use:**
- After updating rules in config.yaml
- After model improvements
- To see why AI made a specific recommendation
- Debugging edge cases

**Example:**
```bash
python rescan_email.py --email-id 12345
# Shows: Old recommendation → New recommendation
# Reasoning updated with current logic
```

---

## Configuration

### Edit `config/config.yaml`

**Email settings:**
```yaml
email:
  server: "imap.gmail.com"
  address: "your-email@gmail.com"
  password: "your-app-password"
```

**Rules thresholds:**
```yaml
rules:
  old_event_days: 60          # Delete events older than 60 days
  old_job_days: 180           # Delete job offers older than 180 days
  old_newsletter_days: 7      # Delete newsletters older than 7 days
  old_promotional_days: 60    # Delete promotional emails older than 60 days
```

**Adjust for your preferences:**
- **Aggressive cleanup**: Lower numbers (promotional: 30, newsletter: 3)
- **Conservative**: Higher numbers (promotional: 90, newsletter: 14)
- **Balanced** (current): promotional: 60, newsletter: 7

**VIP senders:**
```yaml
rules:
  vip_senders:
    - "important@person.com"
    - "boss@company.com"
```
Emails from VIP senders are always kept.

**Scanner limits:**
```yaml
scanner:
  limit: 8000  # Maximum emails per scan
```

---

## Typical Usage Patterns

### Daily User (10 minutes/day)
```bash
# Morning: Scan overnight emails
python scanner.py --limit 50

# Review in browser
python app.py
# Approve/reject in UI

# Cleanup
python cleanup.py
```

### Weekly User (30 minutes/week)
```bash
# Weekend: Process week's emails
python scanner.py --limit 300

# Review in batches
python app.py
# Bulk approve by sender

# Cleanup
python cleanup.py

# Check patterns
python learn_patterns.py
# Add new rules if suggested
```

### Monthly Maintenance
```bash
# Process any backlog
python scanner.py --limit 1000

# Check learning progress
python learn_patterns.py
python confidence_calibration.py

# Review and update config.yaml with new rules
# Adjust age thresholds if needed
```

---

## Understanding the Output

### Scanner Logs

**✓ Symbol** - Rule or pattern matched (no LLM call):
```
✓ Rule matched: old_promotional
✓ Pattern detected for sender@example.com: delete
```

**→ Symbol** - LLM analysis required:
```
→ Analyzing with LLM: unknown@example.com
  Confidence calibrated: 95% → 82%
  Reason: AI tends to be overconfident in this range
```

**Statistics at end:**
```
Rules caught: 125    # Instant decisions by rules engine
Patterns: 45         # Instant decisions by sender memory
LLM calls: 30        # Required AI analysis
```

**Goal**: Over time, rules + patterns should handle 70-90% of emails, minimizing expensive LLM calls.

### Web Interface

**Confidence colors:**
- 🟢 Green (>85%): High confidence, likely correct
- 🟡 Yellow (70-85%): Medium confidence, review carefully
- 🔴 Red (<70%): Low confidence, definitely review

**Categories:**
- `promotional` - Sales, marketing, deals
- `newsletter` - News, digests, updates
- `job_offer` - Recruiters, job postings
- `notification` - Automated alerts, receipts
- `personal` - Real people, friends, family
- `spam` - Obvious junk
- `important` - High-value content

---

## Troubleshooting

### "Cannot connect to Ollama"
```bash
# Check if Ollama is running
ollama list

# Start Ollama if needed
ollama serve

# Test connection
curl http://localhost:11434/api/tags
```

### "Cannot connect to email server"
- Check credentials in `config.yaml`
- For Gmail, use App Password (not regular password)
- Verify IMAP is enabled in Gmail settings

### "No emails to process"
- Already scanned recent emails
- Use `--rescan` to re-analyze existing emails
- Check scanner limit (might need higher limit)

### "Database locked"
- Close other scripts accessing database
- Only run one script at a time
- Web server can run alongside others (read-only)

---

## Performance Tips

1. **Start small**: Use `--limit 50` initially, increase once patterns emerge
2. **Bulk approve**: In web UI, approve all from consistent senders at once
3. **Add patterns**: Run `learn_patterns.py` regularly and add suggestions to config
4. **Check calibration**: If AI seems consistently wrong, run calibration report
5. **Adjust thresholds**: Tune age thresholds in config.yaml to your preferences

---

## Data Safety

- **No permanent deletion**: Emails go to Gmail Trash (30-day recovery)
- **UID-based**: Uses persistent identifiers, safe even if inbox changes
- **Manual approval required**: Nothing deleted without your explicit approval
- **Database backup**: Located at `data/email_scanner.db`, backup regularly
- **Reversible**: Can restore from Trash anytime within 30 days

---

## Getting Help

- Check `docs/LEARNING_SYSTEM.md` for details on progressive learning
- Check `docs/DATE_BASED_DECISIONS.md` for age-based decision logic
- Review logs in terminal for detailed error messages
- Database is SQLite, can inspect with: `sqlite3 data/email_scanner.db`
