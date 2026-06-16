from aiogram import Router, F
from aiogram.types import CallbackQuery

from db.queries import get_services
from rich.client import send_rich
from keyboards.client import after_services_kb
from texts.ru import services_rich_html, services_fallback_html

router = Router(name="services")


@router.callback_query(F.data == "services")
async def cb_services(callback: CallbackQuery) -> None:
    await callback.answer()
    services = await get_services()
    await send_rich(
        callback.bot,
        callback.from_user.id,
        rich_html=services_rich_html(services),
        fallback_html=services_fallback_html(services),
        reply_markup=after_services_kb(),
    )
