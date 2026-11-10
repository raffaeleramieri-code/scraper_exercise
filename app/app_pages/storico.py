from datetime import timedelta

import altair as alt
import polars as pl
import streamlit as st

from core.data import require_data, show_card_image
from core.shops import BY_LABEL, SHOPS

PERIODS = {"7 giorni": 7, "30 giorni": 30, "90 giorni": 90, "Tutto": None}

ds = require_data()
cards, history = ds.cards, ds.history

st.caption(
    "L'API dà solo il prezzo di oggi: lo storico nasce salvando il prezzo ogni volta che "
    "la pipeline gira, un giorno dopo l'altro."
)

names = cards.sort("name").get_column("name").to_list()
with st.container(horizontal=True, vertical_alignment="bottom"):
    name = st.selectbox("Carta", names)
    shop = BY_LABEL[st.segmented_control("Shop", [s.label for s in SHOPS], default=SHOPS[0].label, required=True)]
    period = st.segmented_control("Periodo", list(PERIODS), default="30 giorni", required=True)

card = cards.filter(pl.col("name") == name).row(0, named=True)
series = (
    history.filter(pl.col("card_id") == card["card_id"])
    .select("date", pl.col(shop.column).alias("prezzo"))
    .drop_nulls("prezzo")
    .sort("date")
)
if PERIODS[period] and series.height:
    since = series.get_column("date").max() - timedelta(days=PERIODS[period] - 1)
    series = series.filter(pl.col("date") >= since)

img_col, main_col = st.columns([1, 4])
with img_col:
    show_card_image(card["image_url"], card["name"])

with main_col:
    if series.height == 0:
        st.info(f"Nessun prezzo {shop.label} per questa carta.")
    else:
        first, last = series.get_column("prezzo")[0], series.get_column("prezzo")[-1]
        with st.container(horizontal=True):
            st.metric("Prezzo attuale", shop.fmt(last), f"{(last / first - 1):+.1%}", border=True,
                      delta_description=f"da {series.get_column('date')[0]:%d/%m/%Y}")
            st.metric("Minimo", shop.fmt(series.get_column("prezzo").min()), border=True)
            st.metric("Massimo", shop.fmt(series.get_column("prezzo").max()), border=True)

        if series.height < 2:
            st.info("C'è un solo giorno di storico: il grafico apparirà dal secondo giorno in poi.")
        else:
            chart = (
                alt.Chart(series)
                .mark_line(strokeWidth=2, point=alt.OverlayMarkDef(size=20, opacity=0))
                .encode(
                    x=alt.X("date:T", title=None, axis=alt.Axis(format="%d/%m")),
                    y=alt.Y("prezzo:Q", title=f"Prezzo ({shop.currency})", scale=alt.Scale(zero=False)),
                    tooltip=[
                        alt.Tooltip("date:T", title="Giorno", format="%d/%m/%Y"),
                        alt.Tooltip("prezzo:Q", title=f"Prezzo {shop.currency}", format=",.2f"),
                    ],
                )
                .properties(height=340)
            )
            st.altair_chart(chart, alt=f"Andamento del prezzo {shop.label} di {name}")
