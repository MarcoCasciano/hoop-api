# Hoop API

API REST per la registrazione e il tracciamento delle estrazioni di caffè con la macchina **Ceado Hoop**.

Costruita con **FastAPI** e **PostgreSQL**, permette di salvare ogni estrazione con i suoi parametri (dose, ratio, temperatura, macinatura) e ricevere suggerimenti automatici per migliorarla in base al rating.

---

## Struttura del progetto

```
hoop_app/
├── app/
│   ├── main.py              # Entry point FastAPI, definizione degli endpoint
│   ├── domain/
│   │   └── schemas.py       # Modelli Pydantic (BrewCreate, BrewUpdate, BrewOut)
│   ├── services/
│   │   └── brew_service.py  # Business logic (calcolo acqua, suggerimenti)
│   └── db/
│       ├── database.py      # Connessione PostgreSQL (psycopg)
│       └── init_db.py       # Creazione tabella al primo avvio
├── tests/
│   ├── conftest.py          # Fixture pytest (DB di test, TestClient)
│   ├── test_api.py          # Test di integrazione degli endpoint
│   └── test_brew_service.py # Test unitari della business logic
├── docker-compose.yml       # PostgreSQL + API containerizzati
├── requirements.txt         # Dipendenze di produzione
└── requirements-dev.txt     # Dipendenze di sviluppo (pytest, ecc.)
```

---

## Requisiti

- Python 3.12+
- Docker e Docker Compose

---

## Avvio in locale

### 1. Clona il repository e crea il virtual environment

```bash
git clone https://github.com/MarcoCasciano/hoop_app.git
cd hoop_app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configura le variabili d'ambiente

Crea un file `.env` nella root del progetto:

```
DATABASE_URL=postgresql://hoop:hoop@localhost:5432/hoop_db
```

### 3. Avvia il database

```bash
docker compose up -d db
```

### 4. Avvia l'API

```bash
uvicorn app.main:app --reload
```

L'API sarà disponibile su `http://localhost:8000`.
La documentazione interattiva (Swagger UI) su `http://localhost:8000/docs`.

---

## Avvio con Docker Compose

Per avviare sia il database che l'API in un unico comando:

```bash
cp .env.docker.example .env.docker
docker compose up
```

---

## Endpoint

| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/brews` | Crea una nuova estrazione |
| `GET` | `/brews` | Lista delle ultime estrazioni (default 50, max 200) |
| `GET` | `/brews/{id}` | Dettaglio di una singola estrazione |
| `PATCH` | `/brews/{id}` | Aggiornamento parziale di un'estrazione |
| `DELETE` | `/brews/{id}` | Eliminazione di un'estrazione |
| `GET` | `/brews/{id}/tips` | Suggerimenti per migliorare l'estrazione |

### Esempio: crea una brew

```bash
curl -X POST http://localhost:8000/brews \
  -H "Content-Type: application/json" \
  -d '{
    "coffee": "Ethiopia Yirgacheffe",
    "dose": 18.0,
    "ratio": 16.0,
    "temperature": 94,
    "grind": "medium",
    "rating": 7,
    "notes": "floreale, acidità intensa"
  }'
```

Il campo `water` viene calcolato automaticamente dal server (`dose × ratio`).

---

## Test

### Requisiti

Avvia il database di test (se non è già in esecuzione):

```bash
docker compose up -d db
docker exec hoop_db psql -U hoop -d hoop_db -c "CREATE DATABASE hoop_test_db;"
```

Installa le dipendenze di sviluppo:

```bash
pip install -r requirements-dev.txt
```

### Esegui i test

```bash
pytest tests/ -v
```

I test unitari (service layer) non richiedono il database e girano anche senza Docker:

```bash
pytest tests/test_brew_service.py -v
```
