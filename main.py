import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

from config.settings import TELEGRAM_TOKEN, APP_NAME, VERSION
from services.finnhub_api import get_quote

from analysis.scoring import basic_score
from analysis.trend import detect_trend
from analysis.filters import signal_quality


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

    keyboard = ReplyKeyboardMarkup(MENU, resize_keyboard=True)

    message = f"""
{APP_NAME}
Version : {VERSION}

PredictHood Trading Engine

Statut : EN LIGNE

Modules :
- Analyse Marché
- Option Binaire
- Trading Classique
- Scanner
"""

    await update.message.reply_text(message, reply_markup=keyboard)


# =======================
# PRICE
# =======================
async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):

    symbol = "AAPL"
    data = get_quote(symbol)

    if not data:
        await update.message.reply_text("Données indisponibles.")
        return

    message = f"""
MARCHÉ

ACTIF : {symbol}
Prix : {data['current']}
Haut : {data['high']}
Bas : {data['low']}
"""

    await update.message.reply_text(message)


# =======================
# SCANNER
# =======================
async def scanner(update: Update, context: ContextTypes.DEFAULT_TYPE):

    msg = "OPTION BINAIRE:\n"
    msg += "\n".join(BINARY_ASSETS)

    msg += "\n\nCLASSIQUE:\n"
    msg += "\n".join(CLASSIC_ASSETS)

    await update.message.reply_text(msg)


# =======================
# ANALYSE
# =======================
async def analyse(update: Update, context: ContextTypes.DEFAULT_TYPE):

    symbol = "AAPL"
    data = get_quote(symbol)

    if not data:
        await update.message.reply_text("Données indisponibles.")
        return

    score = basic_score(data)
    trend = detect_trend(data)
    quality = signal_quality(score, trend)

    if quality == "FORTE" and trend == "HAUSSIER":
        decision = "CALL"
    elif quality == "FORTE" and trend == "BAISSIER":
        decision = "PUT"
    else:
        decision = "ATTENTE"

    await update.message.reply_text(
        f"ANALYSE\n\n{symbol}\nTrend: {trend}\nScore: {score}\nSignal: {decision}"
    )


# =======================
# BINARY
# =======================
async def binary_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):

    symbol = "EURUSD"
    data = get_quote(symbol)

    if not data:
        await update.message.reply_text("Données indisponibles.")
        return

    score = basic_score(data)
    trend = detect_trend(data)

    if score >= 65 and trend == "HAUSSIER":
        decision = "CALL"
    elif score <= 35 and trend == "BAISSIER":
        decision = "PUT"
    else:
        decision = "ATTENTE"

    await update.message.reply_text(
        f"BINARY\n\n{symbol}\nTrend: {trend}\nScore: {score}\nSignal: {decision}"
    )


# =======================
# CLASSIC
# =======================
async def classic_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):

    symbol = "XAUUSD"
    data = get_quote(symbol)

    if not data:
        await update.message.reply_text("Données indisponibles.")
        return

    score = basic_score(data)
    trend = detect_trend(data)

    if score >= 60 and trend == "HAUSSIER":
        decision = "BUY"
    elif score <= 40 and trend == "BAISSIER":
        decision = "SELL"
    else:
        decision = "ATTENTE"

    await update.message.reply_text(
        f"CLASSIC\n\n{symbol}\nTrend: {trend}\nScore: {score}\nSignal: {decision}"
    )


# =======================
# MAIN
# =======================
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("scanner", scanner))
    app.add_handler(CommandHandler("analyse", analyse))
    app.add_handler(CommandHandler("binary", binary_analysis))
    app.add_handler(CommandHandler("classic", classic_analysis))

    print("PredictHood running...")
    app.run_polling()


if __name__ == "__main__":
    main()
