# Archivio Yu-Gi-Oh!

Progetto di data engineering con una pipeline **ETL locale**: scarica le carte di
Yu-Gi-Oh! con i loro prezzi da un'API REST, le pulisce, ne costruisce lo storico dei
prezzi e le mostra in un'app Streamlit con tre schede:

- **Carte**: tutte le carte, filtrabili e ordinabili per tipo, elemento, stelle e
  prezzo.
- **Storico prezzi**: l'andamento del prezzo di una carta nel tempo.
- **Cerca negli shop**: il prezzo di una carta su Cardmarket, TCGplayer e
  CoolStuffInc, con il link diretto allo shop.

```
API YGOPRODeck ──GET──> data/raw/ ──> data/wip/ ──> data/cleaned/ ──> app Streamlit
                 (scrape)      (raw_to_wip)   (wip_to_clean)         (già pronta)
```

## Setup

Serve [uv](https://docs.astral.sh/uv/). Dalla root del progetto, in Git Bash:

```bash
uv sync   # crea .venv e installa le dipendenze
```

## La pipeline

I dettagli di ogni passo, con cosa consegnare, sono in `docs/consegne.md`.

### 1. Estrazione → `data/raw/`

Chiamata GET all'API YGOPRODeck. La risposta JSON si salva così com'è, un file per
giorno. Vedi `docs/api_ygoprodeck.md`.

### 2. Trasformazione → `data/wip/`

Esplorazione del raw con polars, poi trasformazione in Python (classi, liste,
dizionari) in una lista di carte "piatte", una per carta.

### 3. Pulizia → `data/cleaned/`

Tipi, nomi delle colonne e valori mancanti sistemati secondo il contratto dati
(`docs/contratto_dati.md`). In `data/cleaned/` finiscono due file:

- `cards.parquet`: una riga per carta, con i prezzi di oggi
- `price_history.parquet`: una riga per carta per giorno, cioè lo storico dei prezzi

Non sai cos'è un file Parquet? Vedi `docs/faq/parquet.md`.

### 4. Visualizzazione con Streamlit

Quando i due file in `data/cleaned/` esistono, avvia l'app:

```bash
uv run streamlit run app/streamlit_app.py
```

Si apre il browser su <http://localhost:8501>. Per fermare l'app: `Ctrl + C` nel
terminale.

Cosa fa il comando:

- `uv run …` esegue il comando dentro il virtual environment del progetto, senza
  doverlo attivare. Se le dipendenze non sono allineate con `uv.lock`, prima le
  sistema.
- `streamlit run app/streamlit_app.py` avvia un piccolo server web locale che esegue
  lo script e mostra il risultato nel browser. Ogni volta che interagisci con la
  pagina, o salvi un file, Streamlit riesegue lo script dall'inizio.
- Va lanciato **dalla root del progetto**: è lì che Streamlit trova
  `.streamlit/config.toml`.

All'avvio l'app controlla che i file rispettino il contratto dati. Se non lo
rispettano si ferma: il pulsante **Controllo dati** nella barra laterale spiega cosa
correggere. Dopo aver rigenerato i dati, premi **Ricarica dati**.

Non hai mai usato Streamlit? Vedi `docs/faq/streamlit.md`.

## Struttura

```
app/                  app Streamlit (NON MODIFICARE)
  streamlit_app.py      entry point e navigazione
  app_pages/            le tre schede
  core/                 contratto dati, caricamento, shop
.streamlit/config.toml configurazione di Streamlit
docs/                 documentazione e consegne
src/                  package della pipeline (da riempire)
main.py               entry point della pipeline (da scrivere)
pyproject.toml        dipendenze, gestite da uv
```

`src/` c'è già, con solo il suo `__init__.py`: i package al suo interno e la
cartella `data/` li crei tu durante le fasi (vedi `docs/consegne.md`).

## Regole

- **Non modificare `app/`.** È il "cliente" dei tuoi dati: se l'app non funziona, è
  il dato da sistemare, non l'app.
- Percorsi dinamici, polars al posto di pandas, `requests` solo in GET, uv per le
  dipendenze.
- I dati (`data/`) non vanno su git.

## Documentazione

| File | Contenuto |
|---|---|
| [docs/consegne.md](docs/consegne.md) | le fasi del progetto, da leggere per prime |
| [docs/consegne_expanded.md](docs/consegne_expanded.md) | le stesse fasi con tutti i dettagli, se ti blocchi |
| [docs/contratto_dati.md](docs/contratto_dati.md) | il formato esatto dei file in `data/cleaned/` |
| [docs/api_ygoprodeck.md](docs/api_ygoprodeck.md) | l'API, le sue regole e la struttura della risposta |
| [docs/polars_vs_pandas.md](docs/polars_vs_pandas.md) | polars spiegato a chi conosce (un po') pandas |
| [docs/faq/git_e_uv.md](docs/faq/git_e_uv.md) | i comandi git e uv che servono |
| [docs/faq/parquet.md](docs/faq/parquet.md) | cos'è un file Parquet e perché lo usiamo |
| [docs/faq/streamlit.md](docs/faq/streamlit.md) | cos'è Streamlit e come funziona l'app |
| [docs/faq/package.md](docs/faq/package.md) | moduli, package e `__init__.py`: come importare le funzioni |
