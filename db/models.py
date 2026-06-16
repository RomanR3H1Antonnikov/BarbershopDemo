import aiosqlite
from config import DB_PATH


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS masters (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                name            TEXT NOT NULL,
                specialization  TEXT,
                photo_url       TEXT,
                description     TEXT
            );

            CREATE TABLE IF NOT EXISTS services (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                name            TEXT NOT NULL,
                duration_min    INTEGER NOT NULL,
                price           INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS slots (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                master_id   INTEGER NOT NULL,
                date        TEXT NOT NULL,
                time        TEXT NOT NULL,
                is_booked   INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (master_id) REFERENCES masters (id)
            );

            CREATE TABLE IF NOT EXISTS bookings (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                user_name   TEXT,
                master_id   INTEGER NOT NULL,
                service_id  INTEGER NOT NULL,
                slot_id     INTEGER NOT NULL,
                created_at  TEXT NOT NULL,
                reminded_day  INTEGER NOT NULL DEFAULT 0,
                reminded_hour INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (master_id)  REFERENCES masters (id),
                FOREIGN KEY (service_id) REFERENCES services (id),
                FOREIGN KEY (slot_id)    REFERENCES slots (id)
            );
        """)
        await db.commit()
