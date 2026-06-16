from __future__ import annotations

from datetime import date, datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


# ── Callback data schemas ─────────────────────────────────────────────────────

class MasterCb(CallbackData, prefix="master"):
    id: int


class ServiceCb(CallbackData, prefix="service"):
    id: int


class DateCb(CallbackData, prefix="date"):
    value: str  # YYYY-MM-DD


class SlotCb(CallbackData, prefix="slot"):
    id: int


class NavCb(CallbackData, prefix="nav"):
    to: str  # master | service | date | slot | menu


class PortfolioCb(CallbackData, prefix="portfolio"):
    category: str


# ── Main menu ─────────────────────────────────────────────────────────────────

def main_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📅 Записаться", callback_data="booking_start")
    builder.button(text="✂️ Услуги и цены", callback_data="services")
    builder.button(text="📸 Наши работы", callback_data="portfolio")
    builder.button(text="🤖 Подобрать стрижку", callback_data="ai_haircut")
    builder.button(text="📍 Контакты", callback_data="contacts")
    builder.button(text="👤 Я мастер", callback_data="admin")
    builder.adjust(2, 2, 2)
    return builder.as_markup()


# ── Booking: master selection ─────────────────────────────────────────────────

def masters_kb(masters: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for m in masters:
        builder.button(
            text=f"👤 {m['name']} — {m['specialization']}",
            callback_data=MasterCb(id=m["id"]),
        )
    builder.button(text="← Назад", callback_data="menu")
    builder.adjust(1)
    return builder.as_markup()


# ── Booking: service selection ────────────────────────────────────────────────

def services_booking_kb(services: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for s in services:
        builder.button(
            text=f"{s['name']} — {s['price']} ₽",
            callback_data=ServiceCb(id=s["id"]),
        )
    builder.button(text="← Назад", callback_data=NavCb(to="master"))
    builder.adjust(1)
    return builder.as_markup()


# ── Booking: date selection ───────────────────────────────────────────────────

_RU_WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
_RU_MONTHS = [
    "янв", "фев", "мар", "апр", "май", "июн",
    "июл", "авг", "сен", "окт", "ноя", "дек",
]


def _format_date_btn(date_str: str) -> str:
    d = datetime.strptime(date_str, "%Y-%m-%d").date()
    wd = _RU_WEEKDAYS[d.weekday()]
    mon = _RU_MONTHS[d.month - 1]
    return f"{wd} {d.day} {mon}"


def dates_kb(available_dates: list[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for ds in available_dates:
        builder.button(
            text=_format_date_btn(ds),
            callback_data=DateCb(value=ds),
        )
    builder.button(text="← Назад", callback_data=NavCb(to="service"))
    builder.adjust(3)
    return builder.as_markup()


# ── Booking: slot selection ───────────────────────────────────────────────────

def slots_kb(slots: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for s in slots:
        builder.button(
            text=f"⏰ {s['time']}",
            callback_data=SlotCb(id=s["id"]),
        )
    builder.button(text="← Другая дата", callback_data=NavCb(to="date"))
    builder.adjust(3)
    return builder.as_markup()


# ── Booking: confirmation ─────────────────────────────────────────────────────

def confirm_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить", callback_data="booking_confirm")
    builder.button(text="❌ Отмена", callback_data="booking_cancel")
    builder.adjust(2)
    return builder.as_markup()


# ── Post-booking / error ──────────────────────────────────────────────────────

def back_to_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🏠 В главное меню", callback_data="menu")
    return builder.as_markup()


def book_now_kb(master_id: int | None = None) -> InlineKeyboardMarkup:
    """CTA button used after AI haircut recommendation."""
    builder = InlineKeyboardBuilder()
    builder.button(text="📅 Записаться", callback_data="booking_start")
    builder.button(text="🏠 В меню", callback_data="menu")
    builder.adjust(1)
    return builder.as_markup()


def ai_waiting_kb() -> InlineKeyboardMarkup:
    """Back button shown while AI is waiting for user input."""
    builder = InlineKeyboardBuilder()
    builder.button(text="← В меню", callback_data="menu")
    return builder.as_markup()


# ── Portfolio ─────────────────────────────────────────────────────────────────

def portfolio_categories_kb() -> InlineKeyboardMarkup:
    from texts.ru import PORTFOLIO_CATEGORIES
    builder = InlineKeyboardBuilder()
    for cat in PORTFOLIO_CATEGORIES:
        builder.button(
            text=f"{cat['emoji']} {cat['label']}",
            callback_data=PortfolioCb(category=cat["id"]),
        )
    builder.button(text="⭐️ Отзывы", callback_data="portfolio_reviews")
    builder.button(text="← В меню", callback_data="menu")
    builder.adjust(2, 1, 1)
    return builder.as_markup()


# ── Services (show book button) ────────────────────────────────────────────────

def after_services_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📅 Записаться", callback_data="booking_start")
    builder.button(text="← В меню", callback_data="menu")
    builder.adjust(1)
    return builder.as_markup()


# ── Contacts CTA ──────────────────────────────────────────────────────────────

def contacts_kb(maps_url: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🗺 Открыть на карте", url=maps_url)
    builder.button(text="📅 Записаться", callback_data="booking_start")
    builder.button(text="← В меню", callback_data="menu")
    builder.adjust(1)
    return builder.as_markup()


# ── Final CTA ─────────────────────────────────────────────────────────────────

def final_cta_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💬 Обсудить проект", url="https://rehy-solutions.ru/#contact")
    builder.button(text="📲 Написать в Telegram", url="https://t.me/RE_HY")
    builder.adjust(1)
    return builder.as_markup()
