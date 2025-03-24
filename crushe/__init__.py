#crushe
import asyncio
import logging
import time
from pyromod import listen
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN, STRING, MONGO_DB
from telethon.sync import TelegramClient
from motor.motor_asyncio import AsyncIOMotorClient

loop = asyncio.get_event_loop()
logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.INFO,
)

# Initialize Telegram clients with improved connection handling
async def setup_telegram_client(max_retries=3, retry_delay=5):
    clients = []
    try:
        app = Client(
            name="crushe/sessions/RestrictBot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=10,
            no_updates=True
        )
        clients.append(app)
        
        if STRING:
            pro = Client(
                name="crushe/sessions/ggbot",
                api_id=API_ID,
                api_hash=API_HASH,
                session_string=STRING,

                no_updates=True
            )
            clients.append(pro)
        else:
            pro = None

        sex = await TelegramClient(
            'crushe/sessions/sexrepo',
            API_ID,
            API_HASH,
            connection_retries=max_retries,
            retry_delay=retry_delay,
            auto_reconnect=True
        ).start(bot_token=BOT_TOKEN)
        clients.append(sex)

        return app, pro, sex

    except Exception as e:
        # Clean up any successfully created clients before re-raising
        for client in clients:
            try:
                if isinstance(client, Client):
                    await client.stop()
                elif isinstance(client, TelegramClient):
                    await client.disconnect()
            except Exception:
                pass
        logging.error(f"Failed to setup Telegram clients: {str(e)}")
        raise

botStartTime = time.time()
app, pro, sex = loop.run_until_complete(setup_telegram_client())


# MongoDB setup with enhanced connection handling and pooling
async def setup_mongodb_connection(max_retries=3, retry_delay=5, max_pool_size=50):
    last_error = None
    for attempt in range(max_retries):
        try:
            # Configure MongoDB client with connection pooling and timeouts
            tclient = AsyncIOMotorClient(
                MONGO_DB,
                serverSelectionTimeoutMS=5000,
                maxPoolSize=max_pool_size,
                connectTimeoutMS=5000,
                socketTimeoutMS=10000,
                waitQueueTimeoutMS=5000,
                retryWrites=True
            )
            
            # Verify connection and ping server
            await tclient.admin.command('ping')
            await tclient.server_info()
            
            logging.info(f"Successfully connected to MongoDB (Pool Size: {max_pool_size})")
            return tclient
            
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                wait_time = retry_delay * (attempt + 1)  # Exponential backoff
                logging.warning(
                    f"MongoDB connection attempt {attempt + 1} failed: {str(e)}. "
                    f"Retrying in {wait_time} seconds..."
                )
                await asyncio.sleep(wait_time)
            else:
                logging.error(
                    f"Failed to connect to MongoDB after {max_retries} attempts. "
                    f"Last error: {str(last_error)}"
                )
                raise last_error

async def create_ttl_index(token_collection):
    """Ensure the TTL index exists for the `tokens` collection."""
    try:
        await token_collection.create_index("expires_at", expireAfterSeconds=0)
        logging.info("MongoDB TTL index created successfully")
    except Exception as e:
        logging.error(f"Failed to create TTL index: {str(e)}")
        raise

# Initialize database connection and setup
async def setup_database():
    tclient = await setup_mongodb_connection()
    tdb = tclient["telegram_bot"]
    token_collection = tdb["tokens"]
    await create_ttl_index(token_collection)
    return token_collection

async def restrict_bot():
    global BOT_ID, BOT_NAME, BOT_USERNAME
    clients_started = []
    try:
        # Setup database first
        await setup_database()
        logging.info("Database setup completed")
        
        # Start bot client
        await app.start()
        clients_started.append(app)
        logging.info("Bot client started successfully")
        
        # Get bot info
        getme = await app.get_me()
        BOT_ID = getme.id
        BOT_USERNAME = getme.username
        BOT_NAME = f"{getme.first_name} {getme.last_name}" if getme.last_name else getme.first_name
        logging.info(f"Bot initialized as {BOT_NAME} (@{BOT_USERNAME})")
        
        # Start user client if STRING is available
        if STRING and pro:
            try:
                await pro.start()
                clients_started.append(pro)
                logging.info("User client started successfully")
            except Exception as e:
                logging.error(f"Failed to start user client: {str(e)}")
                # Continue even if user client fails
                
    except Exception as e:
        # Clean up any started clients
        for client in clients_started:
            try:
                await client.stop()
            except Exception:
                pass
        logging.error(f"Failed to initialize bot: {str(e)}")
        raise


loop.run_until_complete(restrict_bot())
