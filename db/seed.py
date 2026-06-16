"""Demo seed data — 3 masters, 5 services, slots for 14 days ahead."""
import asyncio
import aiosqlite
from datetime import date, timedelta
from config import DB_PATH
from db.models import init_db

MASTERS = [
    {
        "name": "Алексей Фёдоров",
        "specialization": "Фейд и современные стрижки",
        "photo_url": "https://i.pravatar.cc/400?img=12",
        "description": (
            "5 лет в профессии. Специализируется на фейдах и современных техниках. "
            "Участник Barber Battle 2024."
        ),
    },
    {
        "name": "Дмитрий Краснов",
        "specialization": "Классика и борода",
        "photo_url": "https://i.pravatar.cc/400?img=33",
        "description": (
            "7 лет опыта. Мастер классической стрижки и бородки. "
            "Работает с формой лица, подбирает стрижку под клиента."
        ),
    },
    {
        "name": "Кирилл Морозов",
        "specialization": "Детские стрижки и андеркат",
        "photo_url": "https://i.pravatar.cc/400?img=52",
        "description": (
            "3 года опыта. Специалист по детским стрижкам и нестандартным запросам. "
            "Дети обожают — терпелив и весёлый."
        ),
    },
]

SERVICES = [
    {"name": "Стрижка классика", "duration_min": 45, "price": 800},
    {"name": "Фейд / Тейп", "duration_min": 60, "price": 1200},
    {"name": "Борода", "duration_min": 30, "price": 600},
    {"name": "Стрижка + борода", "duration_min": 75, "price": 1500},
    {"name": "Детская стрижка", "duration_min": 30, "price": 600},
]

WORK_START = 10
WORK_END = 20


async def seed() -> None:
    await init_db()

    async with aiosqlite.connect(DB_PATH) as db:
        # Skip if already seeded
        async with db.execute("SELECT COUNT(*) FROM masters") as cur:
            if (await cur.fetchone())[0] > 0:
                print("DB already seeded — skipping.")
                return

        # Insert masters
        master_ids = []
        for m in MASTERS:
            cur = await db.execute(
                "INSERT INTO masters (name, specialization, photo_url, description) "
                "VALUES (?, ?, ?, ?)",
                (m["name"], m["specialization"], m["photo_url"], m["description"]),
            )
            master_ids.append(cur.lastrowid)

        # Insert services
        for s in SERVICES:
            await db.execute(
                "INSERT INTO services (name, duration_min, price) VALUES (?, ?, ?)",
                (s["name"], s["duration_min"], s["price"]),
            )

        # Generate slots for 14 days
        today = date.today()
        for day_offset in range(14):
            day = today + timedelta(days=day_offset)
            day_str = day.strftime("%Y-%m-%d")
            # Mon=0 … Sat=5; skip Sunday (6)
            if day.weekday() == 6:
                continue
            for master_id in master_ids:
                # Each master has their own schedule with a few gaps
                for hour in range(WORK_START, WORK_END):
                    # Skip lunch break and random gaps to make it realistic
                    if hour == 13:
                        continue
                    if master_id % 2 == 0 and hour == 15:
                        continue
                    await db.execute(
                        "INSERT INTO slots (master_id, date, time, is_booked) VALUES (?, ?, ?, 0)",
                        (master_id, day_str, f"{hour:02d}:00"),
                    )

        await db.commit()
        print(f"Seeded {len(MASTERS)} masters, {len(SERVICES)} services, slots for 14 days.")


if __name__ == "__main__":
    asyncio.run(seed())
