"""
Booking FSM — 5 steps:
  1. Master selection
  2. Service selection
  3. Date selection
  4. Slot selection
  5. Confirmation → create booking
"""
from __future__ import annotations

from datetime import datetime

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from states.flows import BookingFlow
from db import queries as db
from keyboards.client import (
    masters_kb,
    services_booking_kb,
    dates_kb,
    slots_kb,
    confirm_kb,
    back_to_menu_kb,
    MasterCb,
    ServiceCb,
    DateCb,
    SlotCb,
    NavCb,
)
from rich.client import send_rich
from texts import ru as t
from config import BOOKING_DAYS_AHEAD
from services.scheduler import schedule_reminders

router = Router(name="booking")

_RU_WEEKDAYS = ["понедельник", "вторник", "среду", "четверг", "пятницу", "субботу", "воскресенье"]
_RU_MONTHS_GEN = [
    "января", "февраля", "марта", "апреля", "мая", "июня",
    "июля", "августа", "сентября", "октября", "ноября", "декабря",
]


def _fmt_date_ru(date_str: str) -> str:
    d = datetime.strptime(date_str, "%Y-%m-%d").date()
    return f"{d.day} {_RU_MONTHS_GEN[d.month - 1]}"


# ── Step 0: Entry point ───────────────────────────────────────────────────────

@router.callback_query(F.data == "booking_start")
async def cb_booking_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(BookingFlow.choosing_master)
    masters = await db.get_masters()
    await callback.message.edit_text(
        t.BOOKING_CHOOSE_MASTER,
        parse_mode="HTML",
        reply_markup=masters_kb(masters),
    )


# ── Step 1: Master chosen ─────────────────────────────────────────────────────

@router.callback_query(MasterCb.filter(), BookingFlow.choosing_master)
async def cb_master_chosen(
    callback: CallbackQuery, callback_data: MasterCb, state: FSMContext
) -> None:
    master = await db.get_master(callback_data.id)
    if not master:
        await callback.answer("Мастер не найден, попробуй снова.", show_alert=True)
        return

    await state.update_data(master_id=master["id"], master_name=master["name"])
    await state.set_state(BookingFlow.choosing_service)

    services = await db.get_services()
    await callback.message.edit_text(
        t.BOOKING_CHOOSE_SERVICE.format(master_name=master["name"]),
        parse_mode="HTML",
        reply_markup=services_booking_kb(services),
    )


# ── Step 2: Service chosen ────────────────────────────────────────────────────

@router.callback_query(ServiceCb.filter(), BookingFlow.choosing_service)
async def cb_service_chosen(
    callback: CallbackQuery, callback_data: ServiceCb, state: FSMContext
) -> None:
    service = await db.get_service(callback_data.id)
    if not service:
        await callback.answer("Услуга не найдена.", show_alert=True)
        return

    data = await state.get_data()
    await state.update_data(service_id=service["id"], service_name=service["name"],
                            price=service["price"])
    await state.set_state(BookingFlow.choosing_date)

    dates = await db.get_available_dates(data["master_id"], BOOKING_DAYS_AHEAD)
    if not dates:
        await callback.message.edit_text(
            "😔 У мастера нет свободных окон в ближайшие 2 недели.\n"
            "Попробуй выбрать другого мастера.",
            reply_markup=back_to_menu_kb(),
        )
        return

    await callback.message.edit_text(
        t.BOOKING_CHOOSE_DATE.format(
            master_name=data["master_name"],
            service_name=service["name"],
        ),
        parse_mode="HTML",
        reply_markup=dates_kb(dates),
    )


# ── Step 3: Date chosen ───────────────────────────────────────────────────────

@router.callback_query(DateCb.filter(), BookingFlow.choosing_date)
async def cb_date_chosen(
    callback: CallbackQuery, callback_data: DateCb, state: FSMContext
) -> None:
    data = await state.get_data()
    date_str = callback_data.value
    slots = await db.get_free_slots(data["master_id"], date_str)

    if not slots:
        dates = await db.get_available_dates(data["master_id"], BOOKING_DAYS_AHEAD)
        await callback.message.edit_text(
            t.BOOKING_NO_SLOTS_ON_DATE.format(date=_fmt_date_ru(date_str)),
            parse_mode="HTML",
            reply_markup=dates_kb(dates),
        )
        return

    await state.update_data(date=date_str)
    await state.set_state(BookingFlow.choosing_slot)

    await callback.message.edit_text(
        t.BOOKING_CHOOSE_SLOT.format(
            master_name=data["master_name"],
            service_name=data["service_name"],
            date=_fmt_date_ru(date_str),
        ),
        parse_mode="HTML",
        reply_markup=slots_kb(slots),
    )


# ── Step 4: Slot chosen ───────────────────────────────────────────────────────

