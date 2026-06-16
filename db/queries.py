from __future__ import annotations

import aiosqlite
from datetime import date, datetime, timedelta
from config import DB_PATH


# ── Masters ───────────────────────────────────────────────────────────────────

async def get_masters() -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM masters ORDER BY id") as cur:
            return [dict(r) for r in await cur.fetchall()]


async def get_master(master_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM masters WHERE id = ?", (master_id,)
        ) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


# ── Services ──────────────────────────────────────────────────────────────────

async def get_services() -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM services ORDER BY price"
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def get_service(service_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM services WHERE id = ?", (service_id,)
        ) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


# ── Slots ─────────────────────────────────────────────────────────────────────

async def get_free_slots(master_id: int, date_str: str) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT * FROM slots
            WHERE master_id = ? AND date = ? AND is_booked = 0
            ORDER BY time
            """,
            (master_id, date_str),
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def get_slot(slot_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM slots WHERE id = ?", (slot_id,)
        ) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def mark_slot_booked(slot_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE slots SET is_booked = 1 WHERE id = ?", (slot_id,)
        )
        await db.commit()


async def get_available_dates(master_id: int, days_ahead: int = 14) -> list[str]:
    """Return dates with at least one free slot for the master."""
    today = date.today()
    dates = [
        (today + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(0, days_ahead)
    ]
    placeholders = ",".join("?" * len(dates))
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            f"""
            SELECT DISTINCT date FROM slots
            WHERE master_id = ? AND is_booked = 0 AND date IN ({placeholders})
            ORDER BY date
            """,
            (master_id, *dates),
        ) as cur:
            rows = await cur.fetchall()
            return [r[0] for r in rows]


# ── Bookings ──────────────────────────────────────────────────────────────────

async def create_booking(
    user_id: int,
    user_name: str | None,
    master_id: int,
    service_id: int,
    slot_id: int,
) -> int:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            INSERT INTO bookings (user_id, user_name, master_id, service_id, slot_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, user_name, master_id, service_id, slot_id, now),
        )
        await db.commit()
        return cursor.lastrowid


async def get_bookings_today() -> list[dict]:
    today = date.today().strftime("%Y-%m-%d")
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT b.id, b.user_name, b.user_id,
                   m.name AS master_name,
                   s.name AS service_name, s.price,
                   sl.time, sl.date
            FROM bookings b
            JOIN masters m  ON m.id = b.master_id
            JOIN services s ON s.id = b.service_id
            JOIN slots sl   ON sl.id = b.slot_id
            WHERE sl.date = ?
            ORDER BY sl.time
            """,
            (today,),
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def get_stats() -> dict:
    today = date.today().strftime("%Y-%m-%d")
    week_start = (date.today() - timedelta(days=date.today().weekday())).strftime("%Y-%m-%d")

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM bookings b JOIN slots sl ON sl.id = b.slot_id WHERE sl.date = ?",
            (today,),
        ) as cur:
            today_count = (await cur.fetchone())[0]

        async with db.execute(
            "SELECT COUNT(*) FROM bookings b JOIN slots sl ON sl.id = b.slot_id WHERE sl.date >= ?",
            (week_start,),
        ) as cur:
            week_count = (await cur.fetchone())[0]

        async with db.execute(
            "SELECT COUNT(*) FROM slots WHERE date >= ? AND date <= ?",
            (today, (date.today() + timedelta(days=6)).strftime("%Y-%m-%d")),
        ) as cur:
            total_slots = (await cur.fetchone())[0]

        async with db.execute(
            "SELECT COUNT(*) FROM slots WHERE date >= ? AND is_booked = 1 AND date <= ?",
            (today, (date.today() + timedelta(days=6)).strftime("%Y-%m-%d")),
        ) as cur:
            filled_slots = (await cur.fetchone())[0]

    return {
        "today": today_count,
        "week": week_count,
        "total_slots": total_slots,
        "filled_slots": filled_slots,
    }


async def get_pending_reminders() -> list[dict]:
    """Bookings that need a day-before or hour-before reminder."""
    now = datetime.now()
    day_threshold = (now + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M")
    hour_threshold = (now + timedelta(hours=1, minutes=5)).strftime("%Y-%m-%d %H:%M")
    hour_threshold_low = (now + timedelta(minutes=55)).strftime("%Y-%m-%d %H:%M")

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT b.id, b.user_id, b.user_name, b.reminded_day, b.reminded_hour,
                   m.name AS master_name,
                   s.name AS service_name,
                   sl.date, sl.time,
                   (sl.date || ' ' || sl.time) AS slot_dt
            FROM bookings b
            JOIN masters m  ON m.id = b.master_id
            JOIN services s ON s.id = b.service_id
            JOIN slots sl   ON sl.id = b.slot_id
            WHERE (sl.date || ' ' || sl.time) > ?
            ORDER BY slot_dt
            """,
            (now.strftime("%Y-%m-%d %H:%M"),),
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def mark_reminded(booking_id: int, kind: str) -> None:
    col = "reminded_day" if kind == "day" else "reminded_hour"
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE bookings SET {col} = 1 WHERE id = ?", (booking_id,))
        await db.commit()
