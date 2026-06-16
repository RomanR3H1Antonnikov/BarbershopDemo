from aiogram.fsm.state import State, StatesGroup


class BookingFlow(StatesGroup):
    choosing_master = State()
    choosing_service = State()
    choosing_date = State()
    choosing_slot = State()
    confirming = State()


class HaircutAI(StatesGroup):
    waiting_input = State()
