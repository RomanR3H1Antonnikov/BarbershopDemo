from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from states.flows import HaircutAI
from rich.client import stream_rich
from keyboards.client import book_now_kb, back_to_menu_kb, ai_waiting_kb
from texts.ru import AI_INTRO, AI_THINKING, AI_ERROR
from ai.client import stream_haircut_advice, get_file_url

router = Router(name="ai_haircut")


@router.callback_query(F.data == "ai_haircut")
async def cb_ai_haircut(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(HaircutAI.waiting_input)
    await callback.message.edit_text(
        AI_INTRO, parse_mode="HTML", reply_markup=ai_waiting_kb()
    )


@router.message(HaircutAI.waiting_input, F.text | F.photo)
async def handle_haircut_input(message: Message, state: FSMContext) -> None:
    await state.clear()

    user_text = message.caption or message.text or ""
    image_url: str | None = None

    if message.photo:
        largest = message.photo[-1]
        image_url = await get_file_url(message.bot, largest.file_id)
        if not user_text:
            user_text = "Подбери стрижку по этому фото."

    try:
        chunks = stream_haircut_advice(user_text, image_url)
        await stream_rich(
            bot=message.bot,
            chat_id=message.from_user.id,
            text_chunks=chunks,
            placeholder=AI_THINKING,
            reply_markup=book_now_kb(),
        )
    except Exception:
        await message.answer(AI_ERROR, parse_mode="HTML", reply_markup=book_now_kb())


@router.message(HaircutAI.waiting_input)
async def handle_haircut_wrong_type(message: Message, state: FSMContext) -> None:
    await message.answer(
        "Пришли текст или фото — я подберу стрижку 😊",
        reply_markup=ai_waiting_kb(),
    )
