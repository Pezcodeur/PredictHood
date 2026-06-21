from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

from config.settings import TELEGRAM_TOKEN, APP_NAME, VERSION
from services.finnhub_api import get_quote

BINARY_ASSETS = [
    "EURUSD",
    "GBPUSD",
    "USDJPY",
    "AUDUSD",
    "USDCAD"
]

CLASSIC_ASSETS = [
    "XAUUSD",
    "EURUSD",
    "GBPUSD",
    "USDJPY",
    "NASDAQ"
]
MENU = [
    ["📊 Analyse Marché"],
    ["⚡ Option Binaire", "📈 Trading Classique"],
    ["📡 Scanner Actifs"],
    ["⚙️ Paramètres", "ℹ️ Aide"]
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(MENU, resize_keyboard=True, one_time_keyboard=False)

    message = f"""

{APP_NAME}
Version : {VERSION}

Système : PredictHood Trading Engine

Statut : EN LIGNE

Choisis un module :

- Analyse marché en temps réel
- Option Binaire (court terme)
- Trading Classique (Forex / Or)
- Scanner des actifs
- Paramètres & aide
"""

    await update.message.reply_text(message)


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))

    print("PredictHood running...")
    app.run_polling()


if __name__ == "__main__":
    main()
