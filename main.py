import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from config.settings import TELEGRAM_TOKEN, APP_NAME, VERSION
from services.finnhub_api import get_quote

from analysis.scoring import basic_score
from analysis.trend import detect_trend
from analysis.filters import signal_quality


# =======================
# ACTIFS
# =======================
BINARY_ASSETS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD"]
CLASSIC_ASSETS = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "NASDAQ"]


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

    await update.message.reply_text(
        f"""
{APP_NAME}
Version : {VERSION}

PredictHood Trading Engine

Statut : EN LIGNE

Choisis une option :
""",
        reply_markup=keyboard
    )


# =======================
# PRICE
# =======================
async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):

    symbol = "AAPL"
    data = get_quote(symbol)

    if not data:
        await update.message.reply_text("Données indisponibles.")
        return

    await update.message.reply_text(
        f"""
MARCHÉ

ACTIF : {symbol}
Prix : {data['current']}
Haut : {data['high']}
Bas : {data['low']}
"""
    )


# =======================
# SCANNER
# =======================
async def scanner(update: Update, context: ContextTypes.DEFAULT_TYPE):

    msg = "OPTION BINAIRE:\n" + "\n".join(BINARY_ASSETS)
    msg += "\n\nTRADING CLASSIQUE:\n" + "\n".join(CLASSIC_ASSETS)

    await update.message.reply_text(msg)


# =======================
# ANALYSE (SAFE VERSION V2)
# =======================
async def analyse(update: Update, context: ContextTypes.DEFAULT_TYPE):

    symbol = "AAPL"
    data = get_quote(symbol)

    if not data:
        await update.message.reply_text("Données indisponibles.")
        return

    current = data.get("current", 100)

    # mini logique stable (sans indicators externes)
    score = basic_score(data)
    trend = detect_trend(data)
    quality = signal_quality(score, trend)

    # simulation RSI simple (SAFE)
    rsi = 50
    if current > data.get("open", current):
        rsi = 60
    else:
        rsi = 40

    # décision améliorée
    if quality == "FORTE" and trend == "HAUSSIER":
        decision = "CALL"
    elif quality == "FORTE" and trend == "BAISSIER":
        decision = "PUT"
    else:
        decision = "ATTENTE"

    await update.message.reply_text(
        f"""
ANALYSE PREDICTHOOD

ACTIF : {symbol}

Tendance : {trend}
Score : {score}
RSI (estimé) : {rsi}
Qualité : {quality}

DÉCISION : {decision}
"""
    )


# =======================
# OPTION BINAIRE
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
        f"""
OPTION BINAIRE

ACTIF : {symbol}
Trend : {trend}
Score : {score}

Signal : {decision}
"""
    )


# =======================
# CLASSIQUE
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
        f"""
TRADING CLASSIQUE

ACTIF : {symbol}
Trend : {trend}
Score : {score}

Signal : {decision}
"""
    )


# =======================
# MENU ROUTER
# =======================
async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    if text == "📊 Analyse Marché":
        await analyse(update, context)

    elif text == "⚡ Option Binaire":
        await binary_analysis(update, context)

    elif text == "📈 Trading Classique":
        await classic_analysis(update, context)

    elif text == "📡 Scanner Actifs":
        await scanner(update, context)

    else:
        await update.message.reply_text("Option non reconnue.")


# =======================
# MAIN
# =======================
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))

    print("PredictHood running...")
    app.run_polling()


if __name__ == "__main__":
    main()
