from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from config import ADMIN_IDS
from keyboards import get_admin_keyboard
from sheets_service import SheetsService
from states import BroadcastStates

router = Router()
sheets_service = SheetsService()


def is_admin(user_id: int) -> bool:
    return str(user_id) in ADMIN_IDS


@router.message(Command("admin"), lambda m: is_admin(m.from_user.id))
async def admin_panel(message: Message):
    await message.answer("Выбери действие из меню ⬇️\n\n", reply_markup=get_admin_keyboard(), parse_mode="HTML")


@router.callback_query(lambda cmd: cmd.data == "broadcast")
async def broadcast(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введи текст сообщения")
    await state.set_state(BroadcastStates.waiting_for_message)
    await callback.answer()


@router.message(BroadcastStates.waiting_for_message)
async def process_broadcast(message: Message):
    sheet = sheets_service.get_worksheet("questions")
    records = sheet.get_all_records()

    for record in records:
        user_id = int(record.get("Телеграм id"))
        await message.bot.send_message(user_id, message.text, parse_mode="HTML")

    await message.answer("Рассылка завершена", reply_markup=get_admin_keyboard())


@router.callback_query(lambda cmd: cmd.data == "trip_info")
async def trip_info(callback: CallbackQuery):
    events = sheets_service.get_upcoming_events()
    if not events:
        await callback.message.answer("Нет предстоящих поездок")
        return

    buttons = []
    for event in events:
        buttons.append([InlineKeyboardButton(
            text=f"{event['date']} - {event['city']} ({event['type']})",
            callback_data=f"list_event_{event['city']}_{event['date']}"
        )])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text("Выбери поездку:", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(lambda cmd: cmd.data.startswith('list_event_'))
async def show_event_registrations(callback: CallbackQuery):
    event_name = callback.data.replace('list_event_', '').replace('_', ' ', 1)

    sheet = sheets_service.get_worksheet("activity")
    event_cell = sheet.find(event_name, in_row=2)
    values = sheet.col_values(event_cell.col)[2:]
    usernames = sheet.col_values(4)[2:]

    registered = []
    for i, value in enumerate(values):
        if value in ['TRUE', True, 'ИСТИНА']:
            registered.append(f"@{usernames[i]}")

    if registered:
        text = ("<b>Список записавшихся:</b> \n\n" + "\n".join(registered))
    else:
        text = f"<b>Пока никто не записался</b>"

    await callback.message.edit_text(text, reply_markup=get_admin_keyboard(), parse_mode="HTML")
    await callback.answer()
