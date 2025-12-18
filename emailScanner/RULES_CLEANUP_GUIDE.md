# Email Scanner - Rules and Cleanup Guide

## Rules Engine

The scanner now has a rules engine that automatically filters emails **before** AI analysis.

### Automatic KEEP Rules

1. **VIP Senders** - Always keep emails from:
   - Catherine Darling (`cdarling926@gmail.com`)
   - Mom (`grace0614@gmail.com`)

2. **Events** - Keeps emails containing event keywords:
   - calendar, meeting, appointment, rsvp, invite, invitation, event, reminder, scheduled, webinar, conference

3. **Personal Contacts** - Heuristic detection of personal emails:
   - From free email providers (gmail, yahoo, hotmail)
   - Short conversational subject lines
   - No promotional content

### Automatic DELETE Rules

1. **Old Job Offers** - Auto-delete job-related emails older than 6 months:
   - Keywords: "job opportunity", "job alert", "career opportunity", "now hiring", etc.
   - Must be 6+ months old

### How Rules Work

1. Scanner fetches email
2. **Rules check first** - if rule matches, skip AI analysis
3. If no rule matches, send to AI for analysis
4. Results stored in database with `model_name='rules_engine'` or actual AI model

### Adding VIP Senders

Edit `src/rules.py` and add to the `VIP_SENDERS` list, or use Python:

```python
from rules import EmailRules
rules = EmailRules()
rules.add_vip_sender('newvip@example.com')
```

---

## Cleanup Script (Batch Deletion)

Two modes of operation:

### Mode 1: Delete Manually Reviewed Emails

After reviewing emails in the web UI and approving deletions:

```powershell
# Dry run (preview what would be deleted)
python src/cleanup.py --dry-run

# Actually delete
python src/cleanup.py
```

This deletes emails where you clicked "Approve" on a delete recommendation.

### Mode 2: Auto-Delete High-Confidence Emails

Skip manual review for emails with high confidence scores:

```powershell
# Preview auto-deletions (confidence >= 0.95)
python src/cleanup.py --auto-delete --dry-run

# Actually auto-delete (confidence >= 0.95)
python src/cleanup.py --auto-delete

# Use different confidence threshold
python src/cleanup.py --auto-delete --min-confidence 0.90
```

**⚠️ Warning**: Auto-delete skips human review! Start with high confidence (0.95+) and use `--dry-run` first.

---

## Complete Workflow

### Workflow 1: Manual Review Everything

1. **Scan emails** (rules pre-filter automatically):
   ```powershell
   python scanner.py --before 2025-01-01 --limit 50
   ```

2. **Review in web UI**:
   ```powershell
   python src/app.py
   # Visit http://localhost:8000/ui
   ```

3. **Approve/reject recommendations** in the UI

4. **Delete approved emails**:
   ```powershell
   python src/cleanup.py --dry-run  # Preview first
   python src/cleanup.py            # Actually delete
   ```

### Workflow 2: Hybrid (Auto-Delete High Confidence)

1. **Scan emails**:
   ```powershell
   python scanner.py --before 2025-01-01 --limit 100
   ```

2. **Auto-delete obvious ones**:
   ```powershell
   python src/cleanup.py --auto-delete --min-confidence 0.95 --dry-run
   python src/cleanup.py --auto-delete --min-confidence 0.95
   ```

3. **Review remaining emails** in web UI

4. **Delete manually approved emails**:
   ```powershell
   python src/cleanup.py
   ```

---

## Safety Features

1. **Dry Run**: Always test with `--dry-run` first
2. **Separation of Concerns**: Scanning and deletion are separate processes
3. **Database Tracking**: All decisions recorded with timestamps
4. **Rules Logging**: See exactly why emails were auto-kept/deleted
5. **Confidence Scores**: Full transparency on AI recommendations

---

## Example Sessions

### Clean up old job offers

```powershell
# Scan old emails
python scanner.py --before 2024-07-01 --limit 200

# Rules engine will automatically mark old job offers for deletion
# Review what was found
python src/app.py

# Auto-delete high confidence recommendations
python src/cleanup.py --auto-delete --min-confidence 0.92 --dry-run
python src/cleanup.py --auto-delete --min-confidence 0.92
```

### Process recent emails carefully

```powershell
# Scan recent emails
python scanner.py --since 2024-12-01 --limit 50

# VIP and event emails auto-flagged as keep
# Review everything in web UI
python src/app.py

# Delete only manually approved ones
python src/cleanup.py --dry-run
python src/cleanup.py
```

---

## Rules Engine Stats

At the end of each scan, you'll see:

```
Rules engine stats: {
  'vip_kept': 5,
  'event_kept': 3,
  'old_job_deleted': 12,
  'personal_kept': 8,
  'auto_deleted': 0
}
```

This shows how many emails were handled by rules vs. AI.
