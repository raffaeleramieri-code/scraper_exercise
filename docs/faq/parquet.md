# Cos'è un file Parquet

È un formato per salvare tabelle, come un CSV, ma con tre differenze importanti:

- **Salva i tipi delle colonne.** Un intero resta un intero, una data resta una
  data, un valore mancante resta `null`. In un CSV invece è tutto testo, e chi lo
  rilegge deve indovinare i tipi.
- **È colonnare.** I dati sono salvati colonna per colonna invece che riga per riga,
  quindi leggere solo alcune colonne è velocissimo.
- **È compresso.** Occupa molto meno spazio di un CSV.

Non si apre con un editor di testo, perché è un file binario. Con polars:

```python
import polars as pl

df.write_parquet("data/cleaned/cards.parquet")   # scrivere
df = pl.read_parquet("data/cleaned/cards.parquet")  # leggere
print(df.schema)                                  # i tipi sono ancora lì
```

(Nel codice vero usa i percorsi dinamici, non stringhe scritte a mano.)
