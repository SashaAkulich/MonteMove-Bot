# sheets.py
import json
import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

class GoogleSheetsManager:
    def __init__(self, sheet_id: str, credentials_json: str = None):
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
        headers = self.sheet.row_values(1)
        if not headers:
            self.sheet.append_row([
                "Дата", "Telegram ID", "Username", "Visit ID",
                "utm_source", "utm_medium", "utm_campaign", 
                "utm_term", "utm_content", "Raw UTM"
            ])
    
    def log_lead(self, telegram_id: int, username: str, utm_data: dict, visit_id: str):
        try:
            row = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Дата
                str(telegram_id),                               # Telegram ID
                f"@{username}" if username else "N/A",         # Username
                str(visit_id),                                  # Visit ID
                str(utm_data.get("utm_source", "")),            # utm_source
                str(utm_data.get("utm_medium", "")),            # utm_medium
                str(utm_data.get("utm_campaign", "")),          # utm_campaign
                str(utm_data.get("utm_term", "")),              # utm_term
                str(utm_data.get("utm_content", "")),           # utm_content
                "&".join(f"{k}={v}" for k, v in utm_data.items()) if utm_data else ""
            ]
            
            print(f"📝 [GoogleSheets] Row: {row}")
            
            # 🔥 ВАЖНО: value_input_option предотвращает сдвиг столбцов!
            self.sheet.append_row(row, value_input_option='USER_ENTERED')
            print(f"✅ [GoogleSheets] Success!")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            raise
