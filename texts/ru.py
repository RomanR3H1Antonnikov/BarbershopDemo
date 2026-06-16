SHOP_NAME = "BRUTAL CUTS"
SHOP_ADDRESS = "ул. Примерная, 42, этаж 2"
SHOP_PHONE = "+7 (999) 123-45-67"
SHOP_HOURS = "Пн–Сб: 10:00–21:00"
SHOP_INSTAGRAM = "@brutal_cuts_demo"
SHOP_MAPS_URL = "https://maps.google.com/?q=55.7558,37.6173"

WELCOME = (
    "<b>BRUTAL CUTS ✂️</b>\n\n"
    "Барбершоп в центре города. Мастера с опытом, без очередей — "
    "только качество и точно в срок.\n\n"
    "Записывайся за 60 секунд 👇"
)

# ── Booking flow ──────────────────────────────────────────────────────────────

BOOKING_CHOOSE_MASTER = (
    "👇 <b>Выбери мастера</b>\n\n"
    "Листай карточки — у каждого своя специализация."
)

BOOKING_CHOOSE_SERVICE = (
    "✂️ <b>Выбери услугу</b>\n\n"
    "Мастер: <b>{master_name}</b>"
)

BOOKING_CHOOSE_DATE = (
    "📅 <b>Выбери дату</b>\n\n"
    "Мастер: <b>{master_name}</b>\n"
    "Услуга: <b>{service_name}</b>"
)

BOOKING_NO_SLOTS_ON_DATE = (
    "😔 На <b>{date}</b> у мастера нет свободных окон.\n"
    "Выбери другую дату:"
)

BOOKING_CHOOSE_SLOT = (
    "⏰ <b>Выбери время</b>\n\n"
    "Мастер: <b>{master_name}</b>\n"
    "Услуга: <b>{service_name}</b>\n"
    "Дата: <b>{date}</b>"
)

BOOKING_CONFIRM = (
    "✅ <b>Проверь запись</b>\n\n"
    "👤 Мастер: <b>{master_name}</b>\n"
    "✂️ Услуга: <b>{service_name}</b>\n"
    "📅 Дата: <b>{date}</b>\n"
    "⏰ Время: <b>{time}</b>\n"
    "💰 Цена: <b>{price} ₽</b>\n\n"
    "Всё верно?"
)

BOOKING_SUCCESS = (
    "🎉 <b>Запись подтверждена!</b>\n\n"
    "👤 {master_name}\n"
    "✂️ {service_name}\n"
    "📅 {date} в {time}\n"
    "💰 {price} ₽\n\n"
    "📍 <b>{address}</b>\n\n"
    "Напомню за день и за час — жди уведомление ⏰"
)

BOOKING_CANCELLED = "❌ Запись отменена. Вернуться в меню?"

REMINDER_DAY_BEFORE = (
    "⏰ <b>Напоминание</b>\n\n"
    "Завтра у тебя запись:\n"
    "👤 {master_name} · ✂️ {service_name}\n"
    "⏰ {time} · 📍 {address}\n\n"
    "До встречи!"
)

REMINDER_HOUR_BEFORE = (
    "⏰ <b>Через час</b> у тебя запись!\n\n"
    "👤 {master_name} · ✂️ {service_name}\n"
    "⏰ {time} · 📍 {address}"
)

# ── Services ─────────────────────────────────────────────────────────────────

SERVICES_TITLE = "✂️ <b>Услуги и цены</b>"

def services_rich_html(rows: list[dict]) -> str:
    rows_html = "".join(
        f"<tr><td>{r['name']}</td><td>{r['duration_min']} мин</td>"
        f"<td><b>{r['price']} ₽</b></td></tr>"
        for r in rows
    )
    return (
        "<h2>Услуги и цены — BRUTAL CUTS</h2>"
        "<table>"
        "<tr><th>Услуга</th><th>Время</th><th>Цена</th></tr>"
        f"{rows_html}"
        "</table>"
        "<p>Запись через кнопку ниже — бесплатно и без звонков.</p>"
    )

