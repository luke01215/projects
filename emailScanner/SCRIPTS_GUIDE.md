# Email Scanner - Scripts Guide

Complete reference for all scripts in the email scanner system.

---

## 📋 Main Scripts

### 1. `scanner.py` - Email Analysis

**Purpose**: Fetch and analyze emails using AI and rules engine

**Usage**:
```powershell
python scanner.py [options]

# Examples:
python scanner.py --limit 50                          # Scan 50 oldest emails
python scanner.py --since 2024-12-01                  # Emails since date
python scanner.py --before 2025-01-01                 # Emails before date
python scanner.py --before 2024-07-01 --limit 200     # Old emails for archival
python scanner.py --newest-first --limit 10           # Process newest first
python scanner.py --folder "INBOX" --limit 100        # Specific folder
```

**Options**:
- `--limit N` - Maximum number of emails to process
- `--since YYYY-MM-DD` - Only emails since this date
- `--before YYYY-MM-DD` - Only emails before this date
- `--oldest-first` - Process oldest emails first (default)
- `--newest-first` - Process newest emails first
- `--folder NAME` - Email folder to scan (default: INBOX)
- `--days N` - Shortcut for emails from last N days

**What it does**:
1. Connects to email server via IMAP
2. Applies rules engine (VIP senders, events, etc.)
3. Sends remaining emails to AI for analysis
4. Stores everything in database
5. Shows progress: `[5/50] Processing: sender@example.com - Subject...`

**Safe to re-run**: Yes! Skips already-analyzed emails automatically.

---

### 2. `app.py` - Web Review Interface

**Purpose**: Web UI for reviewing AI recommendations and making decisions

**Usage**:
```powershell
python src/app.py
```

**Access**: http://localhost:8000/ui

**Features**:
- View all pending emails
- See AI recommendations with confidence scores
- Read email content and reasoning
- Approve/reject recommendations
- View system statistics
- Track accuracy over time

**API Endpoints**:
- `GET /api/emails/pending` - List pending reviews
- `POST /api/emails/{id}/decide` - Record decision
- `GET /api/stats` - System statistics

---

### 3. `cleanup.py` - Email Deletion

**Purpose**: Actually delete emails from server after review

**Usage**:
```powershell
# Mode 1: Delete manually approved emails
python src/cleanup.py --dry-run           # Preview what will be deleted
python src/cleanup.py                     # Actually delete

# Mode 2: Auto-delete high-confidence (skip manual review)
python src/cleanup.py --auto-delete --min-confidence 0.95 --dry-run
python src/cleanup.py --auto-delete --min-confidence 0.95

# Custom confidence threshold
python src/cleanup.py --auto-delete --min-confidence 0.90
```

**Options**:
- `--dry-run` - Show what would be deleted without deleting
- `--auto-delete` - Skip manual review for high-confidence emails
- `--min-confidence X` - Minimum confidence for auto-delete (0.0-1.0, default: 0.95)

**What it does**:
- Finds emails you approved for deletion
- Deletes from email server (goes to Trash in Gmail)
- Marks as deleted in database
- Updates statistics

**Safety**: Always use `--dry-run` first!

---

## 🛠️ Utility Scripts

### 4. `models.py` - Database Schema

**Purpose**: Database models and schema definition

**Usage**:
```powershell
python src/models.py    # Initialize/verify database
```

**Tables**:
- `emails` - Email metadata and content
- `analysis` - AI recommendations and reasoning
- `decisions` - Human approval/rejection history
- `rules` - Learned patterns (future use)
- `system_stats` - Performance metrics

---

### 5. `settings.py` - Configuration

**Purpose**: Load and validate configuration from config.yaml

**Usage**:
```powershell
python src/settings.py    # Test configuration
```

**Validates**:
- Email credentials
- Ollama connection
- Database path
- All required settings

---

### 6. `migrate_add_deleted_at.py` - Database Migration

**Purpose**: Add missing database columns (one-time fix)

**Usage**:
```powershell
python migrate_add_deleted_at.py
```

**What it does**:
- Adds `deleted_at` column to emails table
- Safe to run multiple times (checks if already exists)

---

## 📚 Supporting Modules

### `email_client.py`
IMAP client for connecting to email servers and fetching/deleting emails.

