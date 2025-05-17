from telegram.ext import Application
from utils import load_data, save_data  # You'll create utils.py next
import config

app = Application.builder().token(config.TELEGRAM_TOKEN).build()

# Add handlers later
app.run_polling()