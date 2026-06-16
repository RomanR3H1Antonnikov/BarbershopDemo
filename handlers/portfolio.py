from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto, URLInputFile

from rich.client import send_rich
from keyboards.client import portfolio_categories_kb, back_to_menu_kb, PortfolioCb
from texts.ru import (
    PORTFOLIO_INTRO_RICH,
    PORTFOLIO_TITLE,
    PORTFOLIO_REVIEWS_RICH,
    PORTFOLIO_REVIEWS_FALLBACK,
)

router = Router(name="portfolio")

# Demo photo URLs per category (replace with real Telegram file_ids in production)
_CATEGORY_PHOTOS: dict[str, list[str]] = {
    "fade": [
        "https://images.unsplash.com/photo-1622286342621-4bd786c2447c?w=400",
        "https://images.unsplash.com/photo-1534297635766-a262cdcb8ee4?w=400",
        "https://images.unsplash.com/photo-1605497788044-5a32c7078486?w=400",
    ],
    "classic": [
        "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?w=400",
        "https://images.unsplash.com/photo-1521490683712-35a1cb235d1c?w=400",
    ],
    "beard": [
        "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?w=400",
        "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=400",
    ],
    "kids": [
        "https://images.unsplash.com/photo-1585747860715-2ba37e788b70?w=400",
        "https://images.unsplash.com/photo-1534297635766-a262cdcb8ee4?w=400",
    ],
}

_CATEGORY_CAPTIONS = {
    "fade": "💈 <b>Фейд / Тейп</b>\nЧёткий переход, чистый финиш — каждый раз.",
    "classic": "✂️ <b>Классика</b>\nТимлесс-стиль, который всегда к месту.",
    "beard": "🧔 <b>Борода</b>\nФорма, линии, баланс — под твой тип лица.",
    "kids": "👦 <b>Детская</b>\nБыстро, аккуратно, и ребёнок доволен.",
}


@router.callback_query(F.data == "portfolio")
async def cb_portfolio(callback: CallbackQuery) -> None:
    await callback.answer()
    await send_rich(
        callback.bot,
        callback.from_user.id,
        rich_html=PORTFOLIO_INTRO_RICH,
        fallback_html=PORTFOLIO_TITLE,
        reply_markup=portfolio_categories_kb(),
    )


@router.callback_query(PortfolioCb.filter())
async def cb_portfolio_category(
    callback: CallbackQuery, callback_data: PortfolioCb
) -> None:
    await callback.answer()
    cat = callback_data.category
    photos = _CATEGORY_PHOTOS.get(cat, [])
    caption = _CATEGORY_CAPTIONS.get(cat, "")

    from aiogram.utils.keyboard import InlineKeyboardBuilder

    nav_builder = InlineKeyboardBuilder()
    nav_builder.button(text="📅 Записаться", callback_data="booking_start")
    nav_builder.button(text="← Назад к категориям", callback_data="portfolio")
    nav_builder.adjust(1)
    nav_markup = nav_builder.as_markup()

    try:
        if len(photos) >= 2:
            media = [
                InputMediaPhoto(
                    media=URLInputFile(url, filename=f"photo_{i}.jpg"),
                    caption=caption if i == 0 else None,
                    parse_mode="HTML" if i == 0 else None,
                )
                for i, url in enumerate(photos)
            ]
            await callback.bot.send_media_group(
                chat_id=callback.from_user.id, media=media
            )
        elif photos:
            await callback.bot.send_photo(
                chat_id=callback.from_user.id,
                photo=URLInputFile(photos[0], filename="photo.jpg"),
                caption=caption,
                parse_mode="HTML",
            )
    except Exception:
        await callback.bot.send_message(
            chat_id=callback.from_user.id,
            text=f"{caption}\n\n<i>Фото временно недоступны.</i>",
            parse_mode="HTML",
            reply_markup=nav_markup,
        )
        return

    await callback.bot.send_message(
        chat_id=callback.from_user.id,
        text="Нравится? Запишись прямо сейчас 👇",
        reply_markup=nav_markup,
    )


@router.callback_query(F.data == "portfolio_reviews")
async def cb_reviews(callback: CallbackQuery) -> None:
    await callback.answer()
    await send_rich(
        callback.bot,
        callback.from_user.id,
        rich_html=PORTFOLIO_REVIEWS_RICH,
        fallback_html=PORTFOLIO_REVIEWS_FALLBACK,
        reply_markup=back_to_menu_kb(),
    )
