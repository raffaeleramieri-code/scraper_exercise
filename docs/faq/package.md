# Moduli e package

## Modulo

Un **modulo** è un semplice file `.py`. Quello che ci definisci dentro (funzioni,
classi, costanti) lo puoi usare da un altro file con `import`.

## Package

Un **package** è una cartella che contiene moduli e altri package (sottocartelle).
Per convenzione ogni package ha un file `__init__.py`, di solito vuoto.

> **L'`__init__.py` è obbligatorio?** No. Da Python 3.3 anche una cartella senza
> `__init__.py` si può importare: diventa un *namespace package*, cioè un package
> implicito. Noi lo mettiamo lo stesso, per tre motivi:
>
> - è la convenzione, e chi apre il progetto vede subito quali cartelle sono codice
>   importabile;
> - i namespace package servono a un caso particolare (un package diviso su più
>   cartelle) e hanno comportamenti che possono confondere;
> - alcuni strumenti, come i test e i linter, funzionano meglio con package espliciti.
>
> Quindi: ogni cartella di `src/` ha il suo `__init__.py`.

```
main.py
src/
  __init__.py
  scrape/
    __init__.py
    scraper.py        <- def scarica_carte(): ...
  raw_to_wip/
    __init__.py
    transform.py
```

## Importare

Da `main.py`, che sta nella root, importi seguendo le cartelle con il punto:

```python
from src.scrape.scraper import scarica_carte

scarica_carte()
```

Allo stesso modo, un modulo dentro `src` può importare da un altro package:

```python
# src/raw_to_wip/transform.py
from src.scrape.scraper import RAW_DIR
```

Usa sempre import "completi" che partono da `src.`: si legge subito da dove arriva
ogni cosa.

## Da dove lanciare

Python cerca i package a partire dalla cartella dello script che lanci. Quindi
**lancia sempre dalla root del progetto**:

```bash
uv run python main.py                 # tutta la pipeline
uv run python -m src.scrape.scraper   # un solo modulo, con -m e i punti
```

Con `-m` scrivi il percorso con i punti e senza `.py`. Non lanciare
`python src/scrape/scraper.py`: Python partirebbe da `src/scrape/`, non troverebbe
`src` e darebbe `ModuleNotFoundError: No module named 'src'`.

Se vuoi che un modulo faccia qualcosa quando lo lanci, ma non quando lo importi:

```python
if __name__ == "__main__":
    scarica_carte()
```

## E l'app?

Anche `app/` e `app/core/` sono package. Dentro l'app vedrai `from core.data import ...`
invece di `from app.core.data import ...`: Streamlit parte da `app/`, quindi per lui
`core` è già un package di primo livello. Non serve toccarlo.
