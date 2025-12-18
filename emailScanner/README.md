# 📧 Email Scanner

An intelligent email management system that uses local AI (Ollama) to analyze emails and recommend which ones can be safely deleted. The system learns from your decisions over time to improve accuracy and eventually automate email cleanup.

## 🎯 Features

- **IMAP Email Integration** - Works with Gmail, Outlook, Yahoo, and other IMAP providers
- **Local AI Analysis** - Uses Ollama for privacy-friendly, cost-free email analysis
- **Rules Engine** - Pre-filters VIP senders, events, personal contacts before AI analysis
- **Smart Recommendations** - AI suggests delete/keep/archive actions with confidence scores
- **Human Review Interface** - Web-based UI to review and approve AI recommendations
- **Batch Deletion** - Safely delete approved emails with dry-run preview
- **Auto-Delete Mode** - Skip review for high-confidence recommendations
- **Learning System** - Tracks your decisions to improve accuracy over time
- **Staged Automation** - Gradually enables auto-deletion as the system proves reliable
- **Database Tracking** - SQLite database stores all emails, analysis, and decisions

## 🏗️ Architecture

### Workflow Stages

1. **Scan & Analyze** - Fetch emails via IMAP, analyze with Ollama, store results
2. **Review** - Human reviews AI recommendations through web interface
3. **Learn** - System tracks approval patterns and builds confidence
4. **Automate** - Once proven reliable, automatically handles obvious cases

### Database Schema

- `emails` - Email metadata and content
- `analysis` - AI recommendations and reasoning
- `decisions` - Human approval/rejection history
- `rules` - Learned patterns for automation
- `system_stats` - Performance metrics

## 📋 Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) installed and running
- Email account with IMAP access enabled
- App-specific password (recommended for Gmail)

## 🚀 Setup

### 1. Install Ollama

