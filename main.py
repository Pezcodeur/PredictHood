from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

from config.settings import TELEGRAM_TOKEN, APP_NAME, VERSION
from services.finnhub_api import get_quote


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


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Actif par défaut (on simplifie pour le test)
    symbol = "AAPL"

    data = get_quote(symbol)

    if not data:
        await update.message.reply_text("Erreur : données indisponibles.")
        return

    message = f"""
====================================
ANALYSE MARCHE - PredictHood

ACTIF : {symbol}

Prix actuel : {data['current']}
Haut : {data['high']}
Bas : {data['low']}
Open : {data['open']}
Clôture précédente : {data['previous_close']}

====================================
"""

    await update.message.reply_text(message)


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))

    print("PredictHood running...")
    app.run_polling()


if __name__ == "__main__":
    main()    print("PredictHood running...")
    app.run_polling()


if __name__ == "__main__":
    main()
