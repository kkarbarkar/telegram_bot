from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    waiting_for_full_name = State()
    waiting_for_phone = State()
    waiting_for_faculty = State()
    waiting_for_metro = State()
    waiting_for_tracks = State()
    waiting_for_activities = State()
    waiting_for_expectations = State()
    confirming = State()


class BroadcastStates(StatesGroup):
    waiting_for_message = State()