# API YGOPRODeck

Fonte dei dati: <https://ygoprodeck.com/api-guide/>. È gratuita e **non serve una chiave API**.

## Endpoint principale

```
GET https://db.ygoprodeck.com/api/v7/cardinfo.php
```

Senza parametri restituisce **tutte le carte** in una sola risposta (decine di MB).
Per il progetto basta questa chiamata: la fai una volta, salvi il JSON in `data/raw/`
e da lì in poi lavori solo sul file locale.

Parametri utili mentre fai le prove, per scaricare poco:

| Parametro | Esempio | Cosa fa |
|---|---|---|
| `id` | `?id=89631139` | una carta (o più id separati da virgola) |
| `name` | `?name=Dark Magician` | nome esatto |
| `fname` | `?fname=dragon` | ricerca parziale sul nome |
| `archetype` | `?archetype=Blue-Eyes` | tutte le carte di un archetipo |
| `num` + `offset` | `?num=50&offset=0` | paginazione (vanno usati insieme) |

## Regole d'uso, da rispettare

- **Massimo 20 richieste al secondo.** Se le superi, ti bloccano per un'ora.
- **Salva i dati in locale** e non richiamare l'API a ogni esecuzione: se il file raw
  di oggi esiste già, non riscaricarlo.
- **Immagini:** non vanno caricate continuamente dal loro server (hotlinking), pena
  il blocco dell'IP. Vanno **scaricate una volta**, salvate in locale (es.
  `data/images/<id>.jpg`) e usate da lì. Se ne scarichi tante, metti una pausa tra
  una richiesta e l'altra.

## Esempio minimo con requests

```python
import requests

URL = "https://db.ygoprodeck.com/api/v7/cardinfo.php"

response = requests.get(URL, params={"fname": "dragon"}, timeout=30)
response.raise_for_status()  # se lo status non è 2xx solleva un'eccezione
payload = response.json()     # dict con la chiave "data"
print(len(payload["data"]))
```

## Com'è fatta una carta (risposta ridotta)

```json
{
  "id": 89631139,
  "name": "Blue-Eyes White Dragon",
  "type": "Normal Monster",
  "frameType": "normal",
  "race": "Dragon",
  "attribute": "LIGHT",
  "archetype": "Blue-Eyes",
  "atk": 3000,
  "def": 2500,
  "level": 8,
  "card_sets": [
    {
      "set_name": "Legend of Blue Eyes White Dragon",
      "set_code": "LOB-EN001",
      "set_rarity": "Ultra Rare",
      "set_rarity_code": "(UR)",
      "set_price": "0"
    }
  ],
  "card_images": [
    {
      "id": 89631139,
      "image_url": "https://images.ygoprodeck.com/images/cards/89631139.jpg",
      "image_url_small": "https://images.ygoprodeck.com/images/cards_small/89631139.jpg",
      "image_url_cropped": "https://images.ygoprodeck.com/images/cards_cropped/89631139.jpg"
    }
  ],
  "card_prices": [
    {
      "cardmarket_price": "0.10",
      "tcgplayer_price": "0.13",
      "ebay_price": "5.95",
      "amazon_price": "3.90",
      "coolstuffinc_price": "0.99"
    }
  ]
}
```

Cose da notare:

- `card_sets`, `card_images` e `card_prices` sono **liste annidate** (in polars:
  colonne `List` di `Struct`). Per l'app servono la prima immagine e i prezzi di
  `cardmarket`, `tcgplayer` e `coolstuffinc`. eBay e Amazon li ignoriamo, perché
  hanno prezzi poco affidabili. `card_sets` non serve, ma se vuoi farci analisi in
  più è lì.
- **I prezzi sono stringhe**, non numeri, e `"0"` vuol dire "prezzo sconosciuto".
- L'API dà solo il prezzo **di oggi**: lo storico va costruito salvando i prezzi
  giorno per giorno.
- Non tutti i campi ci sono sempre: magie e trappole non hanno `atk`, `def`,
  `level`, `attribute`, e molte carte non hanno `archetype` o `card_sets`.
- I dati non sono perfettamente puliti. Guardali bene prima di fidarti.