### `ollama_analyzer.py`
AI integration for analyzing email content and making recommendations.

### `rules.py`
Rules engine for pre-filtering emails before AI analysis.

---

## 🔄 Complete Workflows

### Workflow 1: Manual Review Everything

```powershell
# 1. Scan emails
python scanner.py --before 2025-01-01 --limit 50

# 2. Review in web UI
python src/app.py
# Visit http://localhost:8000/ui

# 3. Preview deletions
python src/cleanup.py --dry-run

# 4. Delete approved emails
python src/cleanup.py
```

### Workflow 2: Hybrid (Auto-Delete High Confidence)

```powershell
# 1. Scan emails
python scanner.py --before 2024-07-01 --limit 200

# 2. Auto-delete obvious ones
python src/cleanup.py --auto-delete --min-confidence 0.95 --dry-run
python src/cleanup.py --auto-delete --min-confidence 0.95

# 3. Review remaining in web UI
python src/app.py

# 4. Delete manually approved
python src/cleanup.py
```

### Workflow 3: Archive Old Emails Systematically

```powershell
# Process in batches, oldest first
python scanner.py --before 2024-01-01 --limit 100
python src/app.py  # Review batch 1
python src/cleanup.py

python scanner.py --before 2024-01-01 --limit 100
python src/app.py  # Review batch 2
python src/cleanup.py

# Continue until done...
```

---

## 🎯 Quick Reference

### Daily Use
```powershell
python scanner.py --days 1                    # Today's emails
python src/app.py                             # Review
python src/cleanup.py --dry-run && python src/cleanup.py
```

### Archive Old Emails
```powershell
python scanner.py --before 2024-06-01 --limit 200
python src/app.py
python src/cleanup.py --auto-delete --min-confidence 0.95
```

### Check What's Pending
```powershell
python src/app.py
# Visit http://localhost:8000/api/stats
```

### Emergency: Stop Everything
- Press `Ctrl+C` in scanner (progress is saved)
- All analyzed emails are already in database
- Safe to restart anytime

---

## 🔧 Configuration

All scripts read from: `config/config.yaml`

Key settings:
- `email.*` - IMAP credentials
- `ollama.*` - AI model settings
- `scanner.*` - Default limits and folders
- `rules.*` - VIP senders, keywords
- `auto_delete.*` - Safety thresholds

Edit config.yaml to customize behavior without code changes.

---

## 📊 Monitoring

### View Stats
```powershell
python src/app.py
# Visit http://localhost:8000/api/stats
```

Returns:
- Total emails processed
- Emails deleted/kept
- AI accuracy rate
- Pending reviews
- Last scan time

### Database Query
```powershell
sqlite3 data/email_scanner.db
> SELECT COUNT(*) FROM emails;
> SELECT COUNT(*) FROM analysis WHERE status='pending_review';
> SELECT * FROM system_stats;
```

---

## 🚨 Troubleshooting

### "Ollama timeout"
- Check if Ollama is running: `ollama list`
- Use smaller model in config.yaml: `gemma2:2b`
- Scanner saves progress - safe to restart

### "Database locked"
- Close other connections to database
- Only one script should write at a time
- Web UI (read-only) is fine to run alongside scanner

### "IMAP connection failed"
- Check credentials in config.yaml
- Verify app-specific password (Gmail)
- Check IMAP is enabled in email settings

### "Already processed"
- This is normal! Scanner skips duplicates
- Shows: `Skipped N already-processed emails`

---

## 💡 Tips

1. **Always dry-run cleanup first**: `--dry-run`
2. **Start with small batches**: `--limit 50`
3. **Use oldest-first for archival**: Default behavior
4. **Monitor progress**: Scanner shows real-time progress
5. **Gmail safety net**: Deleted emails go to Trash (30-day recovery)
6. **Rules save time**: Configure VIPs in config.yaml
7. **High confidence = safe**: 0.95+ confidence is very reliable

---

## 📖 See Also

- [README.md](README.md) - General overview and setup
- [RULES_CLEANUP_GUIDE.md](RULES_CLEANUP_GUIDE.md) - Detailed rules and cleanup workflows
- [config/config.yaml](config/config.yaml) - Configuration file
