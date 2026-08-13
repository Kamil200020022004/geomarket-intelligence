from apscheduler.schedulers.background import BackgroundScheduler
from app.services.finance_service import get_stock
from app.services.macro_service import get_current_macro_summary

scheduler = BackgroundScheduler()


def update_market_cache():
    print("🔄 [APScheduler] Automatyczne odświeżanie danych w tle...")
    try:
        # Odświeżenie danych makro
        get_current_macro_summary()
        # Odświeżenie notowań głównych walorów
        for symbol in ["AAPL", "NVDA", "MSFT", "EURPLN=X"]:
            get_stock(symbol)
        print("✅ [APScheduler] Cache danych został pomyślnie zaktualizowany.")
    except Exception as e:
        print(f"❌ [APScheduler] Błąd odświeżania danych: {e}")


def start_scheduler():
    # Uruchamiamy zadanie co 60 minut
    scheduler.add_job(update_market_cache, "interval", minutes=60)
    scheduler.start()
    