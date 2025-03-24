from os import getenv

API_ID = int(getenv("API_ID", "22642292"))
API_HASH = getenv("API_HASH", "4502d35191a2fcb02c8467f54789f0ea")
BOT_TOKEN = getenv("BOT_TOKEN", "8048330196:AAHQSSa8IijT0HfzOEIk40pD5nX1NNU2eas")  # Replace with your actual bot token from @BotFather
OWNER_ID = list(map(int, getenv("OWNER_ID", "922270982").split()))
MONGO_DB = getenv("MONGO_DB", "mongodb://localhost:27017/telegram_bot")
LOG_GROUP = getenv("LOG_GROUP", "-1002493565037")
CHANNEL_ID = int(getenv("CHANNEL_ID", "-1002329264016"))
FREEMIUM_LIMIT = int(getenv("FREEMIUM_LIMIT", "20"))
PREMIUM_LIMIT = int(getenv("PREMIUM_LIMIT", "500000000000000000"))
WEBSITE_URL = getenv("WEBSITE_URL", None)
AD_API = getenv("AD_API", None)
STRING = getenv("STRING", None)
YT_COOKIES = getenv("YT_COOKIES", None)
INSTA_COOKIES = getenv("INSTA_COOKIES", None)
SECONDS = 300  # for example, a 5-minute delay
