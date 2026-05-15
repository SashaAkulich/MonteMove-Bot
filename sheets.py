import os 

class GoogleSheetsManager:
    def __init__(self, sheet_id: str, credentials_json: str = None):
        if credentials_json and credentials_json.strip().startswith('{'):
            import json
            from google.oauth2.service_account import Credentials
            creds_info = json.loads(credentials_json)
            creds = Credentials.from_service_account_info(creds_info, scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ])
        else:
            from google.oauth2.service_account import Credentials
            creds = Credentials.from_service_account_file(
                os.getenv('GOOGLE_CREDENTIALS_FILE', '/app/credentials.json'),
                scopes=[
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive"
                ]
            )
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_key(sheet_id).sheet1
        self._ensure_headers()
