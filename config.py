# config.py
# Vaibhav DDoS Bot Configuration
# Replace with your actual credentials

# Bot Token from @BotFather
BOT_TOKEN = "7984133756:AAExRUlyH8Pyxm3YI143rbiAsAp8OTm3gng"

# Your personal Telegram Chat ID (get it from /start command)
ADMIN_CHAT_ID = 8185900627

# Database settings
DATABASE_PATH = "attack_bot.db"

# Attack limitations (safety measures)
MAX_ATTACK_DURATION = 300  # 5 minutes maximum
MAX_CONCURRENT_ATTACKS = 3

# Bot settings
BOT_USERNAME = "@VAIBHAV_DDOS1_BOT"  # Your bot's username
DEVELOPER = "@VAIBHAV_JAAT_OP"    # Your channel/username

# Webhook settings (if using webhooks instead of polling)
WEBHOOK_URL = ""  # Leave empty for polling mode
WEBHOOK_PORT = 8443

# Logging settings
LOG_LEVEL = "INFO"
LOG_FILE = "bot.log"

# Feature toggles
ENABLE_ANALYTICS = True
ENABLE_USER_LOGGING = True
ENABLE_BROADCAST = True

# Security settings
RATE_LIMIT_PER_USER = 10  # Max attacks per hour per user
AUTO_BACKUP_HOURS = 24    # Auto backup database every 24 hours
