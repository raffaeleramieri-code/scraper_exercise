"""Caricamento dei dati e controllo del contratto, condivisi dalle pagine."""

from __future__ import annotations

from dataclasses import dataclass

import polars as pl
import streamlit as st

from core import contract, mock
from core.paths import CARDS_FILE, PRICE_HISTORY_FILE, PROJECT_ROOT, relative

REAL = "reali"
MOCK = "mock"
FILES = [CARDS_FILE, PRICE_HISTORY_FILE]


@dataclass
class Dataset:
    cards: pl.DataFrame | None
    history: pl.DataFrame | None
    source: str
    report: contract.Report
    files_found: bool = True


@st.cache_data(show_spinner="Carico data/cleaned/ ...", max_entries=3)
def _read_real(mtimes: tuple[float, ...]) -> tuple[pl.DataFrame, pl.DataFrame]:
    # gli mtime fanno parte della chiave della cache: se i file cambiano, si rilegge
    return pl.read_parquet(CARDS_FILE), pl.read_parquet(PRICE_HISTORY_FILE)


@st.cache_data(max_entries=1)
def _build_mock() -> tuple[pl.DataFrame, pl.DataFrame]:
    return mock.build()


def load_real() -> Dataset:
    report = contract.Report()
    missing = [p for p in FILES if not p.exists()]
    for path in missing:
        report.add(contract.ERROR, path.stem, None, f"file non trovato: {relative(path)}")
    if missing:
        return Dataset(None, None, REAL, report, files_found=False)

    try:
        cards, history = _read_real(tuple(p.stat().st_mtime for p in FILES))
    except Exception as exc:  # parquet rotto o non leggibile
        report.add(contract.ERROR, "-", None, f"impossibile leggere i file parquet: {exc}")
        return Dataset(None, None, REAL, report)

    return Dataset(cards, history, REAL, contract.validate(cards, history))


def load_mock() -> Dataset:
    cards, history = _build_mock()
    return Dataset(cards, history, MOCK, contract.validate(cards, history))


def get_dataset() -> Dataset:
    """Dati reali se esistono, altrimenti mock. Il toggle in sidebar forza il mock."""
    if st.session_state.get("use_mock"):
        return load_mock()
    real = load_real()
    return real if real.files_found else load_mock()


def require_data() -> Dataset:
    """Da chiamare all'inizio di ogni pagina: si ferma se il contratto non è rispettato."""
    ds = get_dataset()
    if not ds.report.ok:
        st.error(
            f"I dati in `data/cleaned/` non rispettano il contratto ({len(ds.report.errors)} errori).",
            icon=":material/error:",
        )
        if st.button("Apri il controllo dati", icon=":material/fact_check:"):
            check_dialog()
        st.caption("Per vedere comunque l'app, attiva **Usa dati mock** nella barra laterale.")
        st.stop()
    return ds


@st.dialog("Controllo dati", width="large")
def check_dialog() -> None:
    st.caption(f"Regole in `docs/contratto_dati.md`. File controllati: {', '.join(f'`{relative(p)}`' for p in FILES)}.")
    source = st.segmented_control(
        "Cosa controllare",
        ["Dati reali", "Dati mock"],
        default="Dati reali",
        required=True,
        help="I dati mock passano sempre il controllo: usali come esempio di file corretto.",
    )
    ds = load_real() if source == "Dati reali" else load_mock()
    report = ds.report

    if not ds.files_found:
        st.warning("File non trovati in `data/cleaned/`: finché non esistono, l'app usa i dati mock.", icon=":material/folder_off:")
    elif report.ok and not report.warnings:
        st.success("Tutto in ordine: i dati rispettano il contratto.", icon=":material/check_circle:")
    elif report.ok:
        st.success("Contratto rispettato, l'app funziona. Dai un'occhiata agli avvisi.", icon=":material/check_circle:")
    else:
        st.error(f"Contratto non rispettato: {len(report.errors)} errori da correggere.", icon=":material/error:")

    if report.issues:
        st.dataframe(
            pl.DataFrame(
                [
                    {"livello": i.level, "tabella": i.table, "colonna": i.column, "messaggio": i.message}
                    for i in sorted(report.issues, key=lambda i: i.level != contract.ERROR)
                ]
            ),
            hide_index=True,
            column_config={"messaggio": st.column_config.TextColumn("messaggio", width="large")},
            alt="Errori e avvisi trovati",
        )

    for table, df in zip(contract.TABLES, (ds.cards, ds.history)):
        st.markdown(f"**`{table.name}`**" + (f" · {df.height:,} righe" if df is not None else ""))
        st.dataframe(
            contract.schema_table(df, table),
            hide_index=True,
            column_config={
                "ok": st.column_config.CheckboxColumn("ok"),
                "null ammessi": st.column_config.CheckboxColumn("null ammessi"),
            },
            alt=f"Schema atteso e trovato per {table.name}",
        )


def resolve_image(value: str | None) -> str | None:
    """URL così com'è, percorso locale risolto dalla root; None se non trovato."""
    if not value:
        return None
    if value.startswith(("http://", "https://")):
        return value
    path = PROJECT_ROOT / value
    return str(path) if path.exists() else None


def show_card_image(image_url: str | None, name: str, width="stretch") -> None:
    image = resolve_image(image_url)
    if image:
        st.image(image, width=width, alt=name)
    else:
        st.caption(":material/image_not_supported: immagine non trovata")
