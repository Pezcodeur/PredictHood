def calculate_rsi(closes):
    if len(closes) < 14:
        return 50

    gains = []
    losses = []

    for i in range(1, 14):
        change = closes[i] - closes[i-1]
        if change > 0:
            gains.append(change)
        else:
            losses.append(abs(change))

    avg_gain = sum(gains) / 14 if gains else 0
    avg_loss = sum(losses) / 14 if losses else 1

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return round(rsi, 2)

def ema_direction(closes):
    if len(closes) < 21:
        return "NEUTRE"

    ema9 = sum(closes[-9:]) / 9
    ema21 = sum(closes[-21:]) / 21

    if ema9 > ema21:
        return "HAUSSIER"
    elif ema9 < ema21:
        return "BAISSIER"
    else:
        return "NEUTRE"
