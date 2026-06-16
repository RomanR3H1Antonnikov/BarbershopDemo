"""OpenAI client wrapper — text + vision, async streaming."""
from __future__ import annotations

from typing import AsyncIterator

from config import OPENAI_API_KEY
from ai.prompts import HAIRCUT_SYSTEM


async def stream_haircut_advice(
    user_text: str,
    image_url: str | None = None,
) -> AsyncIterator[str]:
    """
    Stream GPT response for haircut advice.
    Yields text chunks as they arrive.
    Falls back to a canned demo response if OPENAI_API_KEY is empty.
    """
    if not OPENAI_API_KEY:
        async for chunk in _demo_stream():
            yield chunk
        return

    import openai

    client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)

    content: list[dict] = []
    if image_url:
        content.append({
            "type": "image_url",
            "image_url": {"url": image_url, "detail": "low"},
        })
    content.append({"type": "text", "text": user_text or "Подбери стрижку."})

    stream = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": HAIRCUT_SYSTEM},
            {"role": "user", "content": content},
        ],
        stream=True,
        max_tokens=600,
        temperature=0.7,
    )

    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


async def get_file_url(bot, file_id: str) -> str | None:
    """Get a public URL for a Telegram file."""
    try:
        file = await bot.get_file(file_id)
        token = bot.token
        return f"https://api.telegram.org/file/bot{token}/{file.file_path}"
    except Exception:
        return None


async def _demo_stream():  # type: ignore[return]
    """Fallback when no API key is configured."""
    import asyncio

    text = (
        "Вот несколько вариантов под твой запрос:\n\n"
        "1. Фейд со средней длиной\n"
        "Универсально и аккуратно, отрастает плавно. "
        "Иди к Алексею — он специализируется на фейде.\n\n"
        "2. Классический помпадур\n"
        "Элегантно, хорошо для делового образа. "
        "Лучший вариант у Дмитрия.\n\n"
        "3. Андеркат\n"
        "Смелее, но очень популярно. "
        "Кирилл любит нестандартные запросы, справится отлично.\n\n"
        "Записывайся — мастер уточнит детали на месте 👇"
    )
    for word in text.split(" "):
        yield word + " "
        await asyncio.sleep(0.05)
