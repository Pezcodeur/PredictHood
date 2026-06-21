from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from analysis.scoring import basic_score
from config.settings import TELEGRAM_TOKEN, APP_NAME, VERSION
from services.finnhub_api import get_quote


# =======================
# ACTIFS
# =======================
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

# =======================
# MENU
# =======================
MENU = [
    ["📊 Analyse Marché"],
    ["⚡ Option Binaire", "📈 Trading Classique"],
    ["📡 Scanner Actifs"],
    ["⚙️ Paramètres", "ℹ️ Aide"]
]


# =======================
# START
# =======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = ReplyKeyboardMarkup(MENU, resize_keyboard=True, one_time_keyboard=False)

    message = f"""
{APP_NAME}
Version : {VERSION}

Système : PredictHood Trading Engine

Statut : EN LIGNE

Choisis un module :
- Analyse marché
- Option Binaire
- Trading Classique
- Scanner actifs
"""

    await update.message.reply_text(message, reply_markup=keyboard)


# =======================
# PRICE (TEST MARCHÉ)
# =======================
async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):

    symbol = "AAPL"

    data = get_quote(symbol)

    if not data:
        await update.message.reply_text("Erreur : données indisponibles.")
        return

    message = f"""
ANALYSE MARCHÉ

ACTIF : {symbol}

Prix : {data['current']}
Haut : {data['high']}
Bas : {data['low']}
Open : {data['open']}
Close : {data['previous_close']}
"""

    await update.message.reply_text(message)


# =======================
# SCANNER
# =======================
async def scanner(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = "SCANNER PREDICTHOOD\n\nOPTION BINAIRE\n"

    for asset in BINARY_ASSETS:
        message += f"- {asset}\n"

    message += "\nTRADING CLASSIQUE\n"

    for asset in CLASSIC_ASSETS:
        message += f"- {asset}\n"

    await update.message.reply_text(message)


# =======================
# MAIN
# =======================
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("scanner", scanner))

    print("PredictHood running...")
    app.run_polling()
async def analyse(update: Update, context: ContextTypes.DEFAULT_TYPE):

    symbol = "AAPL"

    data = get_quote(symbol)

    if not data:
        await update.message.reply_text("Données indisponibles.")
        return

    score = basic_score(data)

    # logique simple de décision
    if score >= 65:
        decision = "CALL"
    elif score <= 35:
        decision = "PUT"
    else:
        decision = "ATTENTE"

    message = f"""
ANALYSE PREDICTHOOD

ACTIF : {symbol}

Score : {score}/100

Décision : {decision}

Résumé :
- Analyse automatique du marché
- Basée sur volatilité et position du prix
"""

    await update.message.reply_text(message)

if __name__ == "__main__":
    main()
