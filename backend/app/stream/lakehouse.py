"""Tabele Delta Lake domeny `market` (konwencja: backend/docs/konwencja_lakehouse.md).

Ścieżki: {LAKEHOUSE_ROOT}/{warstwa}/market/{tabela}. Jedynym piszącym jest konsument potoku
strumieniowego; API i potok wsadowy Patryka tylko czytają.
"""

from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

import pyarrow as pa
from deltalake import DeltaTable, QueryBuilder, write_deltalake
from deltalake.exceptions import TableNotFoundError

UTC_TS = pa.timestamp("us", tz="UTC")


@dataclass(frozen=True)
class TableSpec:
    layer: str
    name: str
    schema: pa.Schema
    partition_by: tuple[str, ...] = ()
    merge_keys: tuple[str, ...] = ()

    def path(self, root: Path) -> str:
        return str(root / self.layer / "market" / self.name)


BRONZE_RAW = TableSpec(
    "bronze",
    "raw_messages",
    pa.schema([
        ("topic", pa.string()), ("kafka_partition", pa.int32()), ("kafka_offset", pa.int64()),
        ("message_key", pa.string()), ("kind", pa.string()), ("source", pa.string()),
        ("fetched_at", UTC_TS), ("payload", pa.string()), ("parse_error", pa.string()),
        ("ingested_at", UTC_TS), ("ingest_date", pa.date32()),
    ]),
    partition_by=("ingest_date",),
)

SILVER_BARS = TableSpec(
    "silver",
    "bars",
    pa.schema([
        ("symbol", pa.string()), ("interval", pa.string()), ("ts", UTC_TS),
        ("open", pa.float64()), ("high", pa.float64()), ("low", pa.float64()), ("close", pa.float64()),
        ("volume", pa.float64()), ("source", pa.string()), ("fetched_at", UTC_TS),
        ("ingested_at", UTC_TS), ("date", pa.date32()),
    ]),
    partition_by=("date",),
    merge_keys=("date", "symbol", "interval", "ts"),
)

SILVER_INSTRUMENT_INFO = TableSpec(
    "silver",
    "instrument_info",
    pa.schema([
        ("symbol", pa.string()), ("shares", pa.float64()), ("currency", pa.string()), ("exchange", pa.string()),
        ("fetched_at", UTC_TS), ("ingested_at", UTC_TS),
    ]),
    merge_keys=("symbol",),
)

SILVER_CRYPTO = TableSpec(
    "silver",
    "crypto_markets",
    pa.schema([
        ("id", pa.string()), ("ts", UTC_TS), ("symbol", pa.string()), ("name", pa.string()),
        ("image", pa.string()), ("market_cap_rank", pa.int32()), ("price", pa.float64()),
        ("market_cap", pa.float64()), ("total_volume", pa.float64()),
        ("change_1h_pct", pa.float64()), ("change_24h_pct", pa.float64()), ("change_7d_pct", pa.float64()),
        ("sparkline_7d", pa.list_(pa.float64())), ("fetched_at", UTC_TS), ("ingested_at", UTC_TS),
        ("date", pa.date32()),
    ]),
    partition_by=("date",),
    merge_keys=("date", "id", "ts"),
)

GOLD_OHLC_1H = TableSpec(
    "gold",
    "ohlc_1h",
    pa.schema([
        ("symbol", pa.string()), ("ts", UTC_TS), ("open", pa.float64()), ("high", pa.float64()),
        ("low", pa.float64()), ("close", pa.float64()), ("volume", pa.float64()),
        ("last_ts", UTC_TS), ("ingested_at", UTC_TS),
    ]),
    merge_keys=("symbol", "ts"),
)

GOLD_LATEST_PRICES = TableSpec(
    "gold",
    "latest_prices",
    pa.schema([
        ("symbol", pa.string()), ("name", pa.string()), ("asset_class", pa.string()), ("currency", pa.string()),
        ("price", pa.float64()), ("change_1h_pct", pa.float64()), ("change_24h_pct", pa.float64()),
        ("change_7d_pct", pa.float64()), ("volume_24h", pa.float64()), ("market_cap", pa.float64()),
        ("ts", UTC_TS), ("ingested_at", UTC_TS),
    ]),
    merge_keys=("symbol",),
)

GOLD_CRYPTO_TOP = TableSpec("gold", "crypto_top", SILVER_CRYPTO.schema.remove(SILVER_CRYPTO.schema.get_field_index("date")))

GOLD_DIM_INSTRUMENT = TableSpec(
    "gold",
    "dim_instrument",
    pa.schema([
        ("symbol", pa.string()), ("name", pa.string()), ("asset_class", pa.string()), ("market", pa.string()),
        ("currency", pa.string()), ("unit", pa.string()), ("source", pa.string()), ("source_symbol", pa.string()),
        ("streamed", pa.bool_()), ("shares", pa.float64()), ("ingested_at", UTC_TS),
    ]),
)


def sql_str(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def sql_ts(value: datetime) -> str:
    return "TIMESTAMP '" + value.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S.%f") + "+00:00'"


def sql_date(value: date) -> str:
    return f"DATE '{value.isoformat()}'"


def sql_in(column: str, values: list[str]) -> str:
    return f"{column} IN ({', '.join(sql_str(v) for v in values)})" if values else "FALSE"


def read(root: Path, spec: TableSpec, where: str | None = None, columns: list[str] | None = None) -> list[dict]:
    """Odczyt tabeli Delta silnikiem SQL biblioteki delta-rs (DataFusion).

    Dlaczego nie `to_pyarrow_dataset()`: MERGE w delta-rs zapisuje kolumny tekstowe jako `string_view`,
    a filtry PyArrow Dataset nie porównują `string` ze `string_view` (błąd ArrowNotImplementedError).
    DataFusion czyta oba typy i korzysta z partycji (np. `date IN (...)` czyta tylko pasujące katalogi).
    Brak tabeli = pusta lista (np. przed pierwszym zapisem konsumenta).
    """
    table = open_table(root, spec)
    if table is None:
        return []
    select = ", ".join(columns) if columns else "*"
    sql = f"SELECT {select} FROM t" + (f" WHERE {where}" if where else "")
    reader = QueryBuilder().register("t", table).execute(sql)
    return pa.RecordBatchReader.from_stream(reader).read_all().to_pylist()


def to_table(spec: TableSpec, rows: list[dict]) -> pa.Table:
    return pa.Table.from_pylist(rows, schema=spec.schema)


def open_table(root: Path, spec: TableSpec) -> DeltaTable | None:
    try:
        return DeltaTable(spec.path(root))
    except TableNotFoundError:
        return None


def append(root: Path, spec: TableSpec, data: pa.Table) -> None:
    if data.num_rows:
        write_deltalake(spec.path(root), data, mode="append", partition_by=list(spec.partition_by) or None)


def overwrite(root: Path, spec: TableSpec, data: pa.Table) -> None:
    write_deltalake(spec.path(root), data, mode="overwrite", partition_by=list(spec.partition_by) or None)


def upsert(root: Path, spec: TableSpec, data: pa.Table) -> None:
    """MERGE po kluczu: istniejący wiersz → aktualizacja, nowy → wstawienie.

    To czyni zapis idempotentnym: ponowne przetworzenie tej samej wiadomości (np. po awarii
    konsumenta przed zatwierdzeniem offsetu) nie tworzy duplikatów.
    """
    if not data.num_rows:
        return
    data = _dedupe_last(data, spec.merge_keys)
    table = open_table(root, spec)
    if table is None:
        write_deltalake(spec.path(root), data, mode="append", partition_by=list(spec.partition_by) or None)
        return
    predicate = " AND ".join(f"t.{key} = s.{key}" for key in spec.merge_keys)
    (
        table.merge(source=data, predicate=predicate, source_alias="s", target_alias="t")
        .when_matched_update_all()
        .when_not_matched_insert_all()
        .execute()
    )


def _dedupe_last(data: pa.Table, keys: tuple[str, ...]) -> pa.Table:
    """W jednej paczce ten sam klucz może wystąpić kilka razy (zakładka okien) — zostaje ostatni wiersz.

    MERGE w Delta Lake wymaga, by każdy wiersz celu pasował do co najwyżej jednego wiersza źródła.
    """
    seen: dict[tuple, int] = {}
    columns = [data.column(key).to_pylist() for key in keys]
    for index, key in enumerate(zip(*columns, strict=True)):
        seen[key] = index  # późniejszy nadpisuje wcześniejszy
    if len(seen) == data.num_rows:
        return data
    return data.take(sorted(seen.values()))
