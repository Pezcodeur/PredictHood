import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from config.settings import TELEGRAM_TOKEN, APP_NAME, VERSION
from analysis.engine import analyze_symbol


# =========================
# ACTIFS
# =========================
BINARY = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD"]
CLASSIC = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "NAS100"]


# =========================
# MENU
# =========================
MENU = [
    ["📊 Analyse Marché"],
    ["⚡ Option Binaire", "📈 Trading Classique"],
    ["📡 Scanner"]
]


# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = ReplyKeyboardMarkup(MENU, resize_keyboard=True)

    await update.message.reply_text(
        f"""
{APP_NAME}
Version : {VERSION}

🚀 PREDICTHOOD ENGINE V7

Statut : ONLINE
""",
        reply_markup=keyboard
    )


# =========================
# ANALYSE MARCHÉ
# =========================
async def analyse(update: Update, context: ContextTypes.DEFAULT_TYPE):

    symbol = "AAPL"
    result = analyze_symbol(symbol)

    if not result:
        await update.message.reply_text("Erreur données.")
        return

    await update.message.reply_text(f"""
📊 ANALYSE ENGINE

Actif : {result['symbol']}

Prix : {result['price']}
EMA Fast : {result['ema_fast']}
EMA Slow : {result['ema_slow']}
RSI : {result['rsi']}
Volatilité : {result['volatility']}

Score : {result['score']}/100
Signal : {result['signal']}
""")


# =========================
# OPTION BINAIRE
# =========================
async def binary(update: Update, context: ContextTypes.DEFAULT_TYPE):

    symbol = "EURUSD"
    result = analyze_symbol(symbol)

    if not result:
        await update.message.reply_text("Erreur données.")
        return

    signal = "ATTENTE"

    if result["score"] >= 75:
        signal = "CALL (1-3 MIN)"
    elif result["score"] <= 25:
        signal = "PUT (1-3 MIN)"

    await update.message.reply_text(f"""
⚡ OPTION BINAIRE

Actif : {symbol}
RSI : {result['rsi']}
Score : {result['score']}

Signal : {signal}
""")


# =========================
# TRADING CLASSIQUE
# =========================
async def classic(update: Update, context: ContextTypes.DEFAULT_TYPE):

    symbol = "XAUUSD"
    result = analyze_symbol(symbol)

    if not result:
        await update.message.reply_text("Erreur données.")
        return

    signal = "ATTENTE"

    if result["score"] >= 65:
        signal = "BUY"
    elif result["score"] <= 35:
        signal = "SELL"

    await update.message.reply_text(f"""
📈 TRADING CLASSIQUE

Actif : {symbol}
RSI : {result['rsi']}
Score : {result['score']}

Signal : {signal}
""")


# =========================
# ROUTER MENU
# =========================
async def router(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    if text == "📊 Analyse Marché":
        await analyse(update, context)

    elif text == "⚡ Option Binaire":
        await binary(update, context)

    elif text == "📈 Trading Classique":
        await classic(update, context)

    elif text == "📡 Scanner":
        await update.message.reply_text(
            "BINARY:\n" + "\n".join(BINARY) +
            "\n\nCLASSIC:\n" + "\n".join(CLASSIC)
        )


# =========================
# MAIN
# =========================
def main():

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, router))

    print("PredictHood V7 RUNNING...")

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
