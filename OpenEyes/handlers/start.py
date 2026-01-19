from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from keyboards import get_main_menu, get_cancel_keyboard, get_more_info, get_events_keyboard, get_change_profile
from sheets_service import SheetsService
from states import RegistrationStates

router = Router()
sheets_service = SheetsService()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    user_id = message.from_user.id
    user_info = sheets_service.get_user_info(user_id)
    is_registered = user_info is not None

    if is_registered and user_info['full_name'] != "":
        welcome_text = f"Привет, {user_info['full_name'].split()[1]}! 👋\n"
    else:
        welcome_text = f"Привет, {message.from_user.first_name}! 👋\n"

    welcome_text += (
        f"Я бот <b>Открой Глаза</b> — благотворительной организации в Вышке.\n"
    )
    await message.answer(
        welcome_text,
        parse_mode="HTML"
    )

    if is_registered:
        menu_text = "Давно не виделись! Выбери действие из меню ⬇️"
    else:
        menu_text = ("Чтобы стать волонтёром ОГ и отправиться в поездку, нужно пройти регистрацию.\n"
                     "Выбери действие из меню ⬇️")

    await message.answer(
        menu_text,
        reply_markup=get_main_menu(is_registered),
        parse_mode="HTML"
    )

@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext):
    await state.clear()

    user_id = message.from_user.id
    user_info = sheets_service.get_user_info(user_id)
    is_registered = user_info is not None

    if is_registered:
        menu_text = "Давно не виделись! Выбери действие из меню ⬇️"
    else:
        menu_text = ("Чтобы стать волонтёром ОГ и отправиться в поездку, нужно пройти регистрацию.\n"
                     "Выбери действие из меню ⬇️")

    await message.answer(
        menu_text,
        reply_markup=get_main_menu(is_registered),
        parse_mode="HTML"
    )


@router.callback_query(lambda cmd: cmd.data == "menu_info")
async def menu_info(callback: CallbackQuery):
    text = (
        "<b>Открой глаза</b> — крупнейшая благотворительная организация в Вышке,\n"
        "основанная в 2008 году студенческой инициативой «Ингруп СтС».\n\n"
        "<b>Одна из основных наших задач</b> — популяризация добрых дел.\n"
        "Личные истории, волонтерские проекты и интересные поездки к детям, \n"
        "взрослым и животным — все это здесь! \n\n"
        "<b>Наша основная деятельность</b> — онлайн и оффлайн поездки в интернаты\n"
        "к детям и взрослым и поездки в приюты для животных. \n"
        "Также мы проводим различные акции и сборы для поддержки и развития инклюзивного общества.\n"
    )
    await callback.message.edit_text(text, reply_markup=get_more_info(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(lambda cmd: cmd.data == "menu_profile")
async def menu_profile(callback: CallbackQuery):
    user_info = sheets_service.get_user_info(callback.from_user.id)

    text = (
        f"<b>Твой профиль:</b>\n\n"
        f"ФИО: {user_info['full_name']}\n"
        f"Телефон: {user_info['phone']}\n"
        f"Факультет и ОП: {user_info['faculty']}\n"
        f"Метро: {user_info['metro']}\n"
        f"Треки: {user_info['tracks']}\n"
        f"Хочу делать: {user_info['activities']}\n"
    )
    await callback.message.edit_text(text, reply_markup=get_change_profile(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(lambda cmd: cmd.data == "menu_registrate")
async def menu_registrate(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    if sheets_service.is_user_registered(user_id):
        await callback.answer("Ты уже зарегистрирован(a)!", show_alert=True)
        return

    await callback.message.edit_reply_markup(reply_markup=None)

    await callback.message.answer(
        "Для регистрации нужно ответить на несколько вопросов.\n"
        "Это займёт всего пару минут.\n"
        "<b>Как тебя зовут? (Укажи ФИО полностью)</b>",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )

    await state.set_state(RegistrationStates.waiting_for_full_name)
    await callback.answer()


@router.callback_query(lambda cmd: cmd.data == "menu_schedule")
async def menu_schedule(callback: CallbackQuery):
    events = sheets_service.get_upcoming_events()

    if not events:
        await callback.message.edit_text("В ближайшее время поездок не ожидается!")
        return

    user_id = callback.from_user.id
    is_registered = sheets_service.is_user_registered(user_id)

    text = "<b>Предстоящие поездки и мероприятия:</b>\n\n"

    for event in events:
        if event['type'] == "онлайн":
            text = "💻   "
        else:
            text += "🚗  "
        text += f"{event['date']} - {event['city']} ({event['type']})\n\n"

    if not is_registered:
        text += "Чтобы присоединиться к поездке, пройди регистрацию!❤️️\n\n"
    await callback.message.edit_text(text, reply_markup=get_main_menu(is_registered), parse_mode="HTML")
    await callback.answer()


@router.callback_query(lambda cmd: cmd.data == "menu_apply")
async def menu_apply(callback: CallbackQuery):
    upcoming_events = sheets_service.get_upcoming_events()

    if not upcoming_events:
        await callback.message.edit_text("В ближайшее время поездок не ожидается!")
        return

    await callback.message.edit_text("Выбери поездку для подробностей:",
                                     reply_markup=get_events_keyboard(upcoming_events))
    await callback.answer()


@router.callback_query(lambda cmd: cmd.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    is_registered = sheets_service.is_user_registered(user_id)

    await callback.message.edit_text(
        "Выбери действие из меню ⬇️\n\n",
        reply_markup=get_main_menu(is_registered),
        parse_mode="HTML"
    )
    await callback.answer()
