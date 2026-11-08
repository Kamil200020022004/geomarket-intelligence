from datetime import datetime, timedelta
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
    "swiatowe_rynki",
]


def update_news_cache():
    """Cykliczne pobieranie wiadomości do Data Lake w tle."""
    print("🔄 [APScheduler] Pobieranie świeżych newsów do Data Lake...")
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
    if scheduler.running:
        return

    scheduler.add_job(
        update_market_cache,
        "interval",
        minutes=60,
        id="market_cache_job",
        replace_existing=True,
        max_instances=1,
    )
    scheduler.add_job(
        update_news_cache,
        "interval",
        minutes=15,
        id="news_cache_job",
        replace_existing=True,
        max_instances=1,
        next_run_time=datetime.now() + timedelta(seconds=3),
    )
    scheduler.start()


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)