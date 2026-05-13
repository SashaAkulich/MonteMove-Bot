# main.py
from fastapi import FastAPI, Request
from bot import MonteMoveBot
from sheets import GoogleSheetsManager
from storage import VisitStorage
import os
import uvicorn
from dotenv import load_dotenv
from aiogram import types

load_dotenv()
app = FastAPI()

# Инициализация
sheets = GoogleSheetsManager(
    sheet_id=os.getenv('GOOGLE_SHEET_ID'),
    credentials_json=os.getenv('GOOGLE_CREDENTIALS_JSON')
)
storage = VisitStorage()
bot = MonteMoveBot(
    token=os.getenv('TELEGRAM_BOT_TOKEN'),
    sheets=sheets,
    storage=storage
)

@app.on_event("startup")
async def on_startup():
    """Установка вебхука при старте"""
    railway_url = os.getenv('RAILWAY_PUBLIC_DOMAIN')  # Авто-переменная Railway
    webhook_url = f"https://{railway_url}/webhook" if railway_url else os.getenv('WEBHOOK_URL')
    
    if webhook_url:
        await bot.set_webhook(webhook_url)
        print(f"✅ Webhook set: {webhook_url}")

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """Обработка обновлений от Telegram"""
    try:
        update_data = await request.json()
        update = types.Update(**update_data)
        await bot.dp.process_update(update)
        return {"ok": True}
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return {"ok": False}

@app.get("/")
async def root():
    """Health check для Railway"""
    return {
        "status": "ok", 
        "bot": "MonteMoveBot 🇲🇪🇷🇸",
        "services": ["Легализация", "Обмен валют", "Релокация"]
    }

@app.get("/health")
async def health():
    """Эндпоинт для проверки работоспособности"""
    return {"status": "healthy"}

@app.on_event("shutdown")
async def on_shutdown():
    await bot.close()

# Запуск через uvicorn при прямом запуске (для локальной разработки)
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Railway предоставляет PORT [[23]]
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
