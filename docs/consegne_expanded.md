# Consegne per fasi: versione dettagliata

> Questa è la versione **con tutti i dettagli** di `docs/consegne.md`: le fasi sono
> le stesse, ma qui trovi per ogni file quali classi e funzioni scrivere e cosa
> devono fare. Parti da `consegne.md` e vieni qui quando ti blocchi o non sai come
> andare avanti.

---

## Regole per tutte le fasi

| Regola | In pratica |
|---|---|
| Si lavora in locale | sulla tua copia del progetto; quando una fase è pronta, avvisa per la revisione |
| `app/` non si tocca | l'obiettivo è che il **Controllo dati** dell'app sia verde |
| Costanti in un posto solo | percorsi dinamici (niente `C:/Users/...`) e URL dell'API stanno tutti in `src/consts.py` |
| Package | ogni cartella di `src/` ha il suo `__init__.py` |
| Si lancia dalla root | `uv run python -m src.scrape.scraper` (ogni modulo ha il suo `if __name__ == "__main__":`) |
| Python di base | liste, dizionari, `for`, `while`, classi normali (niente `@dataclass` per ora) |
| polars | solo per esplorare (fase 2) e scrivere i Parquet (fasi 4 e 5) |
| requests | solo chiamate GET |
| `data/` | si crea da codice, non va su git |

## Struttura finale

```
src/
├── __init__.py              c'è già
├── consts.py                fase 1
├── scrape/
│   ├── __init__.py          fase 1
│   └── scraper.py           fase 1
├── raw_to_wip/
│   ├── __init__.py          fase 2
│   ├── explore.py           fase 2
│   ├── card.py              fase 3
│   └── transform.py         fase 3
└── wip_to_clean/
    ├── __init__.py          fase 4
    ├── clean.py             fase 4
    └── history.py           fase 5
docs/esplorazione.md         fase 2
main.py                      fase 6

data/                        creata dal codice
├── raw/                     cardinfo_2026-11-10.json   (uno per giorno)
├── wip/                     cards_2026-11-10.json      (uno per giorno)
└── cleaned/                 cards.parquet, price_history.parquet
```

---

## Fase 0 · Setup

1. Scarica la cartella del progetto sul tuo PC e, dalla sua root, lancia `uv sync`.
2. Avvia l'app (vedi README): vedi i **dati mock**, cioè l'esempio di come deve
   venire il risultato.
3. Leggi `docs/contratto_dati.md` e `docs/api_ygoprodeck.md`.

**Info:** `README.md` · `docs/faq/git_e_uv.md` · `docs/faq/streamlit.md`

**Fatto quando:** l'app gira sul tuo PC.

---

## Fase 1 · Estrazione (API → `data/raw/`)

### `src/consts.py`

Contiene tutte le costanti del progetto. Gli altri moduli le importano da qui, per
esempio `from src.consts import RAW_DIR`. I percorsi si calcolano a partire da
`Path(__file__)`: prendi spunto da `app/core/paths.py`.

| Costante | Valore |
|---|---|
| `API_URL` | `"https://db.ygoprodeck.com/api/v7/cardinfo.php"` |
| `ROOT` | la root del progetto |
| `DATA_DIR` | `ROOT / "data"` |
| `RAW_DIR` | `DATA_DIR / "raw"` |
| `WIP_DIR` | `DATA_DIR / "wip"` |
| `CLEANED_DIR` | `DATA_DIR / "cleaned"` |

### `src/scrape/`

Crea la cartella e mettici dentro due file: `__init__.py` (vuoto) e `scraper.py`.
Perché serve `__init__.py` lo trovi in `docs/faq/package.md`.

### `src/scrape/scraper.py`

**Eccezione:** `class ScraperError(Exception)`.

**Classe `YugiohScraper`:**

| Metodo | Cosa fa |
|---|---|
| `__init__(self)` | salva in `self.url` la costante `API_URL` e in `self.raw_dir` la cartella `RAW_DIR` |
| `raw_file_path(self)` | restituisce il `Path` del file di oggi: `RAW_DIR / f"cardinfo_{date.today().isoformat()}.json"` |
| `download(self)` | fa la GET e restituisce `response.json()` (dettagli sotto) |
| `save(self, data)` | crea la cartella (`mkdir(parents=True, exist_ok=True)`) e scrive `data` con `with open(..., "w", encoding="utf-8")` e `json.dump` |
| `run(self)` | se il file di oggi esiste stampa "già scaricato", altrimenti `download()` e poi `save()`. Restituisce sempre il `Path` del file |

**Come funziona `download`:**

- un ciclo `while` che fa **al massimo 3 tentativi**;
- a ogni tentativo `requests.get(self.url, timeout=60)` e poi `raise_for_status()`;
- se il tentativo solleva `requests.RequestException`: stampa l'errore, aspetta 5
  secondi (`time.sleep(5)`) e riprova;
