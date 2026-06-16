from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from texts import ru as t
from keyboards.client import main_menu, final_cta_kb

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(t.WELCOME, parse_mode="HTML", reply_markup=main_menu())


@router.callback_query(F.data == "menu")
async def cb_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(
        t.WELCOME, parse_mode="HTML", reply_markup=main_menu()
    )


@router.callback_query(F.data == "contacts")
async def cb_contacts(callback: CallbackQuery) -> None:
    from rich.client import send_rich
    from keyboards.client import contacts_kb
    from texts.ru import CONTACTS_RICH, CONTACTS_FALLBACK, SHOP_MAPS_URL

    await callback.answer()
    await send_rich(
        callback.bot,
        callback.from_user.id,
        rich_html=CONTACTS_RICH,
        fallback_html=CONTACTS_FALLBACK,
        reply_markup=contacts_kb(SHOP_MAPS_URL),
    )


@router.callback_query(F.data == "cta")
async def cb_cta(callback: CallbackQuery) -> None:
    from rich.client import send_rich
    from texts.ru import FINAL_CTA_RICH, FINAL_CTA_FALLBACK

    await callback.answer()
    await send_rich(
        callback.bot,
        callback.from_user.id,
        rich_html=FINAL_CTA_RICH,
        fallback_html=FINAL_CTA_FALLBACK,
        reply_markup=final_cta_kb(),
    )
