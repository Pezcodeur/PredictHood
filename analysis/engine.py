from services.finnhub_api import get_quote


# =========================
# SAFE GET
# =========================
def safe(data, key, default=0):
    try:
        return data.get(key, default)
    except:
        return default


# =========================
# ENGINE CORE
# =========================
def analyze_symbol(symbol: str):

    data = get_quote(symbol)

    if not data:
        return None

    price = safe(data, "current", 0)
    high = safe(data, "high", 0)
    low = safe(data, "low", 0)

    # =========================
    # SIMULATION HISTORIQUE (TEMPORAIRE)
    # =========================
    history = [price * (1 + i * 0.001) for i in range(-20, 20)]

    # EMA simple
    ema_fast = sum(history[-10:]) / 10
    ema_slow = sum(history) / len(history)

    # RSI simplifié
    gains = 0
    losses = 0

    for i in range(1, len(history)):
        diff = history[i] - history[i - 1]
        if diff > 0:
            gains += diff
        else:
            losses += abs(diff)

    rsi = 100 if losses == 0 else 100 - (100 / (1 + gains / losses))

    # Volatilité simple
    volatility = (high - low) if high and low else 0

    # =========================
    # SCORE CONFLUENCE
    # =========================
    score = 50

    if ema_fast > ema_slow:
        score += 25
    else:
        score -= 25

    if rsi < 30:
        score += 20
    elif rsi > 70:
        score -= 20

    if volatility > 0:
        score += 5

    score = max(0, min(100, score))

    # =========================
    # SIGNAL
    # =========================
    if score >= 70:
        signal = "CALL / BUY"
    elif score <= 30:
        signal = "PUT / SELL"
    else:
        signal = "ATTENTE"

    # =========================
    # RETURN CLEAN DATA
    # =========================
    return {
        "symbol": symbol,
        "price": price,
        "ema_fast": round(ema_fast, 2),
        "ema_slow": round(ema_slow, 2),
        "rsi": round(rsi, 2),
        "volatility": round(volatility, 2),
        "score": score,
        "signal": signal
  }
