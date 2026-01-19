from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ReplyKeyboardRemove
from aiogram.types import Message

from keyboards import get_main_menu, get_cancel_keyboard, get_confirming_keyboard, get_tracks_keyboard, \
    get_activities_keyboard, get_edit_keyboard, get_phone_keyboard
from sheets_service import SheetsService
from states import RegistrationStates

router = Router()
sheets_service = SheetsService()


def make_confirmation_keyboard(data):
    return (
        "<b>Проверь, всё ли верно:</b>\n\n"
        f"<b>ФИО:</b> {data.get('full_name', '')}\n"
        f"<b>Телефон:</b> {data.get('phone', '')}\n"
        f"<b>Факультет:</b> {data.get('faculty', '')}\n"
        f"<b>Метро:</b> {data.get('metro', '')}\n"
        f"<b>Треки:</b> {data.get('tracks', '')}\n"
        f"<b>Хочу делать:</b> {data.get('activities', '')}\n"
        f"<b>Ожидания:</b> {data.get('expectations', '')}\n\n"
    )


async def get_complete_user_data(user_id: int, state: FSMContext) -> dict:
    data = await state.get_data()

    if sheets_service.is_user_registered(user_id):
        sheet_data = sheets_service.get_user_info(user_id)
        for key in ['full_name', 'phone', 'faculty', 'metro', 'tracks',
                    'activities', 'expectations']:
            if not data.get(key):
                await state.update_data(**{key: sheet_data.get(key, '')})

        data = await state.get_data()

    return data


@router.message(RegistrationStates.waiting_for_full_name)
async def process_full_name(message: Message, state: FSMContext):
    if message.text == "❌ Отменить" or message.text == "⏪️ Назад":
        await state.clear()
        await state.clear()
        await message.answer(
            "Регистрация отменена",
            reply_markup=ReplyKeyboardRemove()
        )
        await message.answer("Выбери действие из меню ⬇️", reply_markup=get_main_menu(False))
        return
    await state.update_data(full_name=message.text)
    data = await get_complete_user_data(message.from_user.id, state)

    if not data.get('is_changing', False):
        await message.answer(
            "<b>Твой номер телефона</b>\n\n",
            reply_markup=get_phone_keyboard(True),
            parse_mode="HTML"
        )
        await state.set_state(RegistrationStates.waiting_for_phone)
        return

    await message.answer(
        make_confirmation_keyboard(data),
        reply_markup=get_confirming_keyboard(),
        parse_mode="HTML"
    )
    await state.update_data(is_changing=False)
    await state.set_state(RegistrationStates.confirming)