def services_fallback_html(rows: list[dict]) -> str:
    lines = [f"<b>✂️ Услуги и цены — {SHOP_NAME}</b>\n"]
    lines.append("─────────────────────")
    for r in rows:
        lines.append(f"• <b>{r['name']}</b> — {r['duration_min']} мин · {r['price']} ₽")
    lines.append("─────────────────────")
    lines.append("Запись через кнопку ниже 👇")
    return "\n".join(lines)

# ── Portfolio ────────────────────────────────────────────────────────────────

PORTFOLIO_TITLE = "📸 <b>Наши работы</b>"

PORTFOLIO_CATEGORIES = [
    {"id": "fade", "emoji": "💈", "label": "Фейд / Тейп"},
    {"id": "classic", "emoji": "✂️", "label": "Классика"},
    {"id": "beard", "emoji": "🧔", "label": "Борода"},
    {"id": "kids", "emoji": "👦", "label": "Детская"},
]

PORTFOLIO_INTRO_RICH = (
    "<h2>Наши работы</h2>"
    "<p>Выбери категорию — покажем примеры работ наших мастеров.</p>"
)

PORTFOLIO_REVIEWS_RICH = (
    "<h3>Отзывы клиентов</h3>"
    "<blockquote>«Алексей — лучший! Фейд точный, с первого раза угадал что хочу.»\n"
    "— Денис К., постоянный клиент</blockquote>"
    "<blockquote>«Привожу сына к Кириллу уже год. Ребёнок сам просится — значит нравится!»\n"
    "— Мария Т.</blockquote>"
    "<blockquote>«Дмитрий сделал бороду идеально под форму лица. Теперь только к нему.»\n"
    "— Игорь В.</blockquote>"
)

PORTFOLIO_REVIEWS_FALLBACK = (
    "⭐️ <b>Отзывы клиентов</b>\n\n"
    "«Алексей — лучший! Фейд точный, с первого раза угадал что хочу.»\n"
    "<i>— Денис К., постоянный клиент</i>\n\n"
    "«Привожу сына к Кириллу уже год. Ребёнок сам просится — значит нравится!»\n"
    "<i>— Мария Т.</i>\n\n"
    "«Дмитрий сделал бороду идеально под форму лица. Теперь только к нему.»\n"
    "<i>— Игорь В.</i>"
)

# ── AI Haircut ────────────────────────────────────────────────────────────────

AI_INTRO = (
    "🤖 <b>Подбор стрижки с AI</b>\n\n"
    "Опиши, что хочешь — или пришли фото своей текущей причёски.\n\n"
    "<i>Например: «хочу что-то аккуратное, отрастает редко, лицо круглое»</i>"
)

AI_THINKING = "🤖 Подбираю варианты стрижки..."

AI_ERROR = (
    "😔 AI-ассистент временно недоступен.\n"
    "Можешь записаться напрямую — мастер подберёт стрижку на месте!"
)

# ── Contacts ─────────────────────────────────────────────────────────────────

CONTACTS_RICH = (
    "<h2>Контакты BRUTAL CUTS</h2>"
    f"<p>📍 <b>Адрес:</b> {SHOP_ADDRESS}</p>"
    f"<p>📞 <b>Телефон:</b> {SHOP_PHONE}</p>"
    f"<p>📸 <b>Instagram:</b> {SHOP_INSTAGRAM}</p>"
    f"<p>🕐 <b>Режим работы:</b> {SHOP_HOURS}</p>"
    "<p>Записывайся прямо в боте — никаких звонков!</p>"
)

CONTACTS_FALLBACK = (
    f"📍 <b>{SHOP_NAME}</b>\n\n"
    f"🏠 {SHOP_ADDRESS}\n"
    f"📞 {SHOP_PHONE}\n"
    f"📸 {SHOP_INSTAGRAM}\n"
    f"🕐 {SHOP_HOURS}"
)

# ── Admin panel ───────────────────────────────────────────────────────────────

ADMIN_WELCOME = "👋 <b>Панель мастера</b>\n\nВыбери раздел:"

ADMIN_NO_BOOKINGS_TODAY = "📋 На сегодня записей нет."

