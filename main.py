from telegram import Update
from telegram.ext import Application, MessageHandler, filters
import os
import requests
import logging

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize bot
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
HF_TOKEN = os.getenv('HF_TOKEN')
app = Application.builder().token(TELEGRAM_TOKEN).build()

# Hugging Face API
def query_hf(prompt):
    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
            headers={"Authorization": f"Bearer {HF_TOKEN}"},
            json={"inputs": prompt, "max_new_tokens": 150}
        )
        return response.json()[0]["generated_text"]
    except Exception as e:
        logger.error(f"HF API Error: {e}")
        return "⚠️ AI is overloaded. Try again later!"

# Telegram message handler
async def handle_message(update: Update, context):
    user_message = update.message.text
    logger.info(f"User: {update.effective_user.id} - Message: {user_message}")
    
    ai_response = query_hf(user_message)
    await update.message.reply_text(ai_response)

# Register handler
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Webhook setup for Render
async def set_webhook():
    port = int(os.environ.get('PORT', 5000))
    webhook_url = f"https://your-render-service.onrender.com/{TELEGRAM_TOKEN}"
    await app.bot.set_webhook(webhook_url)
    logger.info(f"Webhook set to {webhook_url}")

if __name__ == '__main__':
    # For Render deployment
    app.run_webhook(
        listen='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        webhook_url=f"https://your-render-service.onrender.com/{TELEGRAM_TOKEN}",
        url_path=TELEGRAM_TOKEN
    )