@router.message(RegistrationStates.waiting_for_phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(phone=phone)

    data = await get_complete_user_data(message.from_user.id, state)
    if not data.get('is_changing', False):
        await message.answer("<b>Факультет и ОП</b>\n",
                             reply_markup=get_cancel_keyboard(),
                             parse_mode="HTML")
        await state.set_state(RegistrationStates.waiting_for_faculty)
        return

    await message.answer(
        make_confirmation_keyboard(data),
        reply_markup=get_confirming_keyboard(),
        parse_mode="HTML"
    )
    await state.update_data(is_changing=False)
    await state.set_state(RegistrationStates.confirming)


@router.message(RegistrationStates.waiting_for_phone, F.text == "✍️ Ввести вручную")
async def process_phone_manual(message: Message):
    await message.answer(
        "Введи номер телефона:",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )


@router.message(RegistrationStates.waiting_for_phone)
async def process_phone_cancel(message: Message, state: FSMContext):
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("Регистрация отменена", reply_markup=ReplyKeyboardRemove())
        await message.answer("Выбери действие из меню ⬇️", reply_markup=get_main_menu(False))
        return
    if message.text == "⏪️ Назад":
        await state.clear()
        await message.answer("<b>Как тебя зовут? (Укажи ФИО полностью)</b>",
                             reply_markup=get_cancel_keyboard(),
                             parse_mode="HTML")
        await state.set_state(RegistrationStates.waiting_for_full_name)
        return

    await state.update_data(phone=message.text)
    data = await get_complete_user_data(message.from_user.id, state)
    if not data.get('is_changing', False):
        await message.answer("<b>Факультет и ОП</b>\n",
                             reply_markup=get_cancel_keyboard(),
                             parse_mode="HTML")
        await state.set_state(RegistrationStates.waiting_for_faculty)
        return

    await message.answer(
        make_confirmation_keyboard(data),
        reply_markup=get_confirming_keyboard(),
        parse_mode="HTML"
    )
    await state.update_data(is_changing=False)
    await state.set_state(RegistrationStates.confirming)


@router.message(RegistrationStates.waiting_for_faculty)
async def process_faculty(message: Message, state: FSMContext):
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("Регистрация отменена", reply_markup=ReplyKeyboardRemove())
        await message.answer("Выбери действие из меню ⬇️", reply_markup=get_main_menu(False))
        return
    if message.text == "⏪️ Назад":
        await message.answer(
            "<b>Твой номер телефона</b>\n\n",
            reply_markup=get_phone_keyboard(),
            parse_mode="HTML"
        )
        await state.set_state(RegistrationStates.waiting_for_phone)
        return

    await state.update_data(faculty=message.text)
    data = await get_complete_user_data(message.from_user.id, state)
    if not data.get('is_changing', False):
        await message.answer("<b>На какой станции метро ты живешь?</b>\n",
                             reply_markup=get_cancel_keyboard(),
                             parse_mode="HTML")
        await state.set_state(RegistrationStates.waiting_for_metro)
        return

    await message.answer(
        make_confirmation_keyboard(data),
        reply_markup=get_confirming_keyboard(),
        parse_mode="HTML"
    )
    await state.update_data(is_changing=False)
    await state.set_state(RegistrationStates.confirming)


@router.message(RegistrationStates.waiting_for_metro)
async def process_metro(message: Message, state: FSMContext):
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("Регистрация отменена", reply_markup=ReplyKeyboardRemove())
        await message.answer("Выбери действие из меню ⬇️", reply_markup=get_main_menu(False))
        return
    if message.text == "⏪️ Назад":
        await message.answer(
            "<b>Факультет и ОП</b>\n",
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )
        await state.set_state(RegistrationStates.waiting_for_faculty)
        return

    await state.update_data(metro=message.text)
    data = await get_complete_user_data(message.from_user.id, state)
    if not data.get('is_changing', False):
        await state.update_data(selected_tracks=[])
        await message.answer(
            "<b>Выбери интересующие треки:</b>",
            reply_markup=get_tracks_keyboard([]), parse_mode="HTML"
        )
        await state.set_state(RegistrationStates.waiting_for_tracks)
        return

    await message.answer(
        make_confirmation_keyboard(data),
        reply_markup=get_confirming_keyboard(),
        parse_mode="HTML"
    )
    await state.update_data(is_changing=False)
    await state.set_state(RegistrationStates.confirming)


@router.message(RegistrationStates.waiting_for_tracks)
async def process_tracks_start(message: Message, state: FSMContext):
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("Регистрация отменена", reply_markup=ReplyKeyboardRemove())
        await message.answer("Выбери действие из меню ⬇️", reply_markup=get_main_menu(False))
        return
    if message.text == "⏪️ Назад":
        await message.answer("<b>На какой станции метро ты живешь?</b>\n",
                             reply_markup=get_cancel_keyboard(),
                             parse_mode="HTML")
        await state.set_state(RegistrationStates.waiting_for_metro)


@router.callback_query(lambda cmd: cmd.data.startswith('track_'))
async def process_track_selection(callback: CallbackQuery, state: FSMContext):
    track = callback.data.replace('track_', '')
    data = await get_complete_user_data(callback.from_user.id, state)
    selected = data.get('selected_tracks', [])

    if track in selected:
        selected.remove(track)
    else:
        selected.append(track)

    await state.update_data(selected_tracks=selected)
    await callback.message.edit_reply_markup(
        reply_markup=get_tracks_keyboard(selected)
    )
    await callback.answer()


@router.callback_query(lambda cmd: cmd.data == 'tracks_done')
async def tracks_done(callback: CallbackQuery, state: FSMContext):
    data = await get_complete_user_data(callback.from_user.id, state)
    selected = data.get('selected_tracks', [])

    if not selected:
        await callback.answer("Выбери хотя бы один трек!", show_alert=True)
        return
    await state.update_data(tracks=", ".join(selected))
    await callback.message.edit_reply_markup(reply_markup=None)

    if not data.get('is_changing', False):
        await state.update_data(selected_activities=[])
        await callback.message.answer(
            "<b>Выбери интересующие активности:</b>",
            reply_markup=get_activities_keyboard([]), parse_mode="HTML"
        )
        await state.set_state(RegistrationStates.waiting_for_activities)
        await callback.answer()
        return

    data = await get_complete_user_data(callback.from_user.id, state)

    await callback.message.answer(
        make_confirmation_keyboard(data),
        reply_markup=get_confirming_keyboard(),
        parse_mode="HTML"
    )
    await state.update_data(is_changing=False)
    await state.set_state(RegistrationStates.confirming)

    await callback.answer()


@router.message(RegistrationStates.waiting_for_activities)
async def process_activities_start(message: Message, state: FSMContext):
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("Регистрация отменена", reply_markup=ReplyKeyboardRemove())
        await message.answer("Выбери действие из меню ⬇️", reply_markup=get_main_menu(False))
        return
    if message.text == "⏪️ Назад":
        data = await get_complete_user_data(message.from_user.id, state)
        prev_tracks = data.get('tracks', '').split(', ') if data.get('tracks') else []
        await state.update_data(selected_tracks=prev_tracks)
        await message.answer(
            "<b>Выбери интересующие треки:</b>",
            reply_markup=get_tracks_keyboard(prev_tracks), parse_mode="HTML"
        )
        await state.set_state(RegistrationStates.waiting_for_tracks)


@router.callback_query(lambda cmd: cmd.data.startswith('activity_'))
async def process_activities_selection(callback: CallbackQuery, state: FSMContext):
    activity = callback.data.replace('activity_', '')
    data = await get_complete_user_data(callback.from_user.id, state)
    selected = data.get('selected_activities', [])

    if activity in selected:
        selected.remove(activity)
    else:
        selected.append(activity)

    await state.update_data(selected_activities=selected)
    await callback.message.edit_reply_markup(
        reply_markup=get_activities_keyboard(selected)
    )
    await callback.answer()


@router.callback_query(lambda cmd: cmd.data == 'activities_done')
async def activities_done(callback: CallbackQuery, state: FSMContext):
    data = await get_complete_user_data(callback.from_user.id, state)
    selected = data.get('selected_activities', [])

    if not selected:
        await callback.answer("Выбери хотя бы одну активность!", show_alert=True)
        return

    await state.update_data(activities=", ".join(selected))
    await callback.message.edit_reply_markup(reply_markup=None)

    if not data.get('is_changing', False):
        await callback.message.answer(
            "<b>Какие у тебя ожидания от ОГ?</b>\n",
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )
        await state.set_state(RegistrationStates.waiting_for_expectations)
        await callback.answer()
        return

    data = await get_complete_user_data(callback.from_user.id, state)

    await callback.message.answer(
        make_confirmation_keyboard(data),
        reply_markup=get_confirming_keyboard(),
        parse_mode="HTML"
    )
    await state.update_data(is_changing=False)
    await state.set_state(RegistrationStates.confirming)
    await callback.answer()


@router.message(RegistrationStates.waiting_for_expectations)
async def process_expectations(message: Message, state: FSMContext):
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("Регистрация отменена", reply_markup=ReplyKeyboardRemove())
        await message.answer("Выбери действие из меню ⬇️", reply_markup=get_main_menu(False))
        return
    if message.text == "⏪️ Назад":
        data = await get_complete_user_data(message.from_user.id, state)
        prev_act = data.get('activities', '').split(', ') if data.get('activities') else []
        await state.update_data(selected_activities=prev_act)
        await message.answer(
            "<b>Выбери интересующие активности:</b>",
            reply_markup=get_activities_keyboard(prev_act), parse_mode="HTML"
        )
        await state.set_state(RegistrationStates.waiting_for_activities)
        return

    await state.update_data(expectations=message.text)

    data = await get_complete_user_data(message.from_user.id, state)

    await message.answer(
        make_confirmation_keyboard(data),
        reply_markup=get_confirming_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(RegistrationStates.confirming)


@router.callback_query(lambda cmd: cmd.data == 'confirming')
async def confirming(callback: CallbackQuery, state: FSMContext):
    if callback.message.reply_markup:
        await callback.message.edit_reply_markup(reply_markup=None)

    data = await get_complete_user_data(callback.from_user.id, state)
    user_data = {
        'id': callback.from_user.id,
        'username': callback.from_user.username,
        **data
    }

    is_updating = sheets_service.is_user_registered(callback.from_user.id)

    if is_updating:
        sheets_service.update_registration(user_data)
        text = "Профиль обновлен!\n\n"
    else:
        sheets_service.save_registration(user_data)
        text = ("Регистрация завершена! 🎉\n\n"
                "Теперь ты можешь записываться на поездки и участвовать в жизни организации.\n\n"
                "Добро пожаловать в Открой Глаза! ❤️\n\n")

    await callback.message.answer(text, reply_markup=ReplyKeyboardRemove(), parse_mode="HTML")
    await callback.message.answer("Выбери действие из меню ⬇️\n\n",
        reply_markup=get_main_menu(is_registered=True)
    )

    await state.clear()
    await callback.answer()


@router.callback_query(lambda cmd: cmd.data == 'not_confirming')
async def not_confirming(callback: CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "<b>Что хочешь изменить?</b>",
        reply_markup=get_edit_keyboard(), parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(lambda cmd: cmd.data == "edit_full_name")
async def edit_full_name(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.update_data(is_changing=True)
    await callback.message.answer(
        "<b>Как тебя зовут? (Укажи ФИО полностью)</b>",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(RegistrationStates.waiting_for_full_name)
    await callback.answer()


@router.callback_query(lambda cmd: cmd.data == "edit_phone")
async def edit_phone(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.update_data(is_changing=True)
    await callback.message.answer(
        "<b>Твой номер телефона</b>\n\n"
        "Можешь поделиться или ввести вручную",
        reply_markup=get_phone_keyboard(False),
        parse_mode="HTML"
    )

    await state.set_state(RegistrationStates.waiting_for_phone)
    await callback.answer()


@router.callback_query(lambda cmd: cmd.data == "edit_faculty")
async def edit_faculty(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.update_data(is_changing=True)
    await callback.message.answer(
        "<b>Введи факультет и ОП</b>",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(RegistrationStates.waiting_for_faculty)
    await callback.answer()


@router.callback_query(lambda cmd: cmd.data == "edit_metro")
async def edit_metro(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.update_data(is_changing=True)
    await callback.message.answer(
        "<b>Введи метро</b>",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(RegistrationStates.waiting_for_metro)
    await callback.answer()


@router.callback_query(lambda cmd: cmd.data == "edit_tracks")
async def edit_tracks(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    data = await get_complete_user_data(callback.from_user.id, state)
    prev_tracks = data.get('tracks', '').split(', ') if data.get('tracks') else []
    await state.update_data(selected_tracks=prev_tracks)
    await state.update_data(is_changing=True)
    await callback.message.answer(
        "<b>Выбери интересующие треки:</b>",
        reply_markup=get_tracks_keyboard(prev_tracks), parse_mode="HTML"
    )
    await state.set_state(RegistrationStates.waiting_for_tracks)
    await callback.answer()


@router.callback_query(lambda cmd: cmd.data == "edit_activities")
async def edit_activities(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    data = await get_complete_user_data(callback.from_user.id, state)
    prev_act = data.get('activities', '').split(', ') if data.get('activities') else []
    await state.update_data(selected_activities=prev_act)
    await state.update_data(is_changing=True)
    await callback.message.answer(
        "<b>Выбери интересующие активности:</b>",
        reply_markup=get_activities_keyboard(prev_act), parse_mode="HTML"
    )
    await state.set_state(RegistrationStates.waiting_for_activities)
    await callback.answer()


@router.callback_query(lambda cmd: cmd.data == "edit_expectations")
async def edit_expectations(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.update_data(is_changing=True)
    await callback.message.answer(
        "<b>Какие у тебя ожидания от ОГ?</b>\n",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(RegistrationStates.waiting_for_expectations)
    await callback.answer()

@router.callback_query(lambda cmd: cmd.data == "confirm_again")
async def confirm_again(callback: CallbackQuery, state: FSMContext):
    data = await get_complete_user_data(callback.from_user.id, state)

    await callback.message.edit_text(
        make_confirmation_keyboard(data),
        reply_markup=get_confirming_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(RegistrationStates.confirming)
    await callback.answer()