def admin_schedule_rich(bookings: list[dict]) -> str:
    if not bookings:
        return "<h2>Расписание на сегодня</h2><p>Записей нет — день свободный!</p>"
    rows = "".join(
        f"<tr><td>{b['time']}</td><td>{b['master_name']}</td>"
        f"<td>{b['service_name']}</td><td>{b['user_name'] or 'Клиент'}</td></tr>"
        for b in bookings
    )
    return (
        "<h2>Расписание на сегодня</h2>"
        "<table>"
        "<tr><th>Время</th><th>Мастер</th><th>Услуга</th><th>Клиент</th></tr>"
        f"{rows}"
        "</table>"
    )

def admin_schedule_fallback(bookings: list[dict]) -> str:
    if not bookings:
        return "📋 На сегодня записей нет."
    lines = ["📋 <b>Расписание на сегодня</b>\n"]
    for b in bookings:
        lines.append(
            f"⏰ <b>{b['time']}</b> — {b['master_name']}\n"
            f"   ✂️ {b['service_name']} · 👤 {b['user_name'] or 'Клиент'}"
        )
    return "\n\n".join(lines)

def admin_stats_rich(stats: dict) -> str:
    fill_pct = int(stats["filled_slots"] / max(stats["total_slots"], 1) * 100)
    return (
        "<h2>Статистика</h2>"
        "<table>"
        "<tr><th>Показатель</th><th>Значение</th></tr>"
        f"<tr><td>Записей сегодня</td><td><b>{stats['today']}</b></td></tr>"
        f"<tr><td>Записей за неделю</td><td><b>{stats['week']}</b></td></tr>"
        f"<tr><td>Заполненность</td><td><b>{fill_pct}%</b></td></tr>"
        f"<tr><td>Свободных слотов</td><td><b>{stats['total_slots'] - stats['filled_slots']}</b></td></tr>"
        "</table>"
        "<p><i>Можем подключить автонапоминания, рассылки и выгрузку в CRM — "
        "напиши нам!</i></p>"
    )

def admin_stats_fallback(stats: dict) -> str:
    fill_pct = int(stats["filled_slots"] / max(stats["total_slots"], 1) * 100)
    return (
        "📊 <b>Статистика</b>\n\n"
        f"Записей сегодня: <b>{stats['today']}</b>\n"
        f"Записей за неделю: <b>{stats['week']}</b>\n"
        f"Заполненность: <b>{fill_pct}%</b>\n"
        f"Свободных слотов: <b>{stats['total_slots'] - stats['filled_slots']}</b>\n\n"
        "<i>💡 Можем подключить автонапоминания, рассылки и выгрузку в CRM!</i>"
    )

# ── CTA (upsell) ──────────────────────────────────────────────────────────────

FINAL_CTA_RICH = (
    "<h2>Понравилось? Это всего лишь демо.</h2>"
    "<p>Мы соберём такого бота под ваш барбершоп — с вашими мастерами, "
    "услугами и фишками. А ещё умеем:</p>"
    "<p>🌐 сайт-витрину барбершопа</p>"
    "<p>📞 AI-ассистента, который примет звонок и запишет клиента голосом</p>"
    "<p>⚙️ автоматизацию: напоминания, рассылки, выгрузку клиентов</p>"
    "<p>💬 тот же бот в MAX как второй канал</p>"
    "<p>Первый созвон бесплатно, отвечаем за 2 часа.</p>"
)

FINAL_CTA_FALLBACK = (
    "✨ <b>Понравилось? Это всего лишь демо.</b>\n\n"
    "Мы соберём такого бота под ваш барбершоп — с вашими мастерами и фишками.\n\n"
    "А ещё умеем:\n"
    "🌐 сайт-витрину барбершопа\n"
    "📞 AI-ассистента, который примет звонок и запишет голосом\n"
    "⚙️ автоматизацию: напоминания, рассылки, выгрузку клиентов\n"
    "💬 тот же бот в MAX как второй канал\n\n"
    "Первый созвон бесплатно, отвечаем за 2 часа 👇"
)

ADMIN_ACCESS_DENIED = "🔒 Этот раздел только для мастеров."
