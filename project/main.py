"""Main entry point for the Telegram employee payment bot."""

import logging
import os
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from config import TELEGRAM_TOKEN
from handlers import start, handle_message

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

def main():
    """Start the bot."""
    # Load environment variables
    load_dotenv()
    
    # Check required env vars
    token = TELEGRAM_TOKEN
    if not token:
        logger.error("No token provided. Set TELEGRAM_TOKEN in .env file.")
        return
    
    # Create the Updater and pass it your bot's token
    updater = Updater(token)
    
    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    
    # Register command handlers
    dp.add_handler(CommandHandler("start", start))
    
    # Register message handler
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    # Start the Bot
    updater.start_polling()
    
    logger.info("Bot started successfully!")
    
    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()