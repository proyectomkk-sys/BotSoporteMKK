from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# 🔑 REEMPLAZA con tu token REAL (entre comillas)
TOKEN = "8078893425:AAH7MJXXWPI3-sIshPJVE7G1c4H3UOEroy8"

# ✅ URL pública de tu miniapp (GitHub Pages recomendado)
WEBAPP_URL = "https://proyectomkk-sys.github.io/BotSoporteMKK/soporte.html"
WEBAPP_Promociones = "https://proyectomkk-sys.github.io/BotSoporteMKK/promociones.html"


# ─────────────────────────────
# /start
# ─────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("ℹ️ Información", callback_data="menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Aquí encontrarás las últimas promociones y tutoriales para aprovechar al máximo nuestros servicios. ",
        reply_markup=reply_markup
    )


# ─────────────────────────────
# Menú principal
# ─────────────────────────────
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("🎁 Promociones", web_app=WebAppInfo(url=WEBAPP_Promociones))],
        # ✅ Abre la WebApp directo (sin callback_data)
        [InlineKeyboardButton("📺 Tutoriales", web_app=WebAppInfo(url=WEBAPP_URL))],
        #[InlineKeyboardButton("🚨 Reportar una falla", callback_data="falla")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text="Selecciona una opción:",
        reply_markup=reply_markup
    )


# ─────────────────────────────
# Promociones
# ─────────────────────────────
async def promociones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "🎁 Promociones disponibles:\n\n"
        "✔ Bono de bienvenida\n"
        "✔ Giros gratis\n"
        "✔ Promos semanales"
    )


# ─────────────────────────────
# Reportar falla
# ─────────────────────────────
async def reportar_falla(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "🚨 Para reportar una falla, por favor envía:\n\n"
        "• Tipo de problema\n"
        "• Hora aproximada\n"
        "• Captura de pantalla (si es posible)"
    )


# ─────────────────────────────
# MAIN
# ─────────────────────────────
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu, pattern="menu"))
    app.add_handler(CallbackQueryHandler(promociones, pattern="promo"))
    app.add_handler(CallbackQueryHandler(reportar_falla, pattern="falla"))

    print("🤖 Bot de soporte iniciado...")
    app.run_polling()


if __name__ == "__main__":
    main()
