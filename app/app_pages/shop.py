from datetime import timedelta

import polars as pl
import streamlit as st

from core.data import require_data, show_card_image
from core.shops import SHOPS

ds = require_data()
cards, history = ds.cards, ds.history

name = st.selectbox(
    "Cerca una carta",
    cards.sort("name").get_column("name").to_list(),
    index=None,
    placeholder="Scrivi il nome di una carta...",
)

if not name:
    st.caption("Scegli una carta per vedere quanto costa nei vari shop.")
    st.stop()

card = cards.filter(pl.col("name") == name).row(0, named=True)
last_day = history.get_column("date").max()
recent = (
    history.filter((pl.col("card_id") == card["card_id"]) & (pl.col("date") > last_day - timedelta(days=30)))
    .sort("date")
)

img_col, info_col = st.columns([1, 3])
with img_col:
    show_card_image(card["image_url"], card["name"])

with info_col:
    st.subheader(card["name"])
    details = [card["card_type"], card["race"]]
    if card["level"] is not None:
        details += [card["attribute"] or "-", f"{card['level']} stelle", f"ATK {card['attack']} / DEF {card['defense']}"]
    st.caption(" · ".join(str(d) for d in details))

    with st.container(horizontal=True):
        for shop in SHOPS:
            with st.container(border=True):
                trend = recent.get_column(shop.column).drop_nulls().to_list()
                delta = f"{trend[-1] / trend[0] - 1:+.1%}" if len(trend) > 1 else None
                st.metric(
                    shop.label,
                    shop.fmt(card[shop.column]),
                    delta,
                    delta_description="ultimi 30 giorni" if delta else None,
                    chart_data=trend if len(trend) > 1 else None,
                    chart_type="line",
                )
                st.link_button(f"Cerca su {shop.label}", shop.link(card["name"]), icon=":material/open_in_new:", width="stretch")

    st.caption(
        "Prezzo della copia più economica secondo YGOPRODeck. "
        "Cardmarket è in euro, TCGplayer e CoolStuffInc in dollari."
    )
