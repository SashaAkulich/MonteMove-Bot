# bot.py
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from storage import VisitStorage
from sheets import GoogleSheetsManager

class MonteMoveBot:
    def __init__(self, token: str, sheets: GoogleSheetsManager, storage: VisitStorage):
        self.bot = Bot(token=token)
        self.dp = Dispatcher(self.bot, storage=MemoryStorage())
        self.sheets = sheets
        self.storage = storage
        self._register_handlers()
    
    def _register_handlers(self):
        
        @self.dp.message_handler(commands=['start'])
        async def handle_start(message: types.Message):
            args = message.get_args()
            visit_id = args.strip() if args else None
            
            # Если есть visit_id — пытаемся получить UTM и залогировать
            if visit_id:
                utm = self.storage.get_and_delete(visit_id)
                if utm:
                    self.sheets.log_lead(
                        telegram_id=message.from_user.id,
                        username=message.from_user.username,
                        utm_data=utm,
                        visit_id=visit_id
                    )
            
            # Приветственное сообщение с услугами [[сайт]]
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add("🇲🇪 Черногория", "🇷🇸 Сербия")
            keyboard.add("💱 Обмен валют", "📄 Документы")
            keyboard.add("👨‍💼 Связаться с менеджером")
            
            await message.answer(
                "Здравствуйте! Добро пожаловать в **MonteMove** 🤝\n\n"
                "Мы помогаем с переездом и легализацией в Черногории и Сербии:\n\n"
                "🇲🇪 **Черногория**:\n"
                "• ВНЖ через бизнес / Digital Nomad\n"
                "• Обмен валют с доставкой\n"
                "• Перевод документов, бухгалтерия\n"
                "• Недвижимость и трансфер\n\n"
                "🇷🇸 **Сербия**:\n"
                "• ВНЖ через ИП / компанию DOO\n"
                "• Юридический адрес, аренда\n"
                "• Обмен валют, грузоперевозки\n\n"
                "Выберите направление или опишите ваш запрос 👇",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        
        @self.dp.message_handler(text=["🇲🇪 Черногория", "🇷🇸 Сербия"])
        async def handle_country(message: types.Message):
            country = message.text
            services = {
                "🇲🇪 Черногория": "Черногория",
                "🇷🇸 Сербия": "Сербия"
            }
            await message.answer(
                f"Отлично! Вы выбрали **{services[country]}**.\n\n"
                f"Напишите, что вас интересует:\n"
                f"• Легализация / ВНЖ 🪪\n"
                f"• Обмен валюты 💱\n"
                f"• Регистрация компании 🏢\n"
                f"• Другой вопрос ✍️"
            )
        
        @self.dp.message_handler(text=["👨‍💼 Связаться с менеджером"])
        async def handle_contact(message: types.Message):
            await message.answer(
                "✅ Ваш запрос принят!\n"
                "Менеджер свяжется с вами в ближайшее время.\n\n"
                "Для срочных вопросов:\n"
                "📧 info@montemove.com\n"
                "🌐 montemove.com"
            )
        
        @self.dp.message_handler(content_types=['text'])
        async def handle_text(message: types.Message):
            # Просто подтверждаем получение сообщения
            await message.answer(
                "✅ Спасибо! Ваше сообщение получено.\n"
                "Менеджер изучит запрос и ответит в ближайшее время 🤝"
            )
    
    async def set_webhook(self, webhook_url: str):
        await self.bot.set_webhook(webhook_url, drop_pending_updates=True)
    
    async def close(self):
        await self.bot.close()
