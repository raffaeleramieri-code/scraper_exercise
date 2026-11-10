"""Percorsi del progetto calcolati in modo dinamico.

Nessun percorso è scritto "a mano" (tipo C:/Users/...): partiamo dalla posizione
di questo file e risaliamo fino alla root del progetto. Così il codice funziona
su qualsiasi PC, qualunque sia la cartella in cui è stata clonata la repo.
"""

from pathlib import Path

# questo file è in <root>/app/core/paths.py -> parents[2] è <root>
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
CLEANED_DIR = DATA_DIR / "cleaned"

CARDS_FILE = CLEANED_DIR / "cards.parquet"
PRICE_HISTORY_FILE = CLEANED_DIR / "price_history.parquet"


def relative(path: Path) -> str:
    """Percorso relativo alla root, comodo da mostrare nei messaggi."""
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return str(path)
