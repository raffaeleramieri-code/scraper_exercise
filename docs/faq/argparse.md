# argparse: dare opzioni a uno script

`argparse` è un modulo di Python (non c'è niente da installare) che ti permette di
scrivere cose del genere:

```bash
uv run python saluta.py --nome Valerio
```

e di ritrovarti `"Valerio"` dentro lo script. Vediamolo con un esempio piccolo,
un pezzo alla volta.

---

## 1. Un solo argomento

`saluta.py`:

```python
import argparse

parser = argparse.ArgumentParser()   # l'oggetto che legge il terminale
parser.add_argument("--nome")        # dichiari che esiste l'opzione --nome
args = parser.parse_args()           # legge quello che hai scritto

print("Ciao", args.nome)
```

`args.nome` contiene quello che hai scritto dopo `--nome`. Il nome dell'attributo è
quello dell'opzione senza i `--`.

```
$ uv run python saluta.py --nome Valerio
Ciao Valerio
```

### E se non scrivo `--nome`?

```
$ uv run python saluta.py
Ciao None
```

Lo script non dà errore: `args.nome` vale semplicemente `None`. E se scrivi
`--nome` ma ti dimentichi il valore, argparse si ferma:

```
$ uv run python saluta.py --nome
usage: saluta.py [-h] [--nome NOME]
saluta.py: error: argument --nome: expected one argument
```

---

## 2. Con un valore di default

Se non vuoi `None`, dai un valore di default:

```python
parser.add_argument("--nome", default="sconosciuto")
```

```
$ uv run python saluta.py
Ciao sconosciuto

$ uv run python saluta.py --nome Valerio
Ciao Valerio
```

Il default si usa **solo** se l'opzione non viene scritta.

### E se l'opzione è obbligatoria?

Al posto del default metti `required=True`. Così, se manca, lo script si ferma
subito:

```python
parser.add_argument("--nome", required=True)
```

```
$ uv run python saluta.py
usage: saluta.py [-h] --nome NOME
saluta.py: error: the following arguments are required: --nome
```

Riassumendo:

| Come lo dichiari | Se non scrivi l'opzione |
|---|---|
| `add_argument("--nome")` | `args.nome` vale `None` |
| `add_argument("--nome", default="sconosciuto")` | `args.nome` vale `"sconosciuto"` |
| `add_argument("--nome", required=True)` | errore, lo script non parte |

---

## 3. Più argomenti insieme

Basta chiamare `add_argument` una volta per ogni opzione. Qui ne aggiungiamo tre,
ognuna con una caratteristica diversa:

```python
import argparse

parser = argparse.ArgumentParser(description="Saluta qualcuno.")
parser.add_argument("--nome", default="sconosciuto", help="chi salutare")
parser.add_argument("--volte", type=int, default=1, help="quante volte salutare")
parser.add_argument("--urla", action="store_true", help="saluta in maiuscolo")
parser.add_argument("--lingua", choices=["it", "en"], default="it", help="lingua del saluto")
args = parser.parse_args()

saluto = "Ciao" if args.lingua == "it" else "Hello"
testo = f"{saluto} {args.nome}"
if args.urla:
    testo = testo.upper()
for _ in range(args.volte):
    print(testo)
```

Le novità:

| Parametro | Cosa fa |
|---|---|
| `type=int` | trasforma il valore in un intero: senza, sarebbe sempre una stringa |
| `action="store_true"` | opzione "interruttore", senza valore: se la scrivi vale `True`, se no `False` |
| `choices=[...]` | accetta solo i valori dell'elenco |
| `help="..."` | la descrizione che compare con `--help` |

Le opzioni si possono scrivere in qualsiasi ordine, e quelle che non scrivi
prendono il loro default:

```
$ uv run python saluta.py --nome Valerio --volte 2 --urla
CIAO VALERIO
CIAO VALERIO

$ uv run python saluta.py --lingua en
Hello sconosciuto
```

Se un valore è sbagliato, argparse si ferma e ti dice perché. Non devi scrivere tu
i controlli:

```
$ uv run python saluta.py --volte tre
usage: saluta.py [-h] [--nome NOME] [--volte VOLTE] [--urla] [--lingua {it,en}]
saluta.py: error: argument --volte: invalid int value: 'tre'
```

### `--help` lo scrive argparse

Con `--help`, o `-h`, ottieni l'elenco delle opzioni con la loro descrizione, senza
scrivere niente in più:

```
$ uv run python saluta.py --help
usage: saluta.py [-h] [--nome NOME] [--volte VOLTE] [--urla] [--lingua {it,en}]

Saluta qualcuno.

options:
  -h, --help        show this help message and exit
  --nome NOME       chi salutare
  --volte VOLTE     quante volte salutare
  --urla            saluta in maiuscolo
  --lingua {it,en}  lingua del saluto
```

---

Tutorial ufficiale, se vuoi approfondire: <https://docs.python.org/3/howto/argparse.html>
