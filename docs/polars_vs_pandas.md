# Polars al posto di pandas

In giro troverai quasi sempre esempi in pandas. In questo progetto usiamo **polars**,
che fa le stesse cose con un approccio un po' diverso.

## Perché polars

- **È veloce**: è scritto in Rust e usa tutti i core della CPU.
- **I tipi sono rigorosi**: una colonna ha un solo tipo, e se qualcosa non torna te
  lo dice subito, invece di trasformarlo in `object` senza dirti niente.
- **Non c'è l'indice**: niente `reset_index()`, niente `.loc` con l'indice che si
  sposta. Le righe sono solo righe.
- **Usa le espressioni**: descrivi *cosa* vuoi (`pl.col("prezzo") * 2`) e polars
  decide come farlo nel modo più efficiente.
- **Ha la modalità lazy**: con `scan_*` e `.lazy()` costruisci la query e la esegui
  alla fine con `.collect()`, così polars la ottimizza tutta insieme.

## Le stesse operazioni nelle due librerie

| Operazione | pandas | polars |
|---|---|---|
| leggere un parquet | `pd.read_parquet(p)` | `pl.read_parquet(p)` |
| scegliere colonne | `df[["a", "b"]]` | `df.select("a", "b")` |
| filtrare | `df[df["a"] > 1]` | `df.filter(pl.col("a") > 1)` |
| nuova colonna | `df["c"] = df["a"] * 2` | `df.with_columns((pl.col("a") * 2).alias("c"))` |
| rinominare | `df.rename(columns={"a": "x"})` | `df.rename({"a": "x"})` |
| cambiare tipo | `df["a"].astype(float)` | `df.with_columns(pl.col("a").cast(pl.Float64))` |
| raggruppare | `df.groupby("a")["b"].mean()` | `df.group_by("a").agg(pl.col("b").mean())` |
| ordinare | `df.sort_values("a", ascending=False)` | `df.sort("a", descending=True)` |
| join | `df.merge(other, on="id")` | `df.join(other, on="id")` |
| lista → righe | `df.explode("lista")` | `df.explode("lista")` |
| struct → colonne | `pd.json_normalize(...)` | `df.unnest("struct")` |
| valori nulli | `NaN` / `None` | sempre `null` |

## Da tenere a mente

- `df.with_columns(...)` **restituisce un nuovo DataFrame**, non modifica quello
  vecchio. Devi riassegnarlo: `df = df.with_columns(...)`.
- Per vedere com'è fatto un DataFrame: `df.schema`, `df.head()`, `df.describe()`,
  `df.glimpse()`.
- Polars legge i JSON annidati in colonne di tipo `List` e `Struct`. È proprio quello
  che serve per i dati dell'API.

Documentazione: <https://docs.pola.rs/>, in particolare la sezione
*"Coming from pandas"*.
