import requests
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

# Конфигурация
TOKEN = "ТОКЕН БОТ"
OWM_API_KEY = "28caefc76d9af8c1c35079990b58b435"
WEATHER_STATES = {
    'Thunderstorm': '⛈ Гроза',
    'Drizzle': '🌧 Морось',
    'Rain': '🌧 Дождь',
    'Snow': '❄ Снег',
    'Mist': '🌫 Туман',
    'Smoke': '🌫 Дымка',
    'Haze': '🌫 Мгла',
    'Dust': '🌫 Пыль',
    'Fog': '🌫 Туман',
    'Sand': '🌫 Песчаная буря',
    'Ash': '🌫 Вулканический пепел',
    'Squall': '💨 Шквал',
    'Tornado': '🌪 Торнадо',
    'Clear': '☀ Ясно',
    'Clouds': '☁ Облачно'
}

# Состояния для ConversationHandler
CITY, DAYS = range(2)

# Отправляет приветственное сообщение при команде /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.first_name}! Я бот погоды.\n"
        "Отправь мне название города, и я пришлю тебе прогноз погоды.\n"
        "Или используй команду /forecast для выбора количества дней."
    )

# Получает текущую погоду для города
async def get_weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    city = update.message.text
    weather_data = fetch_weather(city)
    
    if weather_data:
        await update.message.reply_text(format_current_weather(weather_data), parse_mode='HTML')
    else:
        await update.message.reply_text("Не удалось получить данные о погоде. Проверьте название города.")

# Начинает процесс получения прогноза погоды на несколько дней
async def forecast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Введите название города:",
        reply_markup=ReplyKeyboardRemove()
    )
    return CITY

# Получает город от пользователя и запрашивает количество дней
async def received_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['city'] = update.message.text
    
    reply_keyboard = [['1', '3', '5']]
    await update.message.reply_text(
        "Выберите количество дней для прогноза (максимум 5):",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return DAYS

# Получает количество дней и отправляет прогноз
async def received_days(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    city = context.user_data['city']
    days = int(update.message.text)
    
    if days < 1 or days > 5:
        await update.message.reply_text("Пожалуйста, выберите от 1 до 5 дней.")
        return DAYS
    
    forecast_data = fetch_weather_forecast(city, days)
    
    if forecast_data:
        for day_forecast in format_forecast(forecast_data, days):
            await update.message.reply_text(day_forecast, parse_mode='HTML')
    else:
        await update.message.reply_text("Не удалось получить прогноз погоды. Проверьте название города.")
    
    return ConversationHandler.END

# Отменяет диалог
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Отменено.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# Получает текущую погоду с OpenWeatherMap API
def fetch_weather(city: str) -> dict:
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OWM_API_KEY}&units=metric&lang=ru"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except:
        return None

# Получает прогноз погоды с OpenWeatherMap API
def fetch_weather_forecast(city: str, days: int) -> dict:
    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OWM_API_KEY}&units=metric&lang=ru&cnt={days*8}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except:
        return None

# Форматирует данные о текущей погоде в читаемый текст
def format_current_weather(data: dict) -> str:
    city = data['name']
    country = data['sys']['country']
    temp = data['main']['temp']
    feels_like = data['main']['feels_like']
    humidity = data['main']['humidity']
    wind_speed = data['wind']['speed']
    weather_desc = WEATHER_STATES.get(data['weather'][0]['main'], data['weather'][0]['description'])
    weather_icon = data['weather'][0]['icon']
    
    return (
        f"<b>Погода в {city}, {country}</b>\n\n"
        f"<b>{weather_desc}</b> <i>({temp}°C, ощущается как {feels_like}°C)</i>\n"
        f"💧 Влажность: {humidity}%\n"
        f"🌬 Ветер: {wind_speed} м/с\n"
        f"\n<i>Обновлено: {data['dt']}</i>"
    )

# Форматирует прогноз погоды в список сообщений
def format_forecast(data: dict, days: int) -> list:
    city = data['city']['name']
    country = data['city']['country']
    forecasts = []
    
# Берем прогноз на середину дня (обычно 12:00)
    for i in range(days):
        day_data = data['list'][i*8 + 4] if len(data['list']) > i*8 + 4 else data['list'][-1]
        date = day_data['dt_txt'].split()[0]
        temp = day_data['main']['temp']
        feels_like = day_data['main']['feels_like']
        humidity = day_data['main']['humidity']
        wind_speed = day_data['wind']['speed']
        weather_desc = WEATHER_STATES.get(day_data['weather'][0]['main'], day_data['weather'][0]['description'])
        
        forecast_text = (
            f"<b>Прогноз на {date} в {city}, {country}</b>\n\n"
            f"<b>{weather_desc}</b> <i>({temp}°C, ощущается как {feels_like}°C)</i>\n"
            f"💧 Влажность: {humidity}%\n"
            f"🌬 Ветер: {wind_speed} м/с"
        )
        forecasts.append(forecast_text)
    
    return forecasts

def main() -> None:
    # Создаем Application
    application = Application.builder().token(TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))
    
    # Обработчик для получения текущей погоды
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_weather))
    
    # Обработчик диалога для прогноза
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('forecast', forecast)],
        states={
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_city)],
            DAYS: [MessageHandler(filters.Regex('^(1|3|5)$'), received_days)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    application.add_handler(conv_handler)

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()