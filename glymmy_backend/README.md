# Glymmy Backend

FastAPI service implementing the Glymmy AI health platform.

## Architecture

```
                      ┌─────────────────┐
                      │   FastAPI App   │
                      └────────┬────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
   [Feature Modules]      [Adapters]             [RAG]
    glucose, food,      LLM | CGM | Labs       Chroma +
    labs, profile,       Storage               sentence-
    wearables, chat                            transformers
```

**Design principles:**

- **Singleton config** via `lru_cache` in `app/core/config.py`
- **Adapter pattern** — swap LLM, CGM, labs, storage providers by
  changing env vars (`LLM_PROVIDER`, `CGM_PROVIDER`, etc.)
- **Gemma 4 as default** — multimodal (text + vision), 256K context,
  Apache 2.0, runs locally via Ollama
- **Real clinical data** — GlucoBench (Dubosson + Hall) and MIMIC-IV Demo

## Running Locally

```bash
cd glymmy_backend
uv pip install -e .
cp .env.example .env
uv run uvicorn app.main:app --reload
```

Open http://localhost:8000/docs for the interactive API.

## API Overview

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Provider config + status |
| GET | `/api/v1/info` | Version + dataset stats |
| GET | `/api/v1/patients` | List all available patients |
| GET | `/api/v1/patients/{id}/profile` | Unified patient profile |
| GET | `/api/v1/patients/{id}/qr` | FHIR bundle + QR code |
| GET | `/api/v1/glucose/{id}` | CGM time series + summary |
| POST | `/api/v1/glucose/predict` | Meal → glucose spike prediction |
| GET | `/api/v1/glucose/{id}/hypo-check` | Nocturnal hypo alert |
| POST | `/api/v1/food/scan` | Photo → nutrition + spike |
| POST | `/api/v1/food/analyze-text` | Text → nutrition + spike |
| GET | `/api/v1/labs/{id}` | Lab events for a patient |
| POST | `/api/v1/labs/{id}/interpret` | AI interpretation of lab results |
| GET | `/api/v1/wearables/{id}` | Wearable data (HR, activity, insulin) |
| POST | `/api/v1/chat` | RAG chat (patient context + knowledge) |
| POST | `/api/v1/chat/stream` | SSE streaming chat |
| ALL  | `/graphql` | Strawberry GraphQL endpoint (Query + Mutation, GraphiQL UI) |

## GraphQL

Glymmy ships **both REST and GraphQL** on the same FastAPI app. They
share the same `service.py` business logic, so they're always in sync.

- **REST:** `http://localhost:8000/docs` (auto-generated Swagger UI)
- **GraphQL:** `http://localhost:8000/graphql` (interactive GraphiQL UI)

Example query:

```graphql
query {
  patients {
    id
    name
    diagnosis
  }
  glucoseSeries(patientId: "dubosson_1.0", limit: 100) {
    summary {
      mean
      timeInRangePct
    }
  }
}
```

Example mutation:

```graphql
mutation {
  predictMealSpike(
    patientId: "dubosson_1.0"
    meal: { carbsG: 60, proteinG: 15, fatG: 10, fiberG: 5 }
  ) {
    predictedSpikeMgDl
    risk
    explanation
  }
}
```

## Switching Providers

```bash
# Switch to Claude instead of local Gemma
export LLM_PROVIDER=anthropic
export ANTHROPIC_API_KEY=sk-...

# Switch to Nightscout for real CGM data
export CGM_PROVIDER=nightscout
```

No code changes needed — the factory resolves the new adapter on next
process start (or call `get_llm_adapter.cache_clear()`).
