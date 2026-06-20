from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from config.settings import TELEGRAM_TOKEN, APP_NAME, VERSION

MENU = [
    ["Option Binaire"],
    ["Trading Classique"],
    ["Scanner"],
    ["Paramètres"],
    ["Aide"]
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(MENU, resize_keyboard=True)

    message = f"""
====================================
{APP_NAME}
Version : {VERSION}

Statut : En ligne

Bienvenue dans PredictHood.

Choisissez une option :
====================================
"""

    await update.message.reply_text(message, reply_markup=keyboard)


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("PredictHood running...")
    app.run_polling()


if __name__ == "__main__":
    main()
