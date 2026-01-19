from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from keyboards import get_more_info, get_faq_menu
from sheets_service import SheetsService

router = Router()
sheets_service = SheetsService()


@router.callback_query(lambda cmd: cmd.data == "online_trip")
async def online_trip(callback: CallbackQuery):
    text = ("<b>Онлайн-поездки (или «онлайны»)</b> — это поездка, которая проходит дистанционно. \n"
            "В отличие от оффлайн поездок здесь мы уделяем всего 30 минут в неделю на каждый интернат, \n"
            "чтобы созвониться в Zoom и поговорить с ребятами на интересные темы, например, \n"
            "в течение этого года мы обсуждали «Эмоции». ")
    await callback.message.edit_text(text, reply_markup=get_more_info(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(lambda cmd: cmd.data == "offline_trip")
async def offline_trip(callback: CallbackQuery):
    text = ("В «Открой глаза» существуют различные акции для интернатов и приютов. \n"
            "Зачастую им нужна не только моральная, но и физическая поддержка, \n"
            "поэтому к нам приходят наши подопечные с запросом сбора тех или иных вещей для комфортного существования.\n\n"
            "Например, у нас существует новогодняя традиция - каждый год мы собираем и расшифровываем письма, \n"
            "которые ребята пишут Деду Морозу, чтобы выложить документ со всеми подарками в общий доступ, \n"
            "чтобы наши волонтеры смогли осуществить эти мечты и подарить подарки детям, взрослым и животным.")
    await callback.message.edit_text(text, reply_markup=get_more_info(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(lambda cmd: cmd.data == "faq_info")
async def faq_info(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "<b>Выбери интересующий вопрос:</b>",
        reply_markup=get_faq_menu(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "faq_trips")
async def faq_trips(callback: CallbackQuery):
    text = ("<b>❓Как происходит поездка в детский интернат?</b>\n\n"
            "<b>Ответ:</b> "
            "Как правило мы отправляемся в интернаты на выходных рано утром на трансфере от Вышки. \n"
            "Мы прибываем туда строго в 10 часов утра, чтобы провести программу на 1,5-2 часа по теме, \n"
            "которую мы подготовили. В рамках программы мы показываем презентацию и общаемся с детьми. \n"
            "Также мы часто проводим для них мастер-классы и прочие активности. \n"
            "После проведения программы мы возвращаемся обратно в Москву к 14-15 часам. \n\n")

    await callback.message.edit_text(text, reply_markup=get_faq_menu(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(lambda c: c.data == "faq_events")
async def cmd_info_event(callback: CallbackQuery):
    text = ("<b>❓Какие мероприятия проводит «Открой глаза» помимо поездок и сборов?</b>\n\n"
            "<b>Ответ: </b>"
            "Наша организация часто является участником крупных мероприятий и акций волонтерских организаций, \n"
            "такие как фестиваль Экстра, Дни донора и тд. Кроме того, мы являемся организаторами Фестиваля Улыбок, \n"
            "в рамках которого дети из интернатов приехали в ВШЭ, а также серии выездных летних лагерей, \n"
            "где мы на несколько дней ездили в интернаты, чтобы провести комплексную программу на заданную тему.\n\n")
    await callback.message.edit_text(text, reply_markup=get_faq_menu(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(lambda c: c.data == "faq_fear")
async def cmd_info_scary(callback: CallbackQuery):
    text = ("<b>❓Мне интересно волонтерство, но я боюсь участвовать в вашей деятельности. Что делать?</b>\n\n"
            "<b>Ответ:</b> "
            "Вовлекаться в работу «Открой глаза» можно постепенно! Сначала посетить нашу точку на крупных мероприятиях Вышки, \n"
            "потом вступить в чат Волонтеров ОГ через куратора волонтеров, отправиться в поездку в приют \n"
            "и поучаствовать в онлайн-поездке, и только потом отправиться в первую поездку в интернат.\n\n")
    await callback.message.edit_text(text, reply_markup=get_faq_menu(), parse_mode="HTML")
    await callback.answer()