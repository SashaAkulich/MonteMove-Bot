# sheets.py
import json
import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime


class GoogleSheetsManager:
    def __init__(self, sheet_id: str, credentials_json: str = None):
        # Пробуем распарсить JSON-строку из переменной окружения
        if credentials_json and credentials_json.strip().startswith('{'):
            creds_info = json.loads(credentials_json)
            creds = Credentials.from_service_account_info(
                creds_info,
                scopes=[
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive"
                ]
            )
        else:
            # Если JSON не передан — пробуем загрузить из файла
            creds = Credentials.from_service_account_file(
                os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json'),
                scopes=[
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive"
                ]
            )
        
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_key(sheet_id).sheet1
        self._ensure_headers()
    
    def _ensure_headers(self):
        """Создание заголовков, если таблица пустая"""
        headers = self.sheet.row_values(1)
        if not headers:
            self.sheet.append_row([
                "Дата", "Telegram ID", "Username", "Visit ID",
                "utm_source", "utm_medium", "utm_campaign", 
                "utm_term", "utm_content", "Raw UTM"
            ])
    
    def log_lead(self, telegram_id: int, username: str, utm_data: dict, visit_id: str):
        """Запись лида в таблицу с логированием"""
        try:
            print(f"📝 [GoogleSheets] Writing: telegram_id={telegram_id}, username={username}, visit_id={visit_id}")
            
            row = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                telegram_id,
                f"@{username}" if username else "N/A",
                visit_id,
                utm_data.get("utm_source", ""),
                utm_data.get("utm_medium", ""),
                utm_data.get("utm_campaign", ""),
                utm_data.get("utm_term", ""),
                utm_data.get("utm_content", ""),
                "&".join(f"{k}={v}" for k, v in utm_data.items())
            ]
            
            print(f"📝 [GoogleSheets] Row data: {row}")
            self.sheet.append_row(row)
            print(f"✅ [GoogleSheets] Successfully appended row!")
            
        except Exception as e:
            print(f"❌ [GoogleSheets] ERROR: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise
