"""Entry point dell'app.

NON MODIFICARE: questa parte è già pronta. Il compito è produrre i file in
data/cleaned/ nel formato descritto in docs/contratto_dati.md.

Avvio (dalla root del progetto):
    uv run streamlit run app/streamlit_app.py
"""

import streamlit as st

from core.data import MOCK, check_dialog, get_dataset

st.set_page_config(page_title="Archivio Yu-Gi-Oh!", page_icon=":material/style:", layout="wide")

page = st.navigation(
    [
        st.Page("app_pages/carte.py", title="Carte", icon=":material/style:", default=True),
        st.Page("app_pages/storico.py", title="Storico prezzi", icon=":material/show_chart:"),
        st.Page("app_pages/shop.py", title="Cerca negli shop", icon=":material/storefront:"),
    ],
    position="top",
)

with st.sidebar:
    st.header("Archivio Yu-Gi-Oh!")
    st.toggle("Usa dati mock", key="use_mock", help="Mostra i dati finti anche se data/cleaned/ esiste.")
    ds = get_dataset()
    if ds.source == MOCK:
        st.badge("Dati mock", icon=":material/science:", color="orange")
        if not st.session_state.get("use_mock"):
            st.caption("Non ho trovato `data/cleaned/`: sto usando i dati finti.")
    elif ds.report.ok:
        st.badge("Dati reali", icon=":material/check_circle:", color="green")
    else:
        st.badge("Dati reali non validi", icon=":material/error:", color="red")
    if st.button("Controllo dati", icon=":material/fact_check:", width="stretch"):
        check_dialog()
    if st.button("Ricarica dati", icon=":material/refresh:", width="stretch"):
        st.cache_data.clear()
        st.rerun()

page.run()
