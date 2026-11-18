"""Test obciążeniowy bramki API (Locust).

Symulowani użytkownicy przeglądają zakładki z danymi rynkowymi, a część z nich jest zalogowana
i korzysta z ulubionych. Trasy AI (czat, analizy) są pominięte — mierzyłyby szybkość zewnętrznego
modelu Gemini, a nie bramki.

Uruchomienie (API musi działać, np. w Docker Compose; z katalogu backend/):
    locust -f perf/locustfile.py --host http://localhost:8000 --headless -u 50 -r 10 -t 2m --csv perf/wyniki/api_50

Uwaga: wszyscy wirtualni użytkownicy mają ten sam adres IP, więc na czas testu limity zapytań
muszą być wyłączone (RATE_LIMIT_ENABLED=false) — inaczej logowanie dostaje 429 po 10 próbach.
"""

import random
import uuid

from locust import HttpUser, between, task

FAVORITE_TYPES = ("stock", "crypto", "macro")


class Visitor(HttpUser):
    """Niezalogowany użytkownik oglądający zakładki (przerwa 1–3 s między kliknięciami)."""

    weight = 3
    wait_time = between(1, 3)

    @task(3)
    def dashboard(self):
        self.client.get("/api/dashboard/markets")

    @task(3)
    def stocks(self):
        self.client.get("/api/stocks")

    @task(3)
    def crypto(self):
        self.client.get("/api/crypto/top")

    @task(2)
    def macro(self):
        self.client.get("/api/macro")


class LoggedInUser(HttpUser):
    """Zalogowany użytkownik: rejestracja i logowanie na starcie, potem /me i ulubione."""

    weight = 1
    wait_time = between(1, 3)

    def on_start(self):
        email = f"perf-{uuid.uuid4().hex[:12]}@example.com"
        password = "haslo-testowe-123"
        self.client.post("/auth/register", json={"name": "Perf", "email": email, "password": password},
                         name="/auth/register")
        response = self.client.post("/auth/login", json={"email": email, "password": password}, name="/auth/login")
        token = response.json().get("access_token", "") if response.ok else ""
        self.headers = {"Authorization": f"Bearer {token}"}

    @task(3)
    def me(self):
        self.client.get("/auth/me", headers=self.headers)

    @task(2)
    def list_favorites(self):
        favorite_type = random.choice(FAVORITE_TYPES)
        self.client.get(f"/api/favorites/{favorite_type}", headers=self.headers, name="/api/favorites/[type]")

    @task(1)
    def toggle_favorite(self):
        symbol = random.choice(["AAPL", "PKN", "MSFT", "CDR"])
        self.client.post("/api/favorites/stock", json={"symbol": symbol, "name": symbol}, headers=self.headers,
                         name="/api/favorites/stock (POST)")
        self.client.delete(f"/api/favorites/stock/{symbol}", headers=self.headers,
                           name="/api/favorites/stock/[id] (DELETE)")

    @task(2)
    def stocks(self):
        self.client.get("/api/stocks")
