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
