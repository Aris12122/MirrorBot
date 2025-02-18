import logging
import os
from dotenv import load_dotenv
import telebot

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Retrieve bot token from environment variable
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN found in .env file")

# Initialize bot with token
bot = telebot.TeleBot(BOT_TOKEN)

# Define command handler for /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hi!")

# Define message handler to echo received messages
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, message.text)

# Start polling
bot.polling()
