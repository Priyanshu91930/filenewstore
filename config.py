# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190


import re
import os
from os import environ
from Script import script

id_pattern = re.compile(r'^.\d+$')
def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default
      
# Bot Information
API_ID = int(environ.get("API_ID", "27686895"))
API_HASH = environ.get("API_HASH", "0e996bd3891969ec5dfebf8bb3e39e94")
BOT_TOKEN = environ.get("BOT_TOKEN", "8456336413:AAFArfdOHON1b2FbABTbV-ncetvwFsUM_Jc")

PICS = (environ.get('PICS', 'https://graph.org/file/6a869326b7756a622bd48-6213fc97b75f7bfb30.jpg')).split() # Bot Start Picture
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '1246987713').split()]
BOT_USERNAME = environ.get("BOT_USERNAME", "filesstoreclone_bot") # without @
PORT = environ.get("PORT", "8080")

# Clone Info :-
CLONE_MODE = is_enabled(environ.get('CLONE_MODE', 'True'), True) # Set True or False

# If Clone Mode Is True Then Fill All Required Variable, If False Then Don't Fill.
CLONE_DB_URI = environ.get("CLONE_DB_URI", "mongodb+srv://anihubyt:Zxcvbnmm9193@cluster0.qv5tu12.mongodb.net/?appName=Cluster0")
CDB_NAME = environ.get("CDB_NAME", "clonetechbrain")

# Database Information
DB_URI = environ.get("DB_URI", "mongodb+srv://anihubyt:Zxcvbnmm9193@cluster0.qv5tu12.mongodb.net/?appName=Cluster0")
DB_NAME = environ.get("DB_NAME", "brainaxe")

# Auto Delete Information
AUTO_DELETE_MODE = is_enabled(environ.get('AUTO_DELETE_MODE', 'True'), True) # Set True or False

# If Auto Delete Mode Is True Then Fill All Required Variable, If False Then Don't Fill.
AUTO_DELETE = int(environ.get("AUTO_DELETE", "30")) # Time in Minutes
AUTO_DELETE_TIME = int(environ.get("AUTO_DELETE_TIME", "1800")) # Time in Seconds

# Channel Information
LOG_CHANNEL = int(environ.get("LOG_CHANNEL", "-1003591540042"))
FORCE_SUB_CHANNELS = [int(ch) for ch in environ.get("FORCE_SUB_CHANNELS", "").split()]
UNIVERSAL_FORCE_SUB_CHANNEL = int(environ.get("UNIVERSAL_FORCE_SUB_CHANNEL", "-1003632363697")) # This channel will be forced for all clones

# File Caption Information
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", "")
BATCH_FILE_CAPTION = environ.get("BATCH_FILE_CAPTION", CUSTOM_FILE_CAPTION)

# Enable - True or Disable - False
PUBLIC_FILE_STORE = is_enabled(environ.get('PUBLIC_FILE_STORE', "True"), True)

# Verify Info :-
VERIFY_MODE = is_enabled(environ.get('VERIFY_MODE', 'False'), False) # Set True or False

# If Verify Mode Is True Then Fill All Required Variable, If False Then Don't Fill.
SHORTLINK_URL = environ.get("SHORTLINK_URL", "vplink.in") # shortlink domain without https://
SHORTLINK_API = environ.get("SHORTLINK_API", "35591ad98834a002e1fe0b3b4acc6d84ef401782") # shortlink api
SECONDARY_SHORTLINK_URL = environ.get("SECONDARY_SHORTLINK_URL", "arolinks.com") # 2nd shortlink domain
SECONDARY_SHORTLINK_API = environ.get("SECONDARY_SHORTLINK_API", "3c18358955e8a22e6f76145366e0102a0ba2b9c0") # 2nd shortlink api
TERTIARY_SHORTLINK_URL = environ.get("TERTIARY_SHORTLINK_URL", "alpha-links.in") # 3rd shortlink domain
TERTIARY_SHORTLINK_API = environ.get("TERTIARY_SHORTLINK_API", "") # 3rd shortlink api (initially empty)
VERIFY_TUTORIAL = environ.get("VERIFY_TUTORIAL", "") # how to open link 


# Telegram Mini App (TMA) + Monetag Integration
# Set TMA_MODE to True to use Monetag Mini App ads instead of shortlinks for file verification
TMA_MODE = is_enabled(environ.get('TMA_MODE', 'True'), True)  # Set True or False

# If TMA_MODE Is True Then Fill All Required Variables.
# Get your Zone ID from https://monetag.com after registering and adding a Telegram Mini App property.
MONETAG_ZONE_ID = environ.get("MONETAG_ZONE_ID", "")  # Your Monetag Ad Zone ID (7-digit number)

# Secret key used to sign TMA verification tokens (change this to something random!)
TMA_SECRET_KEY = environ.get("TMA_SECRET_KEY", "tma-secret-key-change-this!")

# TMA Verification validity window in seconds (default 10800 = 3 hours)
# Change this to 3600 for 1 hour, 7200 for 2 hours, etc.
TMA_TIMEOUT = int(environ.get("TMA_TIMEOUT", "10800"))

# Website Info:
WEBSITE_URL_MODE = is_enabled(environ.get('WEBSITE_URL_MODE', 'False'), False) # Set True or False

# If Website Url Mode Is True Then Fill All Required Variable, If False Then Don't Fill.
WEBSITE_URL = environ.get("WEBSITE_URL", "") # For More Information Check Video On Yt - @Tech_VJ

# File Stream Config
STREAM_MODE = is_enabled(environ.get('STREAM_MODE', 'False'), False) # Set True or False

# If Stream Mode Is True Then Fill All Required Variable, If False Then Don't Fill.
MULTI_CLIENT = False
SLEEP_THRESHOLD = int(environ.get('SLEEP_THRESHOLD', '60'))
PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))  # 20 minutes
if 'DYNO' in environ:
    ON_HEROKU = True
else:
    ON_HEROKU = False
URL = environ.get("URL", "https://miniapp.anihubyt.com/")


# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190
    
