"""APScheduler-based reminders: day-before and hour-before."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from texts.ru import REMINDER_DAY_BEFORE, REMINDER_HOUR_BEFORE, SHOP_ADDRESS

log = logging.getLogger(__name__)
_scheduler: AsyncIOScheduler | None = None


def get_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    return _scheduler


async def _send_reminder(bot, user_id: int, text: str, booking_id: int, kind: str) -> None:
    from db.queries import mark_reminded
    try:
        await bot.send_message(user_id, text, parse_mode="HTML")
        await mark_reminded(booking_id, kind)
    except Exception as e:
        log.warning("Reminder failed for booking %s: %s", booking_id, e)


async def schedule_reminders(
    bot,
    booking_id: int,
    user_id: int,
    date_str: str,
    time_str: str,
    master_name: str,
    service_name: str,
) -> None:
    """Schedule day-before and hour-before reminders."""
    slot_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    scheduler = get_scheduler()

    day_before = slot_dt - timedelta(hours=24)
    hour_before = slot_dt - timedelta(hours=1)
    now = datetime.now()

    reminder_kwargs = dict(
        master_name=master_name,
        service_name=service_name,
        time=time_str,
        address=SHOP_ADDRESS,
    )

    if day_before > now:
        scheduler.add_job(
            _send_reminder,
            trigger="date",
            run_date=day_before,
            kwargs=dict(
                bot=bot,
                user_id=user_id,
                text=REMINDER_DAY_BEFORE.format(**reminder_kwargs),
                booking_id=booking_id,
                kind="day",
            ),
            id=f"remind_day_{booking_id}",
            replace_existing=True,
        )

    if hour_before > now:
        scheduler.add_job(
            _send_reminder,
            trigger="date",
            run_date=hour_before,
            kwargs=dict(
                bot=bot,
                user_id=user_id,
                text=REMINDER_HOUR_BEFORE.format(**reminder_kwargs),
                booking_id=booking_id,
                kind="hour",
            ),
            id=f"remind_hour_{booking_id}",
            replace_existing=True,
        )
