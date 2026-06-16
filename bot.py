"""Entry point — initialise DB, register routers, start polling."""
import asyncio
import logging
import os
import sys

# Fix Windows console encoding for Cyrillic logs
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    # ProactorEventLoop conflicts with VPN TAP adapters (WinError 121)
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from db.models import init_db
from services.scheduler import get_scheduler

from handlers import start, booking, services, portfolio, ai_haircut, admin


async def main() -> None:
    if not BOT_TOKEN:
        log.error("BOT_TOKEN is not set. Copy .env.example → .env and fill it in.")
        return

    # Init DB
    await init_db()

    # Start scheduler
    scheduler = get_scheduler()
    scheduler.start()

    # Build bot & dispatcher
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Register routers (order matters for priority)
    dp.include_router(admin.router)   # admin before generic handlers
    dp.include_router(start.router)
    dp.include_router(booking.router)
    dp.include_router(services.router)
    dp.include_router(portfolio.router)
    dp.include_router(ai_haircut.router)

    log.info("Bot started. Press Ctrl+C to stop.")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        scheduler.shutdown(wait=False)
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
