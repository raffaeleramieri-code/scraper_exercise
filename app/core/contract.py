"""Contratto dati tra la pipeline ETL e l'app.

Qui è scritto, in un solo posto, com'è fatto un file "cleaned" valido.
Il controllo dati dell'app usa queste regole per dire cosa non va.
Versione leggibile: docs/contratto_dati.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import polars as pl

INTEGER = "intero"
DECIMAL = "decimale"
TEXT = "testo"
DATE = "data"

ERROR = "errore"
WARNING = "avviso"

PRICE_COLUMNS = ["price_cardmarket", "price_tcgplayer", "price_coolstuffinc"]


@dataclass(frozen=True)
class Column:
    name: str
    kind: str
    nullable: bool
    description: str
    positive: bool = False  # se valorizzato deve essere > 0


@dataclass(frozen=True)
class Table:
    name: str
    columns: list[Column]
    key: list[str]  # colonne che identificano una riga: non possono ripetersi


def _prices() -> list[Column]:
    return [
        Column("price_cardmarket", DECIMAL, True, "prezzo Cardmarket in EUR", positive=True),
        Column("price_tcgplayer", DECIMAL, True, "prezzo TCGplayer in USD", positive=True),
        Column("price_coolstuffinc", DECIMAL, True, "prezzo CoolStuffInc in USD", positive=True),
    ]


CARDS = Table(
    "cards",
    [
        Column("card_id", INTEGER, False, "id della carta (campo `id` dell'API)"),
        Column("name", TEXT, False, "nome della carta"),
        Column("card_type", TEXT, False, "tipo di carta, es. 'Effect Monster', 'Spell Card' (campo `type`)"),
        Column("race", TEXT, False, "tipo del mostro, es. 'Dragon'; per magie/trappole es. 'Quick-Play'"),
        Column("attribute", TEXT, True, "elemento, es. 'DARK' (vuoto per magie e trappole)"),
        Column("level", INTEGER, True, "numero di stelle (livello o rango)"),
        Column("attack", INTEGER, True, "ATK (campo `atk`)"),
        Column("defense", INTEGER, True, "DEF (campo `def`)"),
        Column("image_url", TEXT, False, "URL dell'immagine oppure percorso relativo alla root del progetto"),
        *_prices(),
    ],
    key=["card_id"],
)

PRICE_HISTORY = Table(
    "price_history",
    [
        Column("date", DATE, False, "giorno in cui è stato letto il prezzo"),
        Column("card_id", INTEGER, False, "id della carta, deve esistere in cards"),
        *_prices(),
    ],
    key=["date", "card_id"],
)

TABLES = [CARDS, PRICE_HISTORY]


@dataclass
class Issue:
    level: str
    table: str
    column: str | None
    message: str


@dataclass
class Report:
    issues: list[Issue] = field(default_factory=list)

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.level == ERROR]

    @property
    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.level == WARNING]

    @property
    def ok(self) -> bool:
        return not self.errors

    def add(self, level: str, table: str, column: str | None, message: str) -> None:
        self.issues.append(Issue(level, table, column, message))


def kind_of(dtype: pl.DataType) -> str:
    """Traduce un dtype polars nelle famiglie del contratto."""
    if dtype.is_integer():
        return INTEGER
    if dtype.is_float():
        return DECIMAL
    if dtype == pl.String:
        return TEXT
    if dtype == pl.Date:
        return DATE
    return str(dtype)


def _check_table(df: pl.DataFrame, table: Table, report: Report) -> None:
    name = table.name
    if df.height == 0:
        report.add(ERROR, name, None, "la tabella è vuota")

    expected = {c.name for c in table.columns}
    for extra in sorted(set(df.columns) - expected):
        report.add(WARNING, name, extra, "colonna non prevista dal contratto: verrà ignorata")

    schema_ok = True
    for col in table.columns:
        if col.name not in df.columns:
            report.add(ERROR, name, col.name, f"colonna mancante (tipo atteso: {col.kind})")
            schema_ok = False
            continue

        found = kind_of(df.schema[col.name])
        if found != col.kind:
            report.add(ERROR, name, col.name, f"tipo sbagliato: atteso {col.kind}, trovato {found} ({df.schema[col.name]})")
            schema_ok = False
            continue

        series = df.get_column(col.name)
        nulls = series.null_count()
        if nulls and not col.nullable:
            report.add(ERROR, name, col.name, f"{nulls} valori nulli, ma la colonna è obbligatoria")

        if col.kind == TEXT:
            blanks = series.drop_nulls().str.strip_chars().eq("").sum()
            if blanks:
                report.add(ERROR, name, col.name, f"{blanks} stringhe vuote: usa null al loro posto")

        if col.positive:
            not_positive = series.drop_nulls().le(0).sum()
            if not_positive:
                report.add(ERROR, name, col.name, f"{not_positive} valori <= 0: un prezzo sconosciuto va salvato come null")

    if schema_ok:
        dupes = df.select(table.key).is_duplicated().sum()
        if dupes:
            report.add(ERROR, name, ", ".join(table.key), f"{dupes} righe con la stessa chiave ({' + '.join(table.key)})")


def _check_relations(cards: pl.DataFrame, history: pl.DataFrame, report: Report) -> None:
    orphans = history.join(cards.select("card_id"), on="card_id", how="anti").height
    if orphans:
        report.add(ERROR, "price_history", "card_id", f"{orphans} righe hanno un card_id che non esiste in cards")

    days = history.get_column("date").n_unique()
    if days < 2:
        report.add(WARNING, "price_history", "date", f"c'è solo {days} giorno: per vedere un andamento servono più giorni")

    last_day = history.get_column("date").max()
    missing = cards.join(history.filter(pl.col("date") == last_day), on="card_id", how="anti").height
    if missing:
        report.add(WARNING, "price_history", "card_id", f"{missing} carte non hanno un prezzo nell'ultimo giorno ({last_day})")

    latest = (
        history.filter(pl.col("date") == last_day)
        .join(cards, on="card_id", suffix="_cards")
    )
    for col in PRICE_COLUMNS:
        differ = latest.filter(pl.col(col).ne_missing(pl.col(f"{col}_cards"))).height
        if differ:
            report.add(
                WARNING, "cards", col,
                f"{differ} carte hanno un prezzo diverso da quello dell'ultimo giorno dello storico",
            )


def validate(cards: pl.DataFrame, history: pl.DataFrame) -> Report:
    report = Report()
    _check_table(cards, CARDS, report)
    _check_table(history, PRICE_HISTORY, report)
    if report.ok:  # i controlli incrociati hanno senso solo se lo schema è giusto
        _check_relations(cards, history, report)
    return report


def schema_table(df: pl.DataFrame | None, table: Table) -> pl.DataFrame:
    """Tabella riassuntiva colonna per colonna, mostrata nel controllo dati."""
    rows = []
    for col in table.columns:
        present = df is not None and col.name in df.columns
        found = kind_of(df.schema[col.name]) if present else None
        nulls = df.get_column(col.name).null_count() if present else None
        rows.append(
            {
                "colonna": col.name,
                "tipo atteso": col.kind,
                "tipo trovato": found,
                "null ammessi": col.nullable,
                "null trovati": nulls,
                "ok": present and found == col.kind and (col.nullable or nulls == 0),
                "descrizione": col.description,
            }
        )
    return pl.DataFrame(rows)
