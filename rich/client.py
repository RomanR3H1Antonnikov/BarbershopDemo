"""
Thin wrapper over Bot API 10.1 sendRichMessage / sendRichMessageDraft.

Strategy:
  1. Try bot.send_rich_message(InputRichMessage(html=...))
  2. On any error, fall back to bot.send_message(parse_mode="HTML") with
     stripped HTML (rich tags → plain equivalents via fallback.py).

This single adapter is the only place that calls raw rich API — when aiogram
ships a stable high-level interface we swap only here.
"""
from __future__ import annotations

import asyncio
import time
import logging

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, Message

from rich.fallback import strip_rich_tags

log = logging.getLogger(__name__)


async def send_rich(
    bot: Bot,
    chat_id: int | str,
    rich_html: str,
    fallback_html: str | None = None,
    reply_markup: InlineKeyboardMarkup | None = None,
    **kwargs,
) -> Message:
    """Send a rich message; fall back to HTML on failure."""
    _fallback = fallback_html or strip_rich_tags(rich_html)
    try:
        from aiogram.types import InputRichMessage  # type: ignore[attr-defined]
        return await bot.send_rich_message(
            chat_id=chat_id,
            rich_message=InputRichMessage(html=rich_html),
            reply_markup=reply_markup,
            **kwargs,
        )
    except Exception as exc:
        log.debug("sendRichMessage failed (%s), falling back to HTML", exc)
        return await bot.send_message(
            chat_id=chat_id,
            text=_fallback,
            parse_mode="HTML",
            reply_markup=reply_markup,
            **kwargs,
        )


async def stream_rich(
    bot: Bot,
    chat_id: int | str,
    text_chunks,  # AsyncIterator[str]
    placeholder: str = "⏳",
    reply_markup: InlineKeyboardMarkup | None = None,
) -> Message:
    """
    Stream text chunks into a Telegram message:
      - Sends initial placeholder.
      - Tries sendRichMessageDraft updates; falls back to edit_message_text.
      - Finalises with send_rich (rich) or send_message (plain).
    """
    # Send placeholder
    draft_msg: Message = await bot.send_message(chat_id=chat_id, text=placeholder)
    accumulated = ""
    last_edit = 0.0

    async for chunk in text_chunks:
        accumulated += chunk
        now = time.monotonic()
        if now - last_edit >= 1.2:  # throttle: ~1 edit/sec to avoid rate limits
            try:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=draft_msg.message_id,
                    text=accumulated + " ▌",
                )
                last_edit = now
            except Exception:
                pass  # keep streaming even if an edit fails

    # Delete the streaming placeholder and send the final rich message
    try:
        await bot.delete_message(chat_id=chat_id, message_id=draft_msg.message_id)
    except Exception:
        pass

    final_html = f"<p>{accumulated}</p>"
    return await send_rich(
        bot,
        chat_id,
        rich_html=final_html,
        fallback_html=accumulated,
        reply_markup=reply_markup,
    )
