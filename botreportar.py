# bot.py
# Requisitos:
#   pip install -U python-telegram-bot
#
# Ejecutar:
#   python bot.py

import json
import time

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

# ─────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────

TOKEN = "8078893425:AAH7MJXXWPI3-sIshPJVE7G1c4H3UOEroy8"

# Grupo donde llegan los tickets
TICKETS_GROUP_ID = -1003575621343

# MiniApps
WEBAPP_APUESTON_URL = "https://proyectomkk-sys.github.io/BotSoporteMKK/apueston.html"
# (esta miniapp abre desde apueston.html → reportar.html)
# no se usa directamente aquí, pero la dejo por claridad
WEBAPP_REPORTAR_URL = "https://proyectomkk-sys.github.io/BotSoporteMKK/reportarerror.html"

# Relación: mensaje del ticket en el grupo -> user_id del cliente
TICKET_MAP = {}

# ─────────────────────────────
# /start
# ─────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Bienvenido al servicio automatizado de recargas.\n"
        "Seleccione la plataforma que desea cargar:"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text="🅰️ Apueston",
                web_app=WebAppInfo(url=WEBAPP_APUESTON_URL)
            )
        ]
    ])

    await update.message.reply_text(text, reply_markup=keyboard)

# ─────────────────────────────
# UTILIDAD
# ─────────────────────────────

def format_user(user: dict) -> str:
    if not user:
        return "Desconocido"
    full = " ".join(
        [user.get("first_name", ""), user.get("last_name", "")]
    ).strip()
    username = user.get("username") or "sin_username"
    uid = user.get("id")
    return f"{full} | @{username} | id:{uid}"

# ─────────────────────────────
# RECIBIR DATOS DESDE MINIAPP
# ─────────────────────────────

async def on_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    wad = msg.web_app_data
    if not wad:
        return

    try:
        payload = json.loads(wad.data)
    except Exception:
        await msg.reply_text("❌ Error al procesar el reporte.")
        return

    if payload.get("type") != "reporte_falla":
        return

    user = payload.get("user") or {}
    description = (payload.get("description") or "").strip()
    has_shot = bool(payload.get("hasScreenshot"))
    ts = int(payload.get("ts") or time.time() * 1000)

    user_id = user.get("id")
    if not user_id:
        await msg.reply_text("❌ Reporte inválido. Abre la miniapp desde Telegram.")
        return

    ticket_text = (
        "🎫 **TICKET NUEVO**\n"
        f"👤 **Usuario:** {format_user(user)}\n"
        f"🕒 **Timestamp:** `{ts}`\n"
        f"📎 **Captura:** {'Sí (pendiente backend)' if has_shot else 'No'}\n\n"
        f"📝 **Descripción:**\n{description}"
    )

    sent = await context.bot.send_message(
        chat_id=TICKETS_GROUP_ID,
        text=ticket_text,
        parse_mode="Markdown"
    )

    # Guardamos relación ticket -> usuario
    TICKET_MAP[sent.message_id] = int(user_id)

    await msg.reply_text(
        "✅ Reporte enviado correctamente.\n"
        "Un agente se comunicará contigo por este chat."
    )

# ─────────────────────────────
# RESPONDER TICKETS DESDE EL GRUPO
# ─────────────────────────────
# Uso:
#   Responder al mensaje del ticket y escribir:
#   /r texto de respuesta

async def reply_to_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message

    # Solo en el grupo de tickets
    if msg.chat_id != TICKETS_GROUP_ID:
        return

    if not msg.text or not msg.text.startswith("/r"):
        return

    if not msg.reply_to_message:
        await msg.reply_text(
            "⚠️ Responde al mensaje del ticket y escribe:\n"
            "/r tu respuesta"
        )
        return

    ticket_mid = msg.reply_to_message.message_id
    user_id = TICKET_MAP.get(ticket_mid)

    if not user_id:
        await msg.reply_text(
            "⚠️ No se encontró el usuario de este ticket.\n"
            "Posible reinicio del bot."
        )
        return

    answer = msg.text[2:].strip()
    if not answer:
        await msg.reply_text("⚠️ Escribe una respuesta luego de /r")
        return

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"🛠️ Soporte:\n{answer}"
        )
        await msg.reply_text("✅ Respuesta enviada al usuario.")
    except Exception:
        await msg.reply_text(
            "❌ No pude enviar el mensaje al usuario.\n"
            "El usuario debe haber iniciado chat con el bot."
        )

# ─────────────────────────────
# MAIN
# ─────────────────────────────

def main():
    app = Application.builder().token(TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start", start))

    # Datos desde MiniApps
    app.add_handler(
        MessageHandler(filters.StatusUpdate.WEB_APP_DATA, on_webapp_data)
    )

    # Responder tickets desde el grupo
    app.add_handler(
        MessageHandler(filters.TEXT & (~filters.COMMAND) | filters.COMMAND, reply_to_ticket)
    )

    print("🤖 Bot iniciado correctamente...")
    app.run_polling()

if __name__ == "__main__":
    main()
