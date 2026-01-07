from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# 🔑 REEMPLAZA con tu token REAL (entre comillas)
TOKEN = "8078893425:AAH7MJXXWPI3-sIshPJVE7G1c4H3UOEroy8"

# ✅ URLs públicas de tus miniapps (GitHub Pages recomendado)
WEBAPP_PROMOCIONES = "https://proyectomkk-sys.github.io/BotSoporteMKK/promociones.html"
WEBAPP_TUTORIALES  = "https://proyectomkk-sys.github.io/BotSoporteMKK/soporte.html"

# ✅ Agrega estas miniapps (ajusta a tus rutas reales)
WEBAPP_RECARGAS    = "https://proyectomkk-sys.github.io/BotSoporteMKK/recargas.html"
WEBAPP_COBROS      = "https://proyectomkk-sys.github.io/BotSoporteMKK/cobros.html"
WEBAPP_CAMBIOS     = "https://proyectomkk-sys.github.io/BotSoporteMKK/cambios.html"

# ✅ Miniapp para reportar falla (la que construiremos con formulario + captura + botón chatear)
WEBAPP_REPORTAR    = "https://proyectomkk-sys.github.io/BotSoporteMKK/reportar.html"


# ─────────────────────────────
# /start
# ─────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("ℹ️ Información", callback_data="menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Aquí encontrarás información y accesos rápidos a nuestros servicios.",
        reply_markup=reply_markup
    )


# ─────────────────────────────
# Menú principal
# ─────────────────────────────
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("🎁 Promociones", web_app=WebAppInfo(url=WEBAPP_PROMOCIONES))],
        [InlineKeyboardButton("📺 Tutoriales",  web_app=WebAppInfo(url=WEBAPP_TUTORIALES))],

        [InlineKeyboardButton("💳 Recargas",    web_app=WebAppInfo(url=WEBAPP_RECARGAS))],
        [InlineKeyboardButton("💰 Cobros",      web_app=WebAppInfo(url=WEBAPP_COBROS))],
        [InlineKeyboardButton("🔁 Cambios",     web_app=WebAppInfo(url=WEBAPP_CAMBIOS))],

        [InlineKeyboardButton("🚨 Reportar falla", web_app=WebAppInfo(url=WEBAPP_REPORTAR))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text="Selecciona una opción:",
        reply_markup=reply_markup
    )


# ─────────────────────────────
# MAIN
# ─────────────────────────────
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu, pattern="menu"))

    print("🤖 Bot iniciado...")
    app.run_polling()


if __name__ == "__main__":
    main()
