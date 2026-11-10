import polars as pl
import streamlit as st

from core.data import require_data, show_card_image
from core.shops import SHOPS

PAGE_SIZE = 24
COLUMNS = 6

SORTS = {
    "Nome": "name",
    "Tipo": "card_type",
    "Elemento": "attribute",
    "Stelle": "level",
    **{f"Prezzo {s.label}": s.column for s in SHOPS},
}

cards = require_data().cards

with st.container(horizontal=True, vertical_alignment="bottom"):
    query = st.text_input("Cerca", placeholder="Nome della carta")
    types = st.multiselect("Tipo", sorted(cards.get_column("card_type").unique().to_list()))
    elements = st.multiselect("Elemento", sorted(cards.get_column("attribute").drop_nulls().unique().to_list()))

levels = cards.get_column("level").drop_nulls()
with st.container(horizontal=True, vertical_alignment="bottom"):
    if levels.len():
        lo, hi = int(levels.min()), int(levels.max())
        stars = st.slider("Stelle", lo, max(hi, lo + 1), (lo, max(hi, lo + 1)))
    else:
        stars = None
    sort_label = st.selectbox("Ordina per", list(SORTS), index=list(SORTS).index("Prezzo Cardmarket"))
    descending = st.segmented_control("Ordine", ["Crescente", "Decrescente"], default="Decrescente", required=True) == "Decrescente"

filtered = cards
if query:
    filtered = filtered.filter(pl.col("name").str.to_lowercase().str.contains(query.lower(), literal=True))
if types:
    filtered = filtered.filter(pl.col("card_type").is_in(types))
if elements:
    filtered = filtered.filter(pl.col("attribute").is_in(elements))
if stars and stars != (lo, max(hi, lo + 1)):
    filtered = filtered.filter(pl.col("level").is_between(*stars))
filtered = filtered.sort(SORTS[sort_label], "name", descending=[descending, False], nulls_last=True)

pages = max(1, -(-filtered.height // PAGE_SIZE))
with st.container(horizontal=True, vertical_alignment="center"):
    st.caption(f"{filtered.height:,} carte")
    page_num = st.number_input("Pagina", min_value=1, max_value=pages, value=1, width=140)

rows = filtered.slice((page_num - 1) * PAGE_SIZE, PAGE_SIZE).to_dicts()
if not rows:
    st.info("Nessuna carta corrisponde ai filtri.")

for start in range(0, len(rows), COLUMNS):
    for col, card in zip(st.columns(COLUMNS), rows[start : start + COLUMNS]):
        with col, st.container(border=True):
            show_card_image(card["image_url"], card["name"])
            st.markdown(f"**{card['name']}**")
            if card["level"] is not None:
                st.caption(f"{'★' * min(card['level'], 12)} {card['level']} · {card['attribute'] or '-'} · {card['race']}")
            else:
                st.caption(f"{card['card_type']} · {card['race']}")
            st.caption("  \n".join(f"{s.label}: {s.fmt(card[s.column])}" for s in SHOPS))
