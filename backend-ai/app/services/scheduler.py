from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.macro_service import get_current_macro_summary
from app.data_sources.gdelt import fetch_gdelt_events
from app.services.data_lake_service import save_gdelt_to_lakehouse

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
    """Cykliczne pobieranie wiadomości RSS/NewsAPI do Data Lake."""
    print("🔄 [APScheduler] Pobieranie świeżych newsów do Data Lake...")
    from app.services.news_service import fetch_and_process_category
    for cat in CATEGORIES_TO_SYNC:
        try:
            fetch_and_process_category(cat)
        except Exception as e:
            print(f"❌ [APScheduler] Błąd dla kategorii {cat}: {e}")
    print("✅ [APScheduler] Data Lake zaktualizowany o najnowsze artykuły.")


def update_gdelt_batch():
    """Wsadowe pobieranie wydarzeń geopolitycznych z GDELT do Delta Lake."""
    print("🔄 [APScheduler] Wsadowe pobieranie danych geopolitycznych z GDELT...")
    try:
        events = fetch_gdelt_events(max_records=20)
        if events:
            save_gdelt_to_lakehouse(events)
            print(f"✅ [APScheduler] Zapisano {len(events)} rekordów GDELT w Delta Lake.")
    except Exception as e:
        print(f"❌ [APScheduler] Błąd potoku GDELT: {e}")


def update_macro_cache():
    """Wsadowe pobieranie wskaźników makroekonomicznych (FRED)."""
    print("🔄 [APScheduler] Wsadowe odświeżanie wskaźników makroekonomicznych (FRED)...")
    try:
        get_current_macro_summary()
        print("✅ [APScheduler] Dane makroekonomiczne FRED zaktualizowane w Delta Lake.")
    except Exception as e:
        print(f"❌ [APScheduler] Błąd odświeżania makroekonomii: {e}")


def start_scheduler():
    if scheduler.running:
        return

    # 1. Wsad makroekonomiczny FRED (co 60 min)
    scheduler.add_job(
        update_macro_cache,
        "interval",
        minutes=60,
        id="macro_cache_job",
        replace_existing=True,
        max_instances=1,
    )

    # 2. Wsad artykułów RSS i NewsAPI (co 15 min)
    scheduler.add_job(
        update_news_cache,
        "interval",
        minutes=15,
        id="news_cache_job",
        replace_existing=True,
        max_instances=1,
        next_run_time=datetime.now() + timedelta(seconds=3),
    )

    # 3. Wsad wydarzeń geopolitycznych GDELT (co 30 min)
    scheduler.add_job(
        update_gdelt_batch,
        "interval",
        minutes=30,
        id="gdelt_batch_job",
        replace_existing=True,
        max_instances=1,
        next_run_time=datetime.now() + timedelta(seconds=8),
    )

    scheduler.start()


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)