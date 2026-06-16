"""Degrade rich HTML to plain HTML/MarkdownV2 for older Telegram clients."""
import re


def strip_rich_tags(html: str) -> str:
    """Convert rich-only HTML tags to their plaintext/HTML equivalents."""
    # Headings → bold
    html = re.sub(r"<h[1-6]>(.*?)</h[1-6]>", r"<b>\1</b>", html, flags=re.DOTALL)
    # Details/summary → bold summary (always visible)
    html = re.sub(
        r"<details>\s*<summary>(.*?)</summary>(.*?)</details>",
        r"<b>\1</b>\n\2",
        html,
        flags=re.DOTALL,
    )
    # blockquote → italic with quotes
    html = re.sub(
        r"<blockquote>(.*?)</blockquote>",
        lambda m: "<i>" + m.group(1).strip() + "</i>",
        html,
        flags=re.DOTALL,
    )
    # Table → simple list (best effort)
    # Remove <table>, <thead>, <tbody>, <tr> wrappers; <td>/<th> → " | "
    html = re.sub(r"<t(?:able|head|body|foot)>", "", html)
    html = re.sub(r"</t(?:able|head|body|foot)>", "", html)
    html = re.sub(r"<tr>", "", html)
    html = re.sub(r"</tr>", "\n", html)
    html = re.sub(r"<t[dh]>(.*?)</t[dh]>", r"\1 | ", html, flags=re.DOTALL)
    # Remove remaining unknown tags
    html = re.sub(r"<(?!/?(?:b|i|u|s|code|pre|a|em|strong)\b)[^>]+>", "", html)
    # Collapse blank lines
    html = re.sub(r"\n{3,}", "\n\n", html)
    return html.strip()
