import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
ADMIN_IDS: list[int] = [
    int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()
]
DB_PATH: Path = BASE_DIR / "barbershop.db"

BOOKING_DAYS_AHEAD = 14
WORK_HOURS_START = 10
WORK_HOURS_END = 20
SLOT_DURATION_MIN = 60
