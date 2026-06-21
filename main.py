import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from config.settings import TELEGRAM_TOKEN, APP_NAME, VERSION
from services.finnhub_api import get_quote


# =========================
# SAFE
# =========================
def safe(data, key, default=0):
    try:
        return data.get(key, default)
    except:
        return default


# =========================
# EMA
# =========================
def ema(values, period=10):
    if not values:
        return 0

    k = 2 / (period + 1)
    e = values[0]

    for v in values:
        e = v * k + e * (1 - k)

    return e


# =========================
# RSI SIMPLE
# =========================
def rsi(values):
    if len(values) < 2:
        return 50

    gains = 0
    losses = 0

    for i in range(1, len(values)):
        diff = values[i] - values[i - 1]
        if diff > 0:
            gains += diff
        else:
            losses += abs(diff)

    if losses == 0:
        return 100

    rs = gains / losses
    return 100 - (100 / (1 + rs))


# =========================
# ATR SIMPLE
# =========================
def atr(high, low):
    if not high or not low:
        return 0

    return sum([h - l for h, l in zip(high, low)]) / len(high)


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

PREDICTHOOD V6 ENGINE

Statut : ONLINE
""",
        reply_markup=keyboard
    )


# =========================
# ENGINE SCORE
# =========================
def confluence_score(price, ema_fast, ema_slow, rsi_val, vol):

    score = 50

    # Trend EMA
    if ema_fast > ema_slow:
        score += 25
    else:
        score -= 25

    # RSI
    if rsi_val < 30:
        score += 20
    elif rsi_val > 70:
        score -= 20

    # Volatility filter
    if vol > 0:
        score += 5

    return max(0, min(100, score))


# =========================
# ANALYSE CORE
# =========================
async def analyse(update: Update, context: ContextTypes.DEFAULT_TYPE):

    symbol = "AAPL"
    data = get_quote(symbol)

    if not data:
        await update.message.reply_text("Erreur données.")
        return

    price = safe(data, "current", 100)

    history = [price * (1 + i * 0.001) for i in range(-15, 15)]

    ema_fast = ema(history[-10:])
    ema_slow = ema(history)

    rsi_val = rsi(history)

    vol = atr(history, history)

    score = confluence_score(price, ema_fast, ema_slow, rsi_val, vol)

    signal = "ATTENTE"

    if score >= 70:
        signal = "CALL"
    elif score <= 30:
        signal = "PUT"

    await update.message.reply_text(f"""
PREDICTHOOD V6 ANALYSE

Actif : {symbol}

Price : {price}
EMA Fast : {round(ema_fast,2)}
EMA Slow : {round(ema_slow,2)}
RSI : {round(rsi_val,2)}
Volatility : {round(vol,2)}

Score : {score}/100

SIGNAL : {signal}
""")


# =========================
# BINARY
# =========================
async def binary(update: Update, context: ContextTypes.DEFAULT_TYPE):

    symbol = "EURUSD"
    data = get_quote(symbol)

    if not data:
        await update.message.reply_text("Erreur données.")
        return

    price = safe(data, "current", 100)

    history = [price * (1 + i * 0.0008) for i in range(-15, 15)]

    ema_fast = ema(history[-10:])
    ema_slow = ema(history)

    rsi_val = rsi(history)

    score = confluence_score(price, ema_fast, ema_slow, rsi_val, 1)

    signal = "ATTENTE"

    if score >= 75:
        signal = "CALL (1-3 MIN)"
    elif score <= 25:
        signal = "PUT (1-3 MIN)"

    await update.message.reply_text(f"""
OPTION BINAIRE V6

Actif : {symbol}
RSI : {round(rsi_val,2)}
Score : {score}

SIGNAL : {signal}
""")


# =========================
# CLASSIC
# =========================
async def classic(update: Update, context: ContextTypes.DEFAULT_TYPE):

    symbol = "XAUUSD"
    data = get_quote(symbol)

    if not data:
        await update.message.reply_text("Erreur données.")
        return

    price = safe(data, "current", 100)

    history = [price * (1 + i * 0.0012) for i in range(-15, 15)]

    ema_fast = ema(history[-10:])
    ema_slow = ema(history)

    rsi_val = rsi(history)

    score = confluence_score(price, ema_fast, ema_slow, rsi_val, 1)

    signal = "ATTENTE"

    if score >= 65:
        signal = "BUY"
    elif score <= 35:
        signal = "SELL"

    await update.message.reply_text(f"""
TRADING CLASSIQUE V6

Actif : {symbol}
RSI : {round(rsi_val,2)}
Score : {score}

SIGNAL : {signal}
""")


# =========================
# ROUTER
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
        await update.message.reply_text("BINARY:\n" + "\n".join(BINARY) + "\n\nCLASSIC:\n" + "\n".join(CLASSIC))


# =========================
# MAIN
# =========================
def main():

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, router))

    print("PredictHood V6 RUNNING...")

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
