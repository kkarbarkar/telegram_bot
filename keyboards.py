from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict


def get_main_menu(is_registered: bool = False):
    buttons = [
        [InlineKeyboardButton(text="ℹ️ О нас", callback_data="menu_info")],
        [InlineKeyboardButton(text="📅 Расписание поездок", callback_data="menu_schedule")],
    ]

    if is_registered:
        buttons.insert(0, [InlineKeyboardButton(text="✍️ Записаться на поездку", callback_data="menu_apply")])
        buttons.append([InlineKeyboardButton(text="👤 Мой профиль", callback_data="menu_profile")])
    else:
        buttons.insert(0, [InlineKeyboardButton(text="📝 Стать волонтером", callback_data="menu_registrate")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_phone_keyboard(is_new: bool = True):
    keyboard = [[KeyboardButton(text="📱 Поделиться номером", request_contact=True)],
                [KeyboardButton(text="✍️ Ввести вручную")]]
    if is_new:
        keyboard.append([KeyboardButton(text="⏪️ Назад")])
        keyboard.append([KeyboardButton(text="❌ Отменить")])
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )


def get_change_profile():
    buttons = [
        [InlineKeyboardButton(text="✍️️ Изменить профиль", callback_data="not_confirming")],
        [InlineKeyboardButton(text="◀️ Главное меню", callback_data="back_to_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⏪️ Назад")], [KeyboardButton(text="❌ Отменить")], ],
        resize_keyboard=True
    )


def get_confirming_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="✅ Все верно", callback_data="confirming"),
            InlineKeyboardButton(text="✏️ Изменить", callback_data="not_confirming")
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_edit_keyboard():
    buttons = [
        [InlineKeyboardButton(text="📝 ФИО", callback_data="edit_full_name")],
        [InlineKeyboardButton(text="📱 Телефон", callback_data="edit_phone")],
        [InlineKeyboardButton(text="🎓 Факультет и ОП", callback_data="edit_faculty")],
        [InlineKeyboardButton(text="🚇 Метро", callback_data="edit_metro")],
        [InlineKeyboardButton(text="🔎 Треки", callback_data="edit_tracks")],
        [InlineKeyboardButton(text="🎯 Активности", callback_data="edit_activities")],
        [InlineKeyboardButton(text="💭 Ожидания", callback_data="edit_expectations")],
        [InlineKeyboardButton(text="⏪️ Назад", callback_data="confirm_again")],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_more_info():
    buttons = [
        [InlineKeyboardButton(text="💻 Онлайн-поездки", callback_data="online_trip")],
        [InlineKeyboardButton(text="🚗 Оффлайн-акции и сборы", callback_data="offline_trip")],
        [InlineKeyboardButton(text="❓Частые вопросы и ответы", callback_data="faq_info")],
        [InlineKeyboardButton(text="◀️ Главное меню", callback_data="back_to_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_faq_menu():
    buttons = [[InlineKeyboardButton(text="🚗 О поездках в интернаты", callback_data="faq_trips")],
               [InlineKeyboardButton(text="🎉 О мероприятиях и акциях", callback_data="faq_events")],
               [InlineKeyboardButton(text="😰 Боюсь участвовать", callback_data="faq_fear")],
               [InlineKeyboardButton(text="◀️️ Назад", callback_data="menu_info")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_tracks_keyboard(selected: list = None):
    if selected is None:
        selected = []

    tracks = ["Животные", "Дети", "Взрослые", "Донорские акции"]
    buttons = []

    for track in tracks:
        text = f"✅ {track}" if track in selected else track
        buttons.append([InlineKeyboardButton(
            text=text,
            callback_data=f"track_{track}"
        )])

    buttons.append([InlineKeyboardButton(text="☑️ Готово", callback_data="tracks_done")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_activities_keyboard(selected: list = None):
    if selected is None:
        selected = []

    activities = ["Ездить в поездки", "Участвовать в акциях",
                  "Снимать", "СММ, копирайтинг", "Дизайн", "Делать программу для поездок"]
    buttons = []

    for activity in activities:
        text = f"✅ {activity}" if activity in selected else activity
        buttons.append([InlineKeyboardButton(
            text=text,
            callback_data=f"activity_{activity}"
        )])

    buttons.append([InlineKeyboardButton(text="☑️ Готово", callback_data="activities_done")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_events_keyboard(events: List[Dict]):
    buttons = []
    for event in events:
        buttons.append([InlineKeyboardButton(
            text=f"{event['date']} - {event['city']} ({event['type']})",
            callback_data=f"event_{event['city']}_{event['date']}"
        )])
    buttons.append([InlineKeyboardButton(text="◀️ Главное меню", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_event_detail_keyboard(event: str, is_registered_for_event: bool):
    buttons = []

    if is_registered_for_event:
        buttons.append([InlineKeyboardButton(
            text="❌ Отменить запись",
            callback_data=f"unregister_{event}"
        )])
    else:
        buttons.append([InlineKeyboardButton(
            text="✅ Записаться",
            callback_data=f"register_{event}"
        )])

    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="menu_apply")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admin_keyboard():
    buttons = [[InlineKeyboardButton(text="📢 Отправить рассылку", callback_data="broadcast")],
               [InlineKeyboardButton(text="👥 Информация про поездки", callback_data="trip_info")],
               [InlineKeyboardButton(text="◀️ Главное меню", callback_data="back_to_menu")],
               ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