Download and install Ollama from [ollama.ai](https://ollama.ai/)

```bash
# Pull a model (choose one)
ollama pull llama3.2
# or
ollama pull mistral
```

### 2. Clone and Install

```bash
cd emailScanner

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure

```bash
# Copy example config
copy config\config.yaml.example config\config.yaml

# Edit config.yaml with your settings
notepad config\config.yaml
```

**Important Settings:**
- `email.address` - Your email address
- `email.password` - App-specific password (see below)
- `email.server` - IMAP server (e.g., imap.gmail.com)
- `ollama.model` - Model name from Ollama

### 4. Gmail Setup (if using Gmail)

1. Enable 2-factor authentication on your Google account
2. Generate an app-specific password:
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Select "2-Step Verification"
   - Scroll to "App passwords"
   - Generate password for "Mail"
3. Use this password in your config file

### 5. Initialize Database

```bash
cd src
python models.py
```

This creates the SQLite database in `data/email_scanner.db`

## 💻 Usage

### 1. Scan Emails

Run the scanner to fetch and analyze emails:

```bash
python scanner.py [options]

# Examples:
python scanner.py --limit 50                    # Scan 50 oldest emails
python scanner.py --since 2024-12-01            # Scan emails since date
python scanner.py --before 2025-01-01           # Scan emails before date
python scanner.py --before 2024-07-01 --limit 200  # Old emails for archival
```

The scanner will:
1. Connect to your email account
2. Apply rules engine (auto-keep VIPs, events, personal contacts)
3. Send remaining emails to AI for analysis
4. Store all results in database

### 2. Review Recommendations

Start the web interface:

```bash
python src/app.py
```

Then open: http://localhost:8000/ui

The interface shows:
- Pending emails requiring review
- AI recommendations with confidence scores
- Email details and reasoning
- Approve/reject buttons
- System statistics

### 3. Delete Approved Emails

After reviewing, delete approved emails:

```bash
# Preview what will be deleted
python src/cleanup.py --dry-run

# Actually delete approved emails
python src/cleanup.py

# Or auto-delete high-confidence recommendations (skip review)
python src/cleanup.py --auto-delete --min-confidence 0.95 --dry-run
python src/cleanup.py --auto-delete --min-confidence 0.95
```

**See [RULES_CLEANUP_GUIDE.md](RULES_CLEANUP_GUIDE.md) for detailed workflows.**

### Make Decisions

For each email:
1. Review the AI recommendation
2. Read the reasoning
3. Click "Approve" if you agree, "Reject" if not
4. The system learns from your decisions

### Automated Workflow

Set up a scheduled task (Windows Task Scheduler or cron) to run the scanner regularly:

**Windows (Task Scheduler):**
```bash
# Run scanner every hour
schtasks /create /tn "EmailScanner" /tr "C:\path\to\venv\Scripts\python.exe C:\path\to\src\scanner.py" /sc hourly
```

**Linux/Mac (cron):**
```bash
# Run scanner every hour
0 * * * * /path/to/venv/bin/python /path/to/src/scanner.py
```

## 📁 Project Structure

```
emailScanner/
├── src/
│   ├── __init__.py
│   ├── models.py              # Database models
│   ├── email_client.py        # IMAP email fetching
│   ├── ollama_analyzer.py     # AI analysis
│   ├── scanner.py             # Main scanner script
│   ├── app.py                 # FastAPI web interface
│   └── settings.py            # Configuration management
├── config/
│   ├── config.yaml.example    # Example configuration
│   └── config.yaml            # Your configuration (create this)
├── data/
│   └── email_scanner.db       # SQLite database (auto-created)
├── tests/
│   └── (test files)
├── requirements.txt
├── .gitignore
└── README.md
```

## 🔧 Configuration Options

### Email Settings

```yaml
email:
  server: "imap.gmail.com"  # IMAP server
  port: 993                  # IMAP SSL port
  address: "your@email.com"  # Your email
  password: "app_password"   # App password
```

### Ollama Settings

```yaml
ollama:
  base_url: "http://localhost:11434"
  model: "llama3.2"  # or "mistral", "llama2", etc.
```

### Scanner Settings

```yaml
scanner:
  limit: 50          # Max emails per scan
  folder: "INBOX"    # Folder to scan
```

### Auto-Delete Settings (Use with Caution!)

```yaml
auto_delete:
  enabled: false              # Enable auto-deletion
  confidence_threshold: 0.95  # Minimum confidence (0.0-1.0)
  min_approvals: 10           # Min manual approvals first
```

## 🎓 How It Works

### AI Analysis

The Ollama analyzer examines each email and provides:

- **Recommendation**: delete, keep, or archive
- **Confidence Score**: 0.0 to 1.0 (how sure the AI is)
- **Reasoning**: Explanation for the recommendation
- **Category**: newsletter, personal, promotional, etc.
- **Priority**: low, medium, high

### Learning Process

1. **Initial Phase**: All recommendations require human review
2. **Learning Phase**: System tracks your approval patterns
3. **Confidence Building**: Calculates accuracy over time
4. **Automation Phase**: Once threshold is met (e.g., 95% accuracy, 10+ approvals), can enable auto-deletion

### Safety Features

- Conservative by default (prefers "keep" when uncertain)
- All actions are logged and reversible
- Auto-deletion requires explicit enablement
- High confidence threshold for automated actions
- Minimum approval count before automation

## 📊 Web API

The FastAPI backend provides these endpoints:

- `GET /api/emails/pending` - List emails needing review
- `GET /api/emails/{id}` - Get email details
- `POST /api/emails/{id}/decide` - Record decision
- `GET /api/emails/history` - View past decisions
- `GET /api/stats` - System statistics

Full API documentation: http://localhost:8000/docs

## 🔍 Troubleshooting

### Cannot connect to Ollama

```bash
# Make sure Ollama is running
ollama serve

# Check if model is available
ollama list
```

### Cannot connect to email server

- Verify IMAP is enabled in your email settings
- Check server address and port
- Ensure you're using an app-specific password
- Try from a trusted network (some providers block unfamiliar IPs)

### Import errors

```bash
# Make sure virtual environment is activated
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## 🛣️ Roadmap

- [ ] Gmail API integration (more reliable than IMAP)
- [ ] Rule-based automation for obvious patterns
- [ ] Email archiving to specific folders
- [ ] Batch operations
- [ ] Email statistics and visualizations
- [ ] Multi-account support
- [ ] Export/import of learned rules

## ⚠️ Important Notes

- **Privacy**: All email data stays local. Ollama runs on your machine.
- **Safety**: Start with `auto_delete: false` and review carefully
- **Backups**: Consider backing up important emails before bulk deletion
- **Testing**: Test with a non-critical email account first
- **Responsibility**: You are responsible for any deleted emails

## 📝 License

MIT License - feel free to modify and use as needed

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Better email parsing
- More sophisticated AI prompts
- Additional email providers
- UI enhancements
- Test coverage

## 💡 Tips

1. Start with a small `scan_limit` (10-20) to test
2. Review AI reasoning to understand its decision-making
3. Build up a history of 20-30 decisions before trusting statistics
4. Consider archiving instead of deleting when uncertain
5. Use filters to focus on specific senders or date ranges

---

**Happy email cleaning! 📧✨**
