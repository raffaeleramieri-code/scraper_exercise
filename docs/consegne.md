# Consegne per fasi

> Questa è la versione **sintetica**. Se ti blocchi o non sai come andare avanti,
> in `docs/consegne_expanded.md` trovi le stesse fasi con tutti i dettagli: quali
> classi e funzioni scrivere e cosa devono fare.

## Regole

- Lavori in locale, sulla tua copia del progetto: quando una fase è pronta, avvisa
  per la revisione.
- `app/` **non si tocca**: l'obiettivo è che il **Controllo dati** dell'app sia verde.
- Ogni cartella di `src/` è un package, con il suo `__init__.py`.
- Si lancia sempre dalla root: `uv run python -m src.<cartella>.<file>`.
- Python di base (liste, dizionari, cicli, classi, eccezioni). polars solo per
  esplorare e per scrivere i Parquet, requests solo per le GET.
- Le costanti (percorsi dinamici, URL dell'API) stanno tutte in `src/consts.py`.

## Le fasi

| Fase | Cosa fai | File |
|---|---|---|
| 0 · Setup | installi, avvii l'app, leggi la documentazione | - |
| 1 · Estrazione | scarichi le carte dall'API in `data/raw/` | `src/consts.py`, `src/scrape/scraper.py` |
| 2 · Esplorazione | guardi com'è fatto il raw con polars | `src/raw_to_wip/explore.py`, `docs/esplorazione.md` |
| 3 · Trasformazione | porti il raw in una lista di carte piatte in `data/wip/` | `src/raw_to_wip/card.py`, `transform.py` |
| 4 · Pulizia | sistemi tipi e valori mancanti e scrivi `cards.parquet` | `src/wip_to_clean/clean.py` |
| 5 · Storico | costruisci `price_history.parquet` da tutti i wip | `src/wip_to_clean/history.py` |
| 6 · Pipeline | lanci tutto con un solo comando | `main.py` |

---

### Fase 0 · Setup

- Scarica la cartella del progetto sul tuo PC.
- `uv sync`, poi avvia l'app (vedi README): vedi i dati mock, cioè l'esempio del
  risultato.
- Leggi `docs/contratto_dati.md` e `docs/api_ygoprodeck.md`.

**Fatto quando:** l'app gira sul tuo PC.

### Fase 1 · Estrazione

- `src/consts.py` con le costanti del progetto: i percorsi (`ROOT`, `RAW_DIR`,
  `WIP_DIR`, `CLEANED_DIR`) e l'URL dell'API (`API_URL`).
- `src/scrape/scraper.py` con la classe `YugiohScraper`: scarica `cardinfo.php` e
  lo salva in `data/raw/cardinfo_<data>.json`.
- Se il file di oggi esiste già, non richiama l'API.
- Se la chiamata fallisce riprova fino a 3 volte (`while`), poi solleva una tua
  `ScraperError`.

**Fatto quando:** lanciato due volte di fila, la seconda volta non scarica niente.

### Fase 2 · Esplorazione

- In `src/raw_to_wip/explore.py` leggi il raw con polars e studialo.
- In `docs/esplorazione.md` rispondi alle domande: quante carte, quali campi annidati,
  quali mancano, di che tipo sono i prezzi.

**Fatto quando:** sai spiegare com'è fatto il raw senza aprirlo.

### Fase 3 · Trasformazione

- In `src/raw_to_wip/card.py` la classe `Card`, con gli attributi chiamati come le
  colonne del contratto.
- In `src/raw_to_wip/transform.py` trasformi ogni file raw in
  `data/wip/cards_<data>.json`: una lista di carte piatte.

**Fatto quando:** in `data/wip/` c'è un file per ogni file raw.

### Fase 4 · Pulizia

- In `src/wip_to_clean/clean.py` prezzi da stringa a numero (`"0"` diventa `None`),
  testi vuoti a `None`.
- Salvi l'ultimo wip pulito in `data/cleaned/cards.parquet`.

**Fatto quando:** il Controllo dati non segnala errori su `cards`.

### Fase 5 · Storico

- In `src/wip_to_clean/history.py` leggi tutti i wip, uno per giorno, e costruisci
  `data/cleaned/price_history.parquet` da zero.

**Fatto quando:** il Controllo dati è verde e lo storico, dal secondo giorno, ha una
linea.

### Fase 6 · Pipeline

- `main.py` lancia in ordine scraper → trasformazione → pulizia → storico, con i
  tempi di ogni passo e un messaggio chiaro se l'API non risponde.

**Fatto quando:** `uv run python main.py` fa tutto da solo.

---

### Bonus

- **A · Immagini in locale:** scarichi le immagini una volta sola in `data/images/`.
- **B · Scraper per tutti i giochi:** superclasse `Scraper` con configurazione in
  `@dataclass`, poi un secondo gioco (Magic).

## Dove trovi le informazioni

| Ti serve… | Leggi |
|---|---|
| il formato esatto dei file finali | `docs/contratto_dati.md` |
| come funziona l'API | `docs/api_ygoprodeck.md` |
| i comandi polars | `docs/polars_vs_pandas.md` |
| package e `__init__.py` | `docs/faq/package.md` |
| cos'è un Parquet | `docs/faq/parquet.md` |
| comandi git e uv | `docs/faq/git_e_uv.md` |
| come funziona l'app | `docs/faq/streamlit.md` |
| i dettagli di ogni fase | `docs/consegne_expanded.md` |
