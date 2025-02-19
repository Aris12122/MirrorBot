import logging
import os
from dotenv import load_dotenv
import telebot
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='logs/bot.log'
)
logger = logging.getLogger(__name__)

# Initialize bot
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN found in .env file")

bot = telebot.TeleBot(BOT_TOKEN)

# Initialize model and tokenizer
model_name = "sberbank-ai/rugpt3small_based_on_gpt2"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)

# Set padding token
tokenizer.pad_token = tokenizer.eos_token
model.config.pad_token_id = tokenizer.eos_token_id

def clean_response(text: str) -> str:
    """Clean and format the response text"""
    # Remove common artifacts
    text = text.replace('Соответствие:', '')
    text = text.replace('Ответ:', '')
    
    # Split by common separators and take first part
    for separator in ['\n', '|', ';']:
        text = text.split(separator)[0]
    
    # Clean up periods and spaces
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    if not sentences:
        return "Привет! Как здорово тебя видеть!"
    
    # Take only first complete sentence and add period if needed
    response = sentences[0]
    if not response.endswith('.'):
        response += '.'
        
    return response

def generate_response(prompt, max_length=100):
    try:
        formatted_prompt = "Ты дружелюбный бот. Тебе нужно ответить человеку на следующий запрос одним предложением: " + prompt
        
        encoded = tokenizer.encode_plus(
            formatted_prompt,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512,
            return_attention_mask=True
        )
        
        outputs = model.generate(
            input_ids=encoded['input_ids'],
            attention_mask=encoded['attention_mask'],
            num_return_sequences=2,
            max_length=100,  # Even shorter for more concise responses
            do_sample=True,
            temperature=0.6,
            top_k=40
        )
        
        # Decode and clean response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = response.replace(formatted_prompt, '').strip()
        
        return clean_response(response)

    except Exception as e:
        logger.exception("Error in generate_response")
        return "Извините, произошла ошибка. Попробуйте еще раз."

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hi! Send me /gpt followed by your text to get a response.")

@bot.message_handler(commands=['gpt'])
def handle_gpt(message):
    prompt = message.text.replace('/gpt', '').strip()
    if prompt:
        response = generate_response(prompt)
        bot.reply_to(message, response)
    else:
        bot.reply_to(message, "Please provide some text after /gpt command.")

# Start polling
bot.polling()
