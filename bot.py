from aiogram import Bot, Dispatcher, types
from storage import VisitStorage
from sheets import GoogleSheetsManager

class FinanceBot:
    def __init__(self, token, sheets, storage):
        self.bot = Bot(token=token)
        self.dp = Dispatcher(self.bot)
        self.sheets = sheets
        self.storage = storage
        self.dp.register_message_handler(self.handle_start, commands=["start"])

    async def handle_start(self, message):
        args = message.get_args()
        visit_id = None
        utm_data = {}
        if args:
            if "&" in args or "utm_" in args:
                from urllib.parse import parse_qs, urlparse
                parsed = urlparse("http://t.me/bot?start=" + args)
                params = parse_qs(parsed.query)
                visit_id = params.get("start", [None])[0]
                utm_data = {
                    "source": params.get("utm_source", ["direct"])[0],
                    "medium": params.get("utm_medium", ["direct"])[0],
                    "campaign": params.get("utm_campaign", [""])[0],
                    "content": params.get("utm_content", [""])[0],
                    "term": params.get("utm_term", [""])[0],
                }
            else:
                visit_id = args
                utm_data = {"source": "direct", "medium": "direct"}
        try:
            if visit_id or utm_data.get("source") != "direct":
                self.sheets.log_lead(
                    telegram_id=message.from_user.id,
                    username=message.from_user.username,
                    utm_data=utm_data,
                    visit_id=visit_id or "direct",
                )
                print("✅ Записан лид:", visit_id)
                await message.answer("Здравствуйте! 👋 Наш менеджер скоро ответит.")
                return
        except Exception as e:
            print("❌ Ошибка:", e)
        await message.answer("Здравствуйте! Чем можем помочь?")
