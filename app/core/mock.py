"""Dati finti che rispettano il contratto.

Servono a far girare l'app prima che la pipeline ETL esista, e sono anche un
esempio concreto di come devono essere fatti i file in data/cleaned/.
Carte, immagini e prezzi attuali sono reali; lo storico dei prezzi è inventato.
Le immagini sono in app/assets/mock_images/.
"""

from __future__ import annotations

import math
import random
from datetime import date, timedelta

import polars as pl

from core.contract import CARDS, DATE, DECIMAL, INTEGER, PRICE_COLUMNS, PRICE_HISTORY, TEXT, Table

_DTYPES = {INTEGER: pl.Int64, DECIMAL: pl.Float64, TEXT: pl.String, DATE: pl.Date}
HISTORY_DAYS = 90

# (id, nome, tipo, tipo mostro, elemento, stelle, atk, def, cardmarket €, tcgplayer $, coolstuffinc $)
_CARDS = [
    (14558127, "Ash Blossom & Joyous Spring", "Tuner Monster", "Zombie", "FIRE", 3, 0, 1800, 0.42, 0.38, 4.99),
    (72989439, "Black Luster Soldier - Envoy of the Beginning", "Effect Monster", "Warrior", "LIGHT", 8, 3000, 2500, 0.02, 0.38, 0.49),
    (89631139, "Blue-Eyes White Dragon", "Normal Monster", "Dragon", "LIGHT", 8, 3000, 2500, 0.10, 0.13, 0.99),
    (46986414, "Dark Magician", "Normal Monster", "Spellcaster", "DARK", 7, 2500, 2100, 0.02, 0.33, 0.39),
    (38033121, "Dark Magician Girl", "Effect Monster", "Spellcaster", "DARK", 6, 2000, 1700, 0.05, 0.44, 0.39),
    (89943723, "Elemental HERO Neos", "Normal Monster", "Warrior", "LIGHT", 7, 2500, 2000, 0.15, 0.18, 0.25),
    (33396948, "Exodia the Forbidden One", "Effect Monster", "Spellcaster", "DARK", 3, 1000, 1000, None, 2.69, 0.99),
    (77585513, "Jinzo", "Effect Monster", "Machine", "DARK", 6, 2400, 1500, 0.22, 0.25, 0.39),
    (40640057, "Kuriboh", "Effect Monster", "Fiend", "DARK", 1, 300, 200, 0.06, 0.23, 0.25),
    (44095762, "Mirror Force", "Trap Card", "Normal", None, None, None, None, 0.02, 0.65, 0.99),
    (83764718, "Monster Reborn", "Spell Card", "Normal", None, None, None, None, 0.02, 0.20, 0.79),
    (55144522, "Pot of Greed", "Spell Card", "Normal", None, None, None, None, 0.15, 4.30, 3.99),
    (12580477, "Raigeki", "Spell Card", "Normal", None, None, None, None, 0.22, 0.26, None),
    (74677422, "Red-Eyes Black Dragon", "Normal Monster", "Dragon", "DARK", 7, 2400, 2000, 0.16, 0.25, 0.99),
    (44508094, "Stardust Dragon", "Synchro Monster", "Dragon", "WIND", 8, 2500, 2000, 0.69, 0.61, 0.99),
    (70781052, "Summoned Skull", "Normal Monster", "Fiend", "DARK", 6, 2500, 1200, 0.18, 0.52, 0.39),
]


def _frame(rows: list[dict], table: Table) -> pl.DataFrame:
    return pl.DataFrame(rows, schema={c.name: _DTYPES[c.kind] for c in table.columns})


def _walk_back(rng: random.Random, today_price: float | None, days: int) -> list[float | None]:
    """Prezzi dal più vecchio a oggi: random walk all'indietro che finisce sul prezzo attuale."""
    if today_price is None:
        return [None] * days
    prices = [today_price]
    drift = rng.uniform(-0.006, 0.006)
    for _ in range(days - 1):
        prices.append(prices[-1] / math.exp(drift + rng.gauss(0, 0.03)))
    return [max(round(p, 2), 0.01) for p in reversed(prices)]


def build(seed: int = 42, today: date | None = None) -> tuple[pl.DataFrame, pl.DataFrame]:
    rng = random.Random(seed)
    today = today or date.today()
    days = [today - timedelta(days=n) for n in range(HISTORY_DAYS - 1, -1, -1)]

    cards, history = [], []
    for (card_id, name, ctype, race, attr, lvl, atk, dfn, cm, tcg, csi) in _CARDS:
        current = dict(zip(PRICE_COLUMNS, (cm, tcg, csi)))
        cards.append(
            {
                "card_id": card_id,
                "name": name,
                "card_type": ctype,
                "race": race,
                "attribute": attr,
                "level": lvl,
                "attack": atk,
                "defense": dfn,
                # percorso locale relativo alla root: le immagini sono state scaricate
                # una volta sola, come chiede l'API (niente hotlinking)
                "image_url": f"app/assets/mock_images/{card_id}.jpg",
                **current,
            }
        )
        series = {col: _walk_back(rng, price, HISTORY_DAYS) for col, price in current.items()}
        for i, day in enumerate(days):
            history.append({"date": day, "card_id": card_id, **{col: s[i] for col, s in series.items()}})

    return _frame(cards, CARDS), _frame(history, PRICE_HISTORY)
