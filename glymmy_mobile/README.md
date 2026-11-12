# Glymmy Mobile

Expo-based mobile client for Glymmy.

## Purpose

This app is the patient-facing mobile experience for the existing FastAPI
backend in `../glymmy_backend`.

V1 direction:
- `Now` for current glucose and real-time status
- `Meals` for food analysis and spike prediction
- `Trends` for recent device data
- `Labs` for plain-language interpretation
- `Care` for chat and doctor-sharing flows

## Getting Started

1. Install dependencies:

```bash
cd glymmy_mobile
npm install
```

2. Create env file:

```bash
cp .env.example .env
```

3. Start the backend in another terminal:

```bash
cd glymmy_backend
uv run uvicorn app.main:app --reload
```

4. Start Expo:

```bash
cd glymmy_mobile
npm run dev
```

If you are testing on a physical device, set `EXPO_PUBLIC_API_URL` to a LAN-reachable
backend URL rather than `localhost`.

## Notes

- The current scaffold uses existing backend endpoints first instead of inventing a
  new backend surface.
- Chat may fail if local embedding assets or Ollama are not available.
- The labs screen still uses a demo patient path for now; later it should move to
  a user-scoped `/users/me/labs` style flow.
