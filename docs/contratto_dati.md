# Contratto dati

L'app Streamlit legge **due file Parquet** da `data/cleaned/`. Se i file rispettano
queste regole, l'app funziona. Se non le rispettano, l'app si ferma: il pulsante
**Controllo dati** nella barra laterale ti dice cosa non va.

Le regole sono scritte anche nel codice, in `app/core/contract.py`. Se hai un dubbio,
fa fede quello.

## Come salvare i file

```python
cards.write_parquet(CLEANED_DIR / "cards.parquet")
price_history.write_parquet(CLEANED_DIR / "price_history.parquet")
```

Usiamo Parquet invece di CSV perché salva anche i **tipi** delle colonne: un intero
resta un intero, una data resta una data, un null resta un null. Più dettagli in
`docs/faq/parquet.md`.

## Tipi

| Nel contratto | Tipi polars accettati |
|---|---|
| intero | `pl.Int8` … `pl.Int64`, `pl.UInt8` … `pl.UInt64` |
| decimale | `pl.Float32`, `pl.Float64` |
| testo | `pl.String` |
| data | `pl.Date` (solo il giorno, senza ora) |

## `cards.parquet`: una riga per carta, con i prezzi di oggi

| Colonna | Tipo | Null ammessi | Note |
|---|---|---|---|
| `card_id` | intero | no | campo `id` dell'API, **unico** |
| `name` | testo | no | |
| `card_type` | testo | no | campo `type`, es. `Effect Monster`, `Spell Card` |
| `race` | testo | no | es. `Dragon`; per magie e trappole es. `Quick-Play` |
| `attribute` | testo | sì | l'elemento, es. `DARK`; vuoto per magie e trappole |
| `level` | intero | sì | numero di stelle |
| `attack` | intero | sì | campo `atk` |
| `defense` | intero | sì | campo `def` |
| `image_url` | testo | no | URL, oppure percorso relativo alla root del progetto (es. `data/images/89631139.jpg`) |
| `price_cardmarket` | decimale | sì | EUR, se valorizzato **> 0** |
| `price_tcgplayer` | decimale | sì | USD, se valorizzato **> 0** |
| `price_coolstuffinc` | decimale | sì | USD, se valorizzato **> 0** |

## `price_history.parquet`: una riga per carta per giorno

L'API dà solo il prezzo di **oggi**. Lo storico lo costruisci tu: ogni volta che la
pipeline gira, aggiungi i prezzi del giorno.

| Colonna | Tipo | Null ammessi | Note |
|---|---|---|---|
| `date` | data | no | il giorno in cui hai letto il prezzo |
| `card_id` | intero | no | deve esistere in `cards` |
| `price_cardmarket` | decimale | sì | EUR, se valorizzato **> 0** |
| `price_tcgplayer` | decimale | sì | USD, se valorizzato **> 0** |
| `price_coolstuffinc` | decimale | sì | USD, se valorizzato **> 0** |

La coppia `date` + `card_id` è **unica**: se la pipeline gira due volte nello stesso
giorno, lo storico non deve avere righe doppie.

## Regole generali

- **Un prezzo sconosciuto è `null`, non `0`.**
- **Niente stringhe vuote**: se un testo non c'è, salva `null`.
- I nomi delle colonne sono esattamente quelli qui sopra. Le colonne in più sono
  ammesse: vengono ignorate e segnalate come avviso.
- eBay e Amazon non servono: i loro prezzi non sono affidabili.

## Errori e avvisi

- **Errore**: l'app non può funzionare (colonna mancante, tipo sbagliato, prezzo a 0,
  righe doppie…). Le pagine si fermano.
- **Avviso**: l'app funziona, ma c'è qualcosa da guardare (per esempio lo storico ha
  un solo giorno, o i prezzi di `cards` non coincidono con l'ultimo giorno dello storico).

Esempio di file corretto: nel Controllo dati scegli "Dati mock".
