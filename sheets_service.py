import gspread

from config import CREDENTIALS_FILENAME, QUESTIONS_SPREADSHEET_URL
from datetime import datetime
from typing import List, Dict, Optional


class SheetsService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.account = gspread.service_account(filename=CREDENTIALS_FILENAME)
            self.spreadsheet = self.account.open_by_url(QUESTIONS_SPREADSHEET_URL)
            self.initialized = True

    def get_worksheet(self, sheet_name: str) -> gspread.Worksheet:
        return self.spreadsheet.worksheet(sheet_name)

    def save_registration(self, user_data: Dict):
        sheet = self.get_worksheet("questions")

        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user_data.get('id', ''),
            user_data.get('username', ''),
            user_data.get('full_name', ''),
            user_data.get('phone', ''),
            user_data.get('faculty', ''),
            user_data.get('metro', ''),
            user_data.get('tracks', ''),
            user_data.get('activities', ''),
            user_data.get('expectations', ''),
        ]

        sheet.append_row(row)

        sheet = self.get_worksheet("activity")
        full_name = user_data.get('full_name', '').split()
        row = [
            full_name[0] if len(full_name) > 0 else '',
            full_name[1] if len(full_name) > 1 else '',
            user_data.get('id'),
            user_data.get('username'),
            user_data.get('phone')
        ]
        sheet.append_row(row)

    def update_registration(self, user_data: Dict):
        questions_sheet = self.get_worksheet("questions")
        questions_cell = questions_sheet.find(str(user_data['id']), in_column=2)
        row = questions_cell.row
        questions_sheet.update_cell(row, 4, user_data.get('full_name', ''))
        questions_sheet.update_cell(row, 5, user_data.get('phone', ''))
        questions_sheet.update_cell(row, 6, user_data.get('faculty', ''))
        questions_sheet.update_cell(row, 7, user_data.get('metro', ''))
        questions_sheet.update_cell(row, 8, user_data.get('tracks', ''))
        questions_sheet.update_cell(row, 9, user_data.get('activities', ''))
        questions_sheet.update_cell(row, 10, user_data.get('expectations', ''))

        activity_sheet = self.get_worksheet("activity")
        activity_cell = activity_sheet.find(str(user_data['id']), in_column=3)
        full_name = user_data.get('full_name', '').split()
        activity_sheet.update_cell(activity_cell.row, 1, full_name[0] if len(full_name) > 0 else '')
        activity_sheet.update_cell(activity_cell.row, 2, full_name[1] if len(full_name) > 1 else '')
        activity_sheet.update_cell(activity_cell.row, 5, user_data.get('phone', ''))

    def is_user_registered(self, user_id: int) -> bool:
        sheet = self.get_worksheet("questions")
        cell = sheet.find(str(user_id), in_column=2)
        return cell is not None

    def get_user_info(self, user_id: int) -> Optional[Dict]:
        sheet = self.get_worksheet("questions")
        cell = sheet.find(str(user_id), in_column=2)
        if not cell:
            return None

        row = sheet.row_values(cell.row)

        return {
            'data': row[0],
            'id': row[1] if len(row) > 1 else '',
            'username': row[2] if len(row) > 2 else '',
            'full_name': row[3] if len(row) > 3 else '',
            'phone': row[4] if len(row) > 4 else '',
            'faculty': row[5] if len(row) > 5 else '',
            'metro': row[6] if len(row) > 6 else '',
            'tracks': row[7] if len(row) > 7 else '',
            'activities': row[8] if len(row) > 8 else '',
            'expectations': row[9] if len(row) > 9 else ''
        }

    def get_upcoming_events(self) -> List[Dict]:
        sheet = self.get_worksheet("schedule")
        records = sheet.get_all_records()
        events = []

        for record in records:
            if record.get('Статус') != 'Завершена':
                try:
                    events.append({
                        'name': record.get('Название'),
                        'date': record.get('Дата', ''),
                        'type': record.get('Тип'),
                        'city': record.get('Город')
                    })
                except (ValueError, AttributeError):
                    continue

        return events

    def change_status_for_event(self, user_id: int, event: str, is_register : bool):
        sheet = self.get_worksheet("activity")
        user_id_cell = sheet.find(str(user_id), in_column=3)
        event_cell = sheet.find(event, in_row=2)
        sheet.update_cell(user_id_cell.row, event_cell.col, is_register)

    def is_registered_for_event(self, user_id: int, event: str) -> bool:
        sheet = self.get_worksheet("activity")
        user_id_cell = sheet.find(str(user_id), in_column=3)
        event_cell = sheet.find(event, in_row=2)

        value = sheet.cell(user_id_cell.row, event_cell.col).value
        return value in ['TRUE', True, 'ИСТИНА']
