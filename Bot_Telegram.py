import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests
from bs4 import BeautifulSoup

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(f"Привет, {user.first_name}! Введите /weather <город> для получения погоды.")

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    city_name = ' '.join(context.args)
    if not city_name:
        await update.message.reply_text("Укажите город: /weather Москва")
        return
    
    try:
        city_code = get_city_code(city_name)
        if not city_code:
            await update.message.reply_text("Город не найден.")
            return
        
        weather_report = get_weather(city_code)
        await update.message.reply_text(weather_report)
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("Ошибка. Попробуйте позже.")

# Функции get_city_code() и get_weather() остаются без изменений (см. оригинальный код)

def main() -> None:
    application = Application.builder().token("7717960112:AAFRsM0j2lEkJaUL7XSmsBk6ik7UXb0qB8Q").build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("weather", weather))
    
    application.run_polling()

if __name__ == '__main__':
    main()