- dopo il terzo tentativo fallito: `raise ScraperError("...")` con un messaggio chiaro.

**In fondo al file:** nel blocco `if __name__ == "__main__":` crea uno
`YugiohScraper` e chiama `run()`.

**Info:** `docs/api_ygoprodeck.md` · `app/core/paths.py` · `docs/faq/package.md`

**Fatto quando:** `uv run python -m src.scrape.scraper` crea il file in
`data/raw/` e, lanciato una seconda volta, stampa "già scaricato" senza chiamare
l'API.

---

## Fase 2 · Esplorazione (leggere `raw/` con polars)

### `src/raw_to_wip/`

Crea la cartella con dentro `__init__.py` (vuoto) ed `explore.py`.

### `src/raw_to_wip/explore.py`

1. Leggi l'ultimo file di `data/raw/`:
   ```python
   df = pl.read_json(percorso).explode("data").unnest("data")
   ```
   Così ottieni una riga per carta.
2. Stampa `df.schema`, `df.head()` e `df.describe()`.
3. Conta quello che serve per rispondere alle domande qui sotto.

### `docs/esplorazione.md`

Scrivi le risposte:

- Quante carte ci sono?
- Quali campi sono liste o struct?
- Quali campi mancano su alcune carte (cioè sono null)?
- Di che tipo sono i prezzi? Quante carte hanno `cardmarket_price` uguale a `"0"`?

**Info:** `docs/polars_vs_pandas.md` · `docs/api_ygoprodeck.md`

**Fatto quando:** `docs/esplorazione.md` risponde a tutte le domande.

---

## Fase 3 · Trasformazione (raw → `data/wip/`)

> Da qui in poi solo Python di base: niente polars.

### `src/raw_to_wip/card.py`

**Classe `Card`:**

| Metodo | Cosa fa |
|---|---|
| `__init__(self, ...)` | riceve e salva come attributi i 12 campi elencati sotto |
| `to_dict(self)` | restituisce un dizionario con tutti gli attributi |

I campi hanno gli **stessi nomi** delle colonne di `cards` nel contratto dati:

```
card_id, name, card_type, race, attribute, level, attack, defense,
image_url, price_cardmarket, price_tcgplayer, price_coolstuffinc
```

In questa fase i valori restano come arrivano dall'API: i prezzi sono ancora
stringhe. Li sistemi nella fase 4.

### `src/raw_to_wip/transform.py`

| Funzione | Cosa fa |
|---|---|
| `card_from_api(item)` | riceve il dizionario di una carta dell'API e restituisce una `Card` (dettagli sotto) |
| `raw_to_wip(raw_path)` | legge il raw, crea le `Card` e scrive il file wip (dettagli sotto) |
| `run()` | fa un `for` su `RAW_DIR.glob("cardinfo_*.json")` e chiama `raw_to_wip` solo per i file che non hanno ancora il wip corrispondente |

**Come funziona `card_from_api`:**

- per i campi che possono mancare (`attribute`, `level`, `atk`, `def`) usa
  `item.get("campo")`;
- l'immagine è `item["card_images"][0]["image_url"]`;
- i prezzi sono in `item["card_prices"][0]`.

**Come funziona `raw_to_wip`:**

1. legge il file con `with open` e `json.load`;
2. fa un `for` su `payload["data"]` e crea una `Card` per ognuna;
3. scrive la lista di `card.to_dict()` in `WIP_DIR`, con la stessa data del raw:
   da `cardinfo_2026-11-10.json` esce `cards_2026-11-10.json`.

**In fondo al file:** blocco `if __name__ == "__main__":` che chiama `run()`.

**Info:** `docs/contratto_dati.md` · `docs/api_ygoprodeck.md` · `docs/faq/package.md`

**Fatto quando:** `uv run python -m src.raw_to_wip.transform` crea in `data/wip/`
un file per ogni file raw, con una lista di carte "piatte" (niente liste annidate).

---

## Fase 4 · Pulizia (wip → `data/cleaned/cards.parquet`)

### `src/wip_to_clean/`

Crea la cartella con dentro `__init__.py` (vuoto) e `clean.py`.

### `src/wip_to_clean/clean.py`

**In cima al file:** `CARDS_SCHEMA`, un dizionario colonna → tipo polars preso dalla
tabella del contratto:

```python
CARDS_SCHEMA = {
    "card_id": pl.Int64,
    "name": pl.String,
    # ... tutte le altre colonne
    "price_coolstuffinc": pl.Float64,
}
```

