# Cos'è Streamlit

Streamlit è una libreria Python per fare **app web scrivendo solo Python**, senza
HTML, CSS o JavaScript. La si usa molto nel mondo dati per dashboard e piccoli
strumenti interni.

## Come funziona

Un'app Streamlit è un normale script Python. Ogni comando `st.qualcosa` disegna un
pezzo di pagina, dall'alto verso il basso:

```python
import polars as pl
import streamlit as st

st.title("Le mie carte")

df = pl.read_parquet("data/cleaned/cards.parquet")
nome = st.text_input("Cerca")  # una casella di testo

if nome:
    df = df.filter(pl.col("name").str.contains(nome))

st.dataframe(df)  # una tabella interattiva
```

La cosa più importante da capire: **ogni volta che l'utente tocca qualcosa** (scrive
nella casella, clicca un pulsante…) **Streamlit riesegue tutto lo script da
capo**, con il nuovo valore. Non ci sono callback né eventi da gestire: lo script
gira dall'inizio alla fine, ogni volta.

Siccome lo script riparte spesso, le operazioni lente (come leggere un file grande)
si mettono in **cache** con `@st.cache_data`: la prima volta vengono eseguite, poi
Streamlit riusa il risultato.

## Avviarla

```bash
uv run streamlit run app/streamlit_app.py
```

`streamlit run` avvia un server web locale e apre il browser su
<http://localhost:8501>. Se modifichi un file, la pagina si aggiorna da sola. Per
fermarla: `Ctrl + C` nel terminale.

## Com'è fatta l'app di questo progetto

```
app/
  streamlit_app.py   entry point: impostazioni, barra laterale, menu delle schede
  app_pages/         una pagina per scheda (carte, storico, shop)
  core/              la logica condivisa: contratto dati, caricamento, shop
```

L'app legge solo i due file in `data/cleaned/`. Non sa niente di API, raw o wip:
per lei esistono solo i dati puliti. Per questo **non va modificata**: se qualcosa
non funziona, è il dato che non rispetta il contratto (`docs/contratto_dati.md`).

Vuoi fare esperimenti con Streamlit? Fallo in un file a parte, fuori da `app/`, e
lancialo con `uv run streamlit run <tuo_file>.py`.

Documentazione: <https://docs.streamlit.io/>.
