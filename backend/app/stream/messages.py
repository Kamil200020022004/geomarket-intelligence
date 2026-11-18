"""Format wiadomości w Kafce (koperta / envelope).

Każda wiadomość to JSON w jednej kopercie, niezależnie od źródła:

    {
      "schema_version": 1,
      "kind": "bars" | "instrument_info" | "coins_markets",
      "source": "yahoo" | "coingecko",
      "symbol": "PKN",             # symbol w API/frontendzie (dla coingecko: "top100")
      "source_symbol": "PKN.WA",   # symbol w źródle
      "fetched_at": "...Z",        # kiedy producent pobrał dane ze źródła (UTC)
      "payload": {...}             # surowe dane ze źródła, zależne od `kind`
    }

Kluczem wiadomości jest `symbol` — wiadomości jednego instrumentu trafiają zawsze do tej samej
partycji, więc konsument widzi je w kolejności wysłania.
"""

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any, Literal

SCHEMA_VERSION = 1

Kind = Literal["bars", "instrument_info", "coins_markets"]


class InvalidMessageError(ValueError):
    pass


@dataclass(frozen=True)
class Envelope:
    kind: Kind
    source: str
    symbol: str
    source_symbol: str
    fetched_at: str
    payload: dict[str, Any]
    schema_version: int = SCHEMA_VERSION

    @property
    def key(self) -> bytes:
        return self.symbol.encode("utf-8")

    def to_bytes(self) -> bytes:
        return json.dumps(asdict(self), ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")

    @classmethod
    def from_bytes(cls, raw: bytes) -> "Envelope":
        try:
            data = json.loads(raw)
            if data.get("schema_version") != SCHEMA_VERSION:
                raise InvalidMessageError(f"nieobsługiwana wersja schematu: {data.get('schema_version')}")
            return cls(
                kind=data["kind"],
                source=data["source"],
                symbol=data["symbol"],
                source_symbol=data["source_symbol"],
                fetched_at=data["fetched_at"],
                payload=data["payload"],
            )
        except (ValueError, KeyError, TypeError) as error:
            raise InvalidMessageError(str(error)) from error


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"czas bez strefy: {value}")
    return parsed.astimezone(UTC)
