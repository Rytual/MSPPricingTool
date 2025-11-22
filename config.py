"""
Configuration management for MSP Pricing Application
Handles secure storage of credentials and application settings
"""
import os
import sys
import json
from cryptography.fernet import Fernet
from pathlib import Path

# Application settings
APP_NAME = "MSP NCE Pricing Tool"
APP_VERSION = "1.0.0"
DB_NAME = "nce_pricing.db"
PORT = 5000
HOST = "0.0.0.0"  # Network accessible

# Paths - handle PyInstaller frozen executable
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    BASE_DIR = Path(sys.executable).parent.absolute()
else:
    # Running as script
    BASE_DIR = Path(__file__).parent.absolute()

DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
CONFIG_FILE = DATA_DIR / "config.json"
KEY_FILE = DATA_DIR / ".key"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Microsoft Partner Center API settings
AUTHORITY = "https://login.microsoftonline.com"
SCOPE = ["https://api.partnercenter.microsoft.com/user_impersonation"]
PARTNER_CENTER_API = "https://api.partnercenter.microsoft.com/v1"

# Encryption key management
def get_or_create_key():
    """Get existing encryption key or create a new one"""
    if KEY_FILE.exists():
        with open(KEY_FILE, 'rb') as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as f:
            f.write(key)
        return key

ENCRYPTION_KEY = get_or_create_key()
cipher = Fernet(ENCRYPTION_KEY)

def encrypt_data(data: str) -> str:
    """Encrypt sensitive data"""
    return cipher.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    return cipher.decrypt(encrypted_data.encode()).decode()

class Config:
    """Configuration manager with secure storage"""

    def __init__(self):
        self.config_data = self.load_config()

    def load_config(self):
        """Load configuration from file"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {}

    def save_config(self):
        """Save configuration to file"""
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config_data, f, indent=2)

    def get(self, key, default=None):
        """Get configuration value"""
        return self.config_data.get(key, default)

    def set(self, key, value):
        """Set configuration value"""
        self.config_data[key] = value
        self.save_config()

    def get_secure(self, key, default=None):
        """Get encrypted configuration value"""
        encrypted = self.config_data.get(key)
        if encrypted:
            try:
                return decrypt_data(encrypted)
            except:
                return default
        return default

    def set_secure(self, key, value):
        """Set encrypted configuration value"""
        if value:
            encrypted = encrypt_data(value)
            self.config_data[key] = encrypted
            self.save_config()

    # Azure AD / Partner Center credentials
    @property
    def tenant_id(self):
        return self.get('tenant_id')

    @tenant_id.setter
    def tenant_id(self, value):
        self.set('tenant_id', value)

    @property
    def client_id(self):
        return self.get('client_id')

    @client_id.setter
    def client_id(self, value):
        self.set('client_id', value)

    @property
    def client_secret(self):
        return self.get_secure('client_secret')

    @client_secret.setter
    def client_secret(self, value):
        self.set_secure('client_secret', value)

    @property
    def refresh_token(self):
        return self.get_secure('refresh_token')

    @refresh_token.setter
    def refresh_token(self, value):
        self.set_secure('refresh_token', value)

    @property
    def access_token(self):
        return self.get_secure('access_token')

    @access_token.setter
    def access_token(self, value):
        self.set_secure('access_token', value)

    # UI credentials (basic auth)
    @property
    def ui_username(self):
        return self.get('ui_username', 'admin')

    @ui_username.setter
    def ui_username(self, value):
        self.set('ui_username', value)

    @property
    def ui_password(self):
        return self.get_secure('ui_password')

    @ui_password.setter
    def ui_password(self, value):
        self.set_secure('ui_password', value)

    # Update settings
    @property
    def auto_update_enabled(self):
        return self.get('auto_update_enabled', True)

    @auto_update_enabled.setter
    def auto_update_enabled(self, value):
        self.set('auto_update_enabled', value)

    @property
    def update_frequency_days(self):
        return self.get('update_frequency_days', 7)  # Weekly by default

    @update_frequency_days.setter
    def update_frequency_days(self, value):
        self.set('update_frequency_days', value)

    @property
    def last_update(self):
        return self.get('last_update')

    @last_update.setter
    def last_update(self, value):
        self.set('last_update', value)

# Global config instance
config = Config()

# Logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOGS_DIR / 'app.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'standard',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
}
