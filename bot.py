from aiogram import Bot, Dispatcher, types
from storage import VisitStorage
from sheets import GoogleSheetsManager

class FinanceBot:
    def __init__(self, token: str, sheets: GoogleSheetsManager, storage: VisitStorage):
        self.bot = Bot(token=token)
        self.dp = Dispatcher(self.bot)
        self.sheets = sheets
        self.storage = storage
        
        @self.dp.message_handler(commands=['start'])
        async def handle_start(message: types.Message):
            args = message.get_args()
            visit_id = args if args else None
            
            if visit_id:
                utm = self.storage.get_and_delete(visit_id)
                if utm:
                    self.sheets.log_lead(
                        telegram_id=message.from_user.id,
                        username=message.from_user.username,
                        utm_data=utm,
                        visit_id=visit_id
                    )
                    await message.answer(
                        "Здравствуйте! 👋\n"
                        "Наш менеджер уже получил уведомление и скоро ответит вам.\n"
                        "Если вопрос срочный — напишите, что вас интересует."
                    )
                    return
            
            await message.answer(
                "Здравствуйте! Чем можем помочь?\n"
                "Опишите ваш запрос, и мы свяжемся с вами."
            )