@router.callback_query(SlotCb.filter(), BookingFlow.choosing_slot)
async def cb_slot_chosen(
    callback: CallbackQuery, callback_data: SlotCb, state: FSMContext
) -> None:
    slot = await db.get_slot(callback_data.id)
    if not slot or slot["is_booked"]:
        await callback.answer("Этот слот уже занят — выбери другое время.", show_alert=True)
        return

    data = await state.get_data()
    await state.update_data(slot_id=slot["id"], time=slot["time"])
    await state.set_state(BookingFlow.confirming)

    await callback.message.edit_text(
        t.BOOKING_CONFIRM.format(
            master_name=data["master_name"],
            service_name=data["service_name"],
            date=_fmt_date_ru(data["date"]),
            time=slot["time"],
            price=data["price"],
        ),
        parse_mode="HTML",
        reply_markup=confirm_kb(),
    )


# ── Step 5: Confirm ───────────────────────────────────────────────────────────

@router.callback_query(F.data == "booking_confirm", BookingFlow.confirming)
async def cb_booking_confirmed(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()

    # Double-check slot is still free
    slot = await db.get_slot(data["slot_id"])
    if not slot or slot["is_booked"]:
        await callback.answer(
            "Кто-то успел занять этот слот — выбери другое время.", show_alert=True
        )
        await state.set_state(BookingFlow.choosing_slot)
        slots = await db.get_free_slots(data["master_id"], data["date"])
        if slots:
            await callback.message.edit_text(
                t.BOOKING_CHOOSE_SLOT.format(
                    master_name=data["master_name"],
                    service_name=data["service_name"],
                    date=_fmt_date_ru(data["date"]),
                ),
                parse_mode="HTML",
                reply_markup=slots_kb(slots),
            )
        return

    user = callback.from_user
    booking_id = await db.create_booking(
        user_id=user.id,
        user_name=user.full_name or user.username,
        master_id=data["master_id"],
        service_id=data["service_id"],
        slot_id=data["slot_id"],
    )
    await db.mark_slot_booked(data["slot_id"])
    await state.clear()

    # Schedule reminders
    try:
        await schedule_reminders(
            bot=callback.bot,
            booking_id=booking_id,
            user_id=user.id,
            date_str=data["date"],
            time_str=data["time"],
            master_name=data["master_name"],
            service_name=data["service_name"],
        )
    except Exception:
        pass  # reminders are best-effort

    from rich.client import send_rich
    from texts.ru import BOOKING_SUCCESS, SHOP_ADDRESS

    success_html = (
        "<h2>✅ Запись подтверждена!</h2>"
        f"<p>👤 <b>{data['master_name']}</b></p>"
        f"<p>✂️ {data['service_name']}</p>"
        f"<p>📅 {_fmt_date_ru(data['date'])} в {data['time']}</p>"
        f"<p>💰 {data['price']} ₽</p>"
        f"<p>📍 {SHOP_ADDRESS}</p>"
        "<p>Напомню за день и за час — жди уведомление ⏰</p>"
    )
    success_plain = t.BOOKING_SUCCESS.format(
        master_name=data["master_name"],
        service_name=data["service_name"],
        date=_fmt_date_ru(data["date"]),
        time=data["time"],
        price=data["price"],
        address=SHOP_ADDRESS,
    )

    await callback.message.delete()
    await send_rich(
        callback.bot,
        callback.from_user.id,
        rich_html=success_html,
        fallback_html=success_plain,
        reply_markup=back_to_menu_kb(),
    )


@router.callback_query(F.data == "booking_cancel")
async def cb_booking_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    from keyboards.client import main_menu
    await callback.message.edit_text(
        t.BOOKING_CANCELLED,
        parse_mode="HTML",
        reply_markup=main_menu(),
    )


# ── Back navigation ───────────────────────────────────────────────────────────

@router.callback_query(NavCb.filter(F.to == "master"))
async def nav_to_master(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(BookingFlow.choosing_master)
    masters = await db.get_masters()
    await callback.message.edit_text(
        t.BOOKING_CHOOSE_MASTER,
        parse_mode="HTML",
        reply_markup=masters_kb(masters),
    )


@router.callback_query(NavCb.filter(F.to == "service"))
async def nav_to_service(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    if not data.get("master_name"):
        await nav_to_master(callback, state)
        return
    await state.set_state(BookingFlow.choosing_service)
    services = await db.get_services()
    await callback.message.edit_text(
        t.BOOKING_CHOOSE_SERVICE.format(master_name=data["master_name"]),
        parse_mode="HTML",
        reply_markup=services_booking_kb(services),
    )


@router.callback_query(NavCb.filter(F.to == "date"))
async def nav_to_date(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    if not data.get("service_name"):
        await nav_to_service(callback, state)
        return
    await state.set_state(BookingFlow.choosing_date)
    dates = await db.get_available_dates(data["master_id"], BOOKING_DAYS_AHEAD)
    await callback.message.edit_text(
        t.BOOKING_CHOOSE_DATE.format(
            master_name=data["master_name"],
            service_name=data["service_name"],
        ),
        parse_mode="HTML",
        reply_markup=dates_kb(dates),
    )
