from typing import List, Dict
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from keyboards import get_events_keyboard, get_event_detail_keyboard
from sheets_service import SheetsService

router = Router()
sheets_service = SheetsService()


@router.callback_query(lambda c: c.data.startswith('event_'))
async def show_event_detail(callback: CallbackQuery):
    info = callback.data.split('_', 2)
    event_name = f"{info[1]} {info[2]}"
    events = sheets_service.get_upcoming_events()
    event = next((e for e in events if f"{e['city']} {e['date']}" == event_name), None)

    user_id = callback.from_user.id
    is_registered = sheets_service.is_registered_for_event(user_id, event_name)

    text = (
        f"📅 <b>Когда:</b> {event['date']}\n"
        f"📍 <b>Куда:</b> {event['city']}\n")
    if is_registered:
        text += "<b>Статус:</b> Ты записан(а)! ✅\n\n"
    else:
        text += "<b>Статус:</b> Ты не записан(а)! ❌\n\n"

    await callback.message.edit_text(
        text,
        reply_markup=get_event_detail_keyboard(event_name, is_registered),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(lambda cmd: cmd.data.startswith('register_'))
async def register_for_event(callback: CallbackQuery):
    event_name = callback.data.replace('register_', '').replace('_', ' ', 1)
    user_id = callback.from_user.id
    sheets_service.change_status_for_event(user_id, event_name, True)
    await callback.message.edit_text("Ты записан на поездку! ✅", show_alert=True)
    await callback.message.edit_reply_markup(
        reply_markup=get_event_detail_keyboard(event_name, True)
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith('unregister_'))
async def unregister_for_event(callback: CallbackQuery):
    event_name = callback.data.replace('unregister_', '').replace('_', ' ', 1)
    user_id = callback.from_user.id
    sheets_service.change_status_for_event(user_id, event_name, False)

    await callback.message.edit_text("Запись отменена!\n"
                                     "Будем ждать в следующих поездках ❤️\n\n", show_alert=True)
    await callback.message.edit_reply_markup(
        reply_markup=get_event_detail_keyboard(event_name, False)
    )
    await callback.answer()
