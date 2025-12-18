"""
Application settings and configuration management.
Loads configuration from environment variables and config file.
"""
import os
from typing import Optional
from pathlib import Path
import yaml

# Project root directory (parent of src/)
PROJECT_ROOT = Path(__file__).parent.parent


class Settings:
    """Application configuration settings"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Load settings from environment variables and config file
        
        Args:
            config_file: Path to YAML config file (optional)
        """
        # Load from config file if provided
        config_data = {}
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f) or {}
        
        # Database settings
        self.database_url = os.getenv(
            'DATABASE_URL',
            config_data.get('database', {}).get('url', 'sqlite:///data/email_scanner.db')
        )
        
        # Email settings
        email_config = config_data.get('email', {})
        self.email_server = os.getenv('EMAIL_SERVER', email_config.get('server', 'imap.gmail.com'))
        self.email_port = int(os.getenv('EMAIL_PORT', email_config.get('port', 993)))
        self.email_address = os.getenv('EMAIL_ADDRESS', email_config.get('address', ''))
        self.email_password = os.getenv('EMAIL_PASSWORD', email_config.get('password', ''))
        
        # Ollama settings
        ollama_config = config_data.get('ollama', {})
        self.ollama_base_url = os.getenv(
            'OLLAMA_BASE_URL',
            ollama_config.get('base_url', 'http://localhost:11434')
        )
        self.ollama_model = os.getenv(
            'OLLAMA_MODEL',
            ollama_config.get('model', 'llama3.2')
        )
        
        # Scanner settings
        scanner_config = config_data.get('scanner', {})
        self.scan_limit = int(os.getenv(
            'SCAN_LIMIT',
            scanner_config.get('limit', 50)
        ))
        self.scan_folder = os.getenv(
            'SCAN_FOLDER',
            scanner_config.get('folder', 'INBOX')
        )
        
        # Auto-deletion settings
        auto_delete_config = config_data.get('auto_delete', {})
        self.auto_delete_enabled = os.getenv(
            'AUTO_DELETE_ENABLED',
            str(auto_delete_config.get('enabled', False))
        ).lower() == 'true'
        self.auto_delete_confidence_threshold = float(os.getenv(
            'AUTO_DELETE_CONFIDENCE_THRESHOLD',
            auto_delete_config.get('confidence_threshold', 0.95)
        ))
        self.auto_delete_min_approvals = int(os.getenv(
            'AUTO_DELETE_MIN_APPROVALS',
            auto_delete_config.get('min_approvals', 10)
        ))
        
        # Web UI settings
        web_config = config_data.get('web', {})
        self.web_host = os.getenv('WEB_HOST', web_config.get('host', '0.0.0.0'))
        self.web_port = int(os.getenv('WEB_PORT', web_config.get('port', 8000)))
        
        # Rules engine settings
        rules_config = config_data.get('rules', {})
        self.vip_senders = rules_config.get('vip_senders', [])
        self.event_keywords = rules_config.get('event_keywords', [])
        self.job_keywords = rules_config.get('job_keywords', [])
        self.old_event_days = int(rules_config.get('old_event_days', 60))
        self.old_job_days = int(rules_config.get('old_job_days', 180))
        self.newsletter_senders = rules_config.get('newsletter_senders', [])
        self.old_newsletter_days = int(rules_config.get('old_newsletter_days', 7))
        self.promotional_keywords = rules_config.get('promotional_keywords', [])
        self.old_promotional_days = int(rules_config.get('old_promotional_days', 90))
    
    def validate(self) -> bool:
        """
        Validate that required settings are present
        
        Returns:
            True if valid, False otherwise
        """
        errors = []
        
        if not self.email_address:
            errors.append("Email address is required (EMAIL_ADDRESS)")
        
        if not self.email_password:
            errors.append("Email password is required (EMAIL_PASSWORD)")
        
        if errors:
            print("Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    
    def __repr__(self):
        """String representation (hides sensitive data)"""
        return f"""Settings(
    database_url='{self.database_url}',
    email_server='{self.email_server}',
    email_address='{self.email_address}',
    email_password='***',
    ollama_base_url='{self.ollama_base_url}',
    ollama_model='{self.ollama_model}',
    scan_limit={self.scan_limit},
    auto_delete_enabled={self.auto_delete_enabled}
)"""


# Default config file location (relative to project root)
DEFAULT_CONFIG_FILE = PROJECT_ROOT / 'config' / 'config.yaml'


def load_settings(config_file: Optional[str] = None) -> Settings:
    """
    Load settings with automatic config file detection
    
    Args:
        config_file: Optional path to config file
    
    Returns:
        Settings instance
    """
    if config_file is None:
        # Try to find config.yaml in project root
        if DEFAULT_CONFIG_FILE.exists():
            config_file = str(DEFAULT_CONFIG_FILE)
        else:
            print(f"Warning: Config file not found at {DEFAULT_CONFIG_FILE}")
    
    return Settings(config_file)


if __name__ == '__main__':
    # Test settings loading
    settings = load_settings()
    print(settings)
    
    if settings.validate():
        print("\n✓ Configuration is valid")
    else:
        print("\n✗ Configuration is invalid")
