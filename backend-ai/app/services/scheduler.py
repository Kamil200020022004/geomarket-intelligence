from apscheduler.schedulers.background import BackgroundScheduler
from app.services.finance_service import get_stock
from app.services.macro_service import get_current_macro_summary

scheduler = BackgroundScheduler()

CATEGORIES_TO_SYNC = [
    "gielda",
    "makroekonomia",
    "kryptowaluty",
    "geopolityka",
    "polska_gospodarka",
    "swiatowe_rynki"
]


def update_news_cache():
    """Cykliczne pobieranie wiadomości do Data Lake (0 tokenów Gemini)."""
    print("🔄 [APScheduler] Pobieranie świeżych newsów do Data Lake...")
    # Import lokalny zapobiega cyklicznym importom przy starcie
    from app.services.news_service import fetch_and_process_category
    for cat in CATEGORIES_TO_SYNC:
        try:
            fetch_and_process_category(cat)
        except Exception as e:
            print(f"❌ [APScheduler] Błąd dla kategorii {cat}: {e}")
    print("✅ [APScheduler] Data Lake zaktualizowany o najnowsze artykuły.")


def update_market_cache():
    print("🔄 [APScheduler] Automatyczne odświeżanie danych rynkowych...")
    try:
        get_current_macro_summary()
        for symbol in ["AAPL", "NVDA", "MSFT", "EURPLN=X"]:
            get_stock(symbol)
        print("✅ [APScheduler] Notowania rynkowe zaktualizowane.")
    except Exception as e:
        print(f"❌ [APScheduler] Błąd odświeżania notowań: {e}")


def start_scheduler():
    # Odświeżanie notowań co 60 minut
    scheduler.add_job(update_market_cache, "interval", minutes=60)
    # Odświeżanie newsów co 15 minut (wymaganie Kamila)
    scheduler.add_job(update_news_cache, "interval", minutes=15)
    
    scheduler.start()

    # Jednorazowe wstępne napełnienie bazy przy starcie
    try:
        update_news_cache()
    except Exception:
        pass