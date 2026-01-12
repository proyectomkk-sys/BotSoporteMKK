# bot.py
# Requisitos:
#   pip install -U python-telegram-bot
#
# Ejecutar:
#   python bot.py

import json
import time
import re
import logging
from typing import Optional

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────
TOKEN = "8078893425:AAH7MJXXWPI3-sIshPJVE7G1c4H3UOEroy8"

# Grupo donde llegan los tickets
TICKETS_GROUP_ID = -1003575621343

# MiniApp principal (GitHub Pages / hosting)
WEBAPP_APUESTON_URL = "https://proyectomkk-sys.github.io/BotSoporteMKK/apueston.html"

# Mapa: message_id del ticket en el grupo -> user_id del cliente
# (si el bot creó el ticket desde sendData, se llena; si el ticket vino del backend, quizá no)
TICKET_MAP: dict[int, int] = {}


# ─────────────────────────────
# MENSAJE DE BIENVENIDA + BOTÓN
# ─────────────────────────────
def welcome_text() -> str:
    return (
        "Bienvenido al servicio automatizado de recargas.\n"
        "Seleccione la plataforma que desea cargar:"
    )

def apueston_inline_keyboard() -> InlineKeyboardMarkup:
    # ⚠️ Si te vuelve a salir Button_type_invalid, ahí sí toca usar Menu Button (pero por ahora lo dejamos inline).
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text="🅰️ Apueston",
                web_app=WebAppInfo(url=WEBAPP_APUESTON_URL),
            )
        ]
    ])


# ─────────────────────────────
# /start
# ─────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        welcome_text(),
        reply_markup=apueston_inline_keyboard()
    )


# ─────────────────────────────
# CUALQUIER TEXTO EN PRIVADO → MISMO MENSAJE QUE /start
# ─────────────────────────────
async def welcome_on_any_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Solo en privado
    if update.effective_chat.type != "private":
        return

    # Ignorar comandos
    if not update.message or not update.message.text:
        return
    if update.message.text.startswith("/"):
        return

    await start(update, context)


# ─────────────────────────────
# UTILIDAD: extraer user_id del texto del ticket
# ─────────────────────────────
def extract_user_id_from_ticket(text: str) -> Optional[int]:
    """
    Busca patrones como:
      id:123456
      id: 123456
      id:1234567890
    """
    if not text:
        return None
    m = re.search(r"\bid\s*:\s*(\d{5,20})\b", text, re.IGNORECASE)
    if not m:
        return None
    return int(m.group(1))


# ─────────────────────────────
# RECIBIR DATOS DESDE MINIAPP via tg.sendData (OPCIONAL)
# Si ya envías reportes 100% por backend, esto puede quedarse igual (no molesta).
# ─────────────────────────────
async def on_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    wad = msg.web_app_data
    if not wad:
        return

    try:
        payload = json.loads(wad.data)
    except Exception:
        await msg.reply_text("❌ Error al procesar el reporte (JSON inválido).")
        return

    if payload.get("type") != "reporte_falla":
        return

    user = payload.get("user") or {}
    desc = (payload.get("description") or "").strip()
    has_shot = bool(payload.get("hasScreenshot"))
    ts = int(payload.get("ts") or time.time() * 1000)

    user_id = user.get("id")
    if not user_id:
        await msg.reply_text("❌ Reporte inválido. Abre la miniapp desde Telegram.")
        return

    full_name = " ".join([user.get("first_name", ""), user.get("last_name", "")]).strip() or "Sin nombre"
    username = user.get("username") or "sin_username"

    ticket_text = (
        "🎫 **TICKET NUEVO**\n"
        f"👤 **Usuario:** {full_name} | @{username} | id:{user_id}\n"
        f"🕒 **Timestamp:** `{ts}`\n"
        f"📎 **Captura:** {'Sí (pendiente backend)' if has_shot else 'No'}\n\n"
        f"📝 **Descripción:**\n{desc}"
    )

    sent = await context.bot.send_message(
        chat_id=TICKETS_GROUP_ID,
        text=ticket_text,
        parse_mode="Markdown"
    )

    # Guardamos ticket -> usuario (solo si el bot crea el ticket)
    TICKET_MAP[sent.message_id] = int(user_id)

    await msg.reply_text("✅ Reporte enviado. Te responderemos por este chat.")


# ─────────────────────────────
# RESPONDER TICKETS DESDE EL GRUPO
# Uso:
#   1) Responde (reply) al ticket y escribe: /r tu respuesta
#   2) Manual: /r 123456789 tu respuesta
# ─────────────────────────────
async def reply_to_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message

    # Solo en el grupo de tickets
    if msg.chat_id != TICKETS_GROUP_ID:
        return

    # Debe ser una respuesta (reply) a un ticket
    if not msg.reply_to_message:
        return

    # Ignorar comandos distintos a /r
    if msg.text and msg.text.startswith("/") and not msg.text.startswith("/r"):
        return

    # Texto del mensaje
    text = msg.text or ""
    text = text.strip()

    # Si viene con /r, lo quitamos
    if text.startswith("/r"):
        text = text[2:].strip()

    if not text:
        return

    # 1) Intento normal: mapa
    ticket_mid = msg.reply_to_message.message_id
    user_id = TICKET_MAP.get(ticket_mid)

    # 2) Extraer id del texto o caption del ticket
    if not user_id:
        user_id = extract_user_id_from_ticket(msg.reply_to_message.text or "")
        if not user_id:
            user_id = extract_user_id_from_ticket(
                getattr(msg.reply_to_message, "caption", "") or ""
            )

    # 3) Modo manual: primer token es id
    parts = text.split(maxsplit=1)
    if parts and parts[0].isdigit() and len(parts[0]) >= 5:
        user_id = int(parts[0])
        text = parts[1] if len(parts) > 1 else ""

    if not user_id or not text.strip():
        return

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"🛠️ Soporte:\n{text.strip()}"
        )
        await msg.reply_text("✅ Respuesta enviada al usuario por privado.")
    except Exception:
        await msg.reply_text(
            "❌ No pude enviarle mensaje al usuario.\n"
            "• El usuario no inició chat con el bot\n"
            "• Bloqueó el bot"
        )


# ─────────────────────────────
# ERROR HANDLER (evita 'No error handlers are registered')
# ─────────────────────────────
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Exception while handling an update:", exc_info=context.error)


# ─────────────────────────────
# MAIN
# ─────────────────────────────
def main() -> None:
    app = Application.builder().token(TOKEN).build()

    # /start
    app.add_handler(CommandHandler("start", start))

    # Cualquier texto (no comando) en privado -> muestra bienvenida + botón
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, welcome_on_any_text))

    # Recibir data desde miniapps via tg.sendData (si lo usas)
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, on_webapp_data))

    # Responder tickets desde el grupo con /r (solo actuará en el grupo indicado)
    app.add_handler(MessageHandler(filters.TEXT | filters.COMMAND, reply_to_ticket))

    app.add_error_handler(error_handler)

    print("🤖 Bot iniciado correctamente...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
