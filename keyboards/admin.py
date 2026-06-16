from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📋 Расписание на сегодня", callback_data="admin_schedule")
    builder.button(text="✂️ Услуги", callback_data="admin_services")
    builder.button(text="📊 Статистика", callback_data="admin_stats")
    builder.button(text="← В главное меню", callback_data="menu")
    builder.adjust(1)
    return builder.as_markup()


def admin_back_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="← Панель мастера", callback_data="admin")
    return builder.as_markup()
