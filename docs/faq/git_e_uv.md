# Git e uv: i comandi che servono

Su Windows usa **Git Bash**, non PowerShell né il Prompt dei comandi: i comandi qui
sotto sono scritti per Git Bash.

> **Terminale bloccato?** Di solito si risolve con, in ordine:
> 1. `Ctrl + C`
> 2. `q` (se sei dentro una schermata tipo `git log`)
> 3. preghiere

## uv

uv gestisce la versione di Python, il virtual environment (`.venv/`) e le dipendenze
(`pyproject.toml` + `uv.lock`).

| Comando | Cosa fa |
|---|---|
| `uv init` | crea un nuovo progetto (qui è già fatto, **non** serve rilanciarlo) |
| `uv venv` | crea il virtual environment `.venv/` |
| `source .venv/Scripts/activate` | attiva il venv in Git Bash su Windows (su Linux e Mac: `.venv/bin/activate`) |
| `deactivate` | disattiva il venv |
| `uv sync` | installa nel venv esattamente le dipendenze del `uv.lock` |
| `uv add <pacchetto>` | aggiunge una dipendenza (aggiorna `pyproject.toml` e `uv.lock`) |
| `uv run <comando>` | esegue il comando dentro il venv, anche se non l'hai attivato |

La prima volta, dopo aver clonato la repo:

```bash
uv sync
```

Poi puoi lavorare in due modi:

```bash
# 1) senza attivare niente: uv run usa il venv da solo
uv run python main.py

# 2) attivando il venv: da qui "python" è quello del progetto
source .venv/Scripts/activate
python main.py
```

## git

| Comando | Cosa fa |
|---|---|
| `git status` | cosa è cambiato e cosa è pronto per il commit. **Usalo spesso.** |
| `git branch` | elenca i branch; quello attuale ha l'asterisco |
| `git checkout -b <nome>` | crea un nuovo branch e ci si sposta |
| `git checkout main` | si sposta su un branch che esiste già |
| `git add <file>` | prepara un file per il commit (`git add .` = tutto) |
| `git commit -m "messaggio"` | salva i file preparati in un commit |
| `git commit -am "messaggio"` | `add` + `commit` insieme, **ma solo per i file già tracciati** |
| `git pull` | scarica e unisce le modifiche dal remoto |
| `git push` | carica i tuoi commit sul remoto |
| `git log --oneline` | storia dei commit (si esce con `q`) |

Attenzione a `commit -am`: **i file nuovi li ignora**. Se hai creato un file, prima
fai `git add` su quel file.

In questo progetto si lavora direttamente su `main`.