| Funzione | Cosa fa |
|---|---|
| `parse_price(value)` | stringa → `float`. Restituisce `None` se il valore manca, non è un numero (`try` / `except ValueError`) o è `<= 0` |
| `clean_text(value)` | restituisce `None` se il valore è `None` o vuoto (anche solo spazi), altrimenti la stringa senza spazi ai bordi |
| `clean_card(card)` | riceve una carta del wip e restituisce un **nuovo** dizionario, con `parse_price` sui prezzi e `clean_text` sui testi |
| `build_cards()` | legge **l'ultimo** file di `WIP_DIR`, applica `clean_card` a ogni carta, crea `pl.DataFrame(righe, schema=CARDS_SCHEMA)` e lo salva con `write_parquet(CLEANED_DIR / "cards.parquet")` |

**In fondo al file:** blocco `if __name__ == "__main__":` che chiama `build_cards()`.

**Info:** `docs/contratto_dati.md` · `docs/faq/parquet.md` · per un esempio di file
corretto, nell'app apri **Controllo dati** e scegli "Dati mock" (il codice è in
`app/core/mock.py`).

**Fatto quando:** il Controllo dati non segnala errori su `cards`. Su
`price_history` ne segnalerà ancora, perché manca il file.

---

## Fase 5 · Storico prezzi (`data/cleaned/price_history.parquet`)

> Lo storico si **ricostruisce da zero a ogni esecuzione** leggendo tutti i file
> wip, uno per giorno. Così non ci sono mai righe doppie e, se qualcosa va storto,
> basta rilanciare.

### `src/wip_to_clean/history.py`

**In cima al file:** `HISTORY_SCHEMA`, come `CARDS_SCHEMA` ma per le colonne di
`price_history` (la data è `pl.Date`).

**Funzione `build_history()`:**

1. fa un `for` su tutti i file di `WIP_DIR`;
2. dal nome del file ricava la data: da `cards_2026-11-10.json` si ottiene
   `date.fromisoformat("2026-11-10")`;
3. per ogni carta del file aggiunge a una lista una riga con `date`, `card_id` e i
   tre prezzi puliti con `parse_price` (importata da `src.wip_to_clean.clean`);
4. crea il DataFrame con `schema=HISTORY_SCHEMA` e lo salva in
   `CLEANED_DIR / "price_history.parquet"`.

**In fondo al file:** blocco `if __name__ == "__main__":` che chiama `build_history()`.

**Info:** `docs/contratto_dati.md` (sezione `price_history`) · `docs/faq/parquet.md` ·
Controllo dati con "Dati mock"

**Fatto quando:** il Controllo dati non ha errori, tutte e tre le pagine mostrano i
dati reali e, dal secondo giorno in poi, lo storico ha una linea.

---

## Fase 6 · Pipeline completa

### `main.py`

1. Importa `YugiohScraper`, `ScraperError`, `run` di `transform`, `build_cards` e
   `build_history`.
2. Nella funzione `main()` chiama in ordine: scraper → trasformazione → pulizia →
   storico. Prima di ogni passo stampa cosa sta facendo, dopo stampa quanti secondi
   ci ha messo (`time.perf_counter()`).
3. Metti tutto dentro un `try` / `except ScraperError`: se l'API non risponde,
   stampa un messaggio chiaro invece di un traceback lungo.

**Info:** `docs/faq/package.md` · `README.md` · `docs/faq/git_e_uv.md`

**Fatto quando:** `uv run python main.py` fa tutto da solo e l'app funziona.

---

## Bonus A · Immagini in locale

L'API chiede di non caricare le immagini dal loro server ogni volta (vedi
`docs/api_ygoprodeck.md`).

### `src/scrape/images.py`

Una funzione che, per ogni carta, scarica l'immagine *small* (`image_url_small`)
in `data/images/<card_id>.jpg`:

- se il file esiste già, la salta;
- tra un download e l'altro aspetta 0.1 secondi (`time.sleep(0.1)`);
- scrive il file con `with open(..., "wb")` e `response.content`.

### `src/wip_to_clean/clean.py`

In `image_url` metti il percorso locale relativo alla root, per esempio
`data/images/89631139.jpg`. I dati mock fanno già così.

---

## Bonus B · Uno scraper per tutti i giochi

1. Crea la superclasse `Scraper` con la logica comune: GET con i tentativi,
   salvataggio in `raw/`, controllo "già scaricato oggi".
2. Descrivi la configurazione di ogni gioco (nome, URL, prefisso del file raw) con
   una `@dataclass`, che la superclasse riceve.
3. `YugiohScraper` estende `Scraper`. Poi aggiungi `MagicScraper` per Magic, con
   l'API Scryfall.
4. Solo in questa fase si potrà estendere anche l'app, per mostrare gli altri
   giochi: ne parliamo prima di toccarla.

**Info:** <https://scryfall.com/docs/api> ·
<https://docs.python.org/3/tutorial/classes.html> ·
<https://docs.python.org/3/library/dataclasses.html>
