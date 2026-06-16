from aiogram import Router, F
from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message

from config import ADMIN_IDS
from db import queries as db
from rich.client import send_rich
from keyboards.admin import admin_menu_kb, admin_back_kb
from texts import ru as t

router = Router(name="admin")


class IsAdmin(Filter):
    async def __call__(self, event: CallbackQuery | Message) -> bool:
        uid = (
            event.from_user.id
            if isinstance(event, (Message, CallbackQuery))
            else 0
        )
        return uid in ADMIN_IDS


# Guard — deny non-admins silently
@router.callback_query(F.data == "admin")
async def cb_admin_entry(callback: CallbackQuery) -> None:
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer(t.ADMIN_ACCESS_DENIED, show_alert=True)
        return
    await callback.message.edit_text(
        t.ADMIN_WELCOME,
        parse_mode="HTML",
        reply_markup=admin_menu_kb(),
    )


@router.callback_query(IsAdmin(), F.data == "admin_schedule")
async def cb_admin_schedule(callback: CallbackQuery) -> None:
    await callback.answer()
    bookings = await db.get_bookings_today()
    await send_rich(
        callback.bot,
        callback.from_user.id,
        rich_html=t.admin_schedule_rich(bookings),
        fallback_html=t.admin_schedule_fallback(bookings),
        reply_markup=admin_back_kb(),
    )


@router.callback_query(IsAdmin(), F.data == "admin_services")
async def cb_admin_services(callback: CallbackQuery) -> None:
    await callback.answer()
    services = await db.get_services()
    from texts.ru import services_rich_html, services_fallback_html
    await send_rich(
        callback.bot,
        callback.from_user.id,
        rich_html=services_rich_html(services),
        fallback_html=services_fallback_html(services),
        reply_markup=admin_back_kb(),
    )


@router.callback_query(IsAdmin(), F.data == "admin_stats")
async def cb_admin_stats(callback: CallbackQuery) -> None:
    await callback.answer()
    stats = await db.get_stats()
    await send_rich(
        callback.bot,
        callback.from_user.id,
        rich_html=t.admin_stats_rich(stats),
        fallback_html=t.admin_stats_fallback(stats),
        reply_markup=admin_back_kb(),
    )
