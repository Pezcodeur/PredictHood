def signal_quality(score, trend):
    """
    Filtre la qualité du signal
    """

    if trend == "NEUTRE":
        return "FAIBLE"

    if score >= 70 and trend == "HAUSSIER":
        return "FORTE"

    if score <= 30 and trend == "BAISSIER":
        return "FORTE"

    if (score >= 60 and trend == "BAISSIER") or (score <= 40 and trend == "HAUSSIER"):
        return "CONFLIT"

    return "MOYENNE"
