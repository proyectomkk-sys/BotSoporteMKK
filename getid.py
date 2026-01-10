from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8078893425:AAH7MJXXWPI3-sIshPJVE7G1c4H3UOEroy8"

async def getid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    await update.message.reply_text(
        f"✅ Chat detectado\n"
        f"Nombre: {chat.title or chat.username or 'Privado'}\n"
        f"Tipo: {chat.type}\n"
        f"chat_id: {chat.id}"
    )

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("getid", getid))
    print("Listo. Envía /getid en el grupo y te devuelvo el chat_id.")
    app.run_polling()

if __name__ == "__main__":
    main()
