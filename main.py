from telegram import Update
from telegram.ext import Application, MessageHandler, filters
import os
import requests
import logging
from datetime import datetime

# Configuration
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
HF_API_KEY = os.getenv('HF_API_KEY')  # Your Hugging Face token
API_URL = "https://router.huggingface.co/novita/v3/openai/chat/completions"

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

headers = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}

def query_hf(prompt: str) -> str:
    """Query Novita's HF-compatible endpoint with error handling"""
    payload = {
        "model": "mistralai/Mistral-7B-Instruct-v0.3",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 150
    }
    
    try:
        start_time = datetime.now()
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=30  # 30-second timeout
        )
        response.raise_for_status()  # Raises HTTPError for bad responses
        return response.json()["choices"][0]["message"]["content"]
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API Error: {str(e)}")
        return "⚠️ The AI service is currently overloaded. Please try again later."
    except (KeyError, IndexError) as e:
        logger.error(f"Response Parsing Error: {str(e)}")
        return "⚠️ I'm having trouble understanding the response. Try rephrasing your question."

async def handle_message(update: Update, context):
    """Process Telegram messages"""
    user_msg = update.message.text
    logger.info(f"Processing message from {update.effective_user.id}: {user_msg[:50]}...")
    
    ai_response = query_hf(user_msg)
    await update.message.reply_text(ai_response)

# Bot initialization
app = Application.builder().token(TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Webhook configuration for Render
if __name__ == '__main__':
    PORT = int(os.getenv('PORT', 5000))
    WEBHOOK_URL = f"https://your-render-service.onrender.com/{TELEGRAM_TOKEN}"
    
    app.run_webhook(
        listen='0.0.0.0',
        port=PORT,
        webhook_url=WEBHOOK_URL,
        url_path=TELEGRAM_TOKEN,
        drop_pending_updates=True
    )
