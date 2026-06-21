import requests
from config.settings import FINNHUB_API_KEY

BASE_URL = "https://finnhub.io/api/v1"


def get_quote(symbol: str):
    try:
        url = f"{BASE_URL}/quote"

        params = {
            "symbol": symbol,
            "token": FINNHUB_API_KEY
        }

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        # Vérification sécurité
        if not data or "c" not in data:
            return None

        return {
            "current": data.get("c"),
            "high": data.get("h"),
            "low": data.get("l"),
            "open": data.get("o"),
            "previous_close": data.get("pc")
        }

    except Exception as e:
        print("Finnhub error:", e)
        return None
