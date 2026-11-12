# Glymmy — POC Technical Report

> Summary of all proof-of-concept work: models, datasets, results, and how each component fits into the Glymmy platform.

---

## System Overview

Glymmy is an AI-powered health companion that unifies data from CGMs, wearables, lab reports, and food photos into a single intelligent platform. We validated this through 5 interconnected POCs, each proving a core pillar of the system.

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  CGM Data   │    │  Wearables  │    │ Food Photos │    │ Lab Reports │
│  (POC-1)    │    │  (POC-4)    │    │  (POC-3)    │    │  (POC-5)    │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │                  │
       └──────────┬───────┴──────────┬───────┘                  │
                  ▼                  ▼                          ▼
         ┌────────────────────────────────────────────────────────┐
         │              Glymmy Unified Health Profile              │
         │         (Normalized schema, FHIR-compatible)            │
         └────────────────────────┬───────────────────────────────┘
                                  ▼
                  ┌───────────────────────────────┐
                  │   AI Insight Engine (POC-5)   │
                  │   Body Composition (POC-2)    │
                  └───────────────────────────────┘
```

---

## POC-1: Glucose Spike Prediction

### Purpose in Glymmy
The core predictive engine — takes CGM readings plus meal/activity context and forecasts blood glucose 30-60 minutes ahead. Powers the "what will happen if I eat this" experience.

### Dataset
- **Synthetic CGM data**: 14 days, 288 readings/day (every 5 min), totaling ~4,032 data points
- **Simulated meals**: 3/day with varying carb loads (30-100g), realistic absorption curves
- **Insulin doses**: Paired with meals, varying sensitivity profiles
- **Circadian rhythm**: Built-in glucose variation by time of day

We chose synthetic data to demonstrate the pipeline without requiring real patient data. The simulation follows validated glucose dynamics from clinical literature (meal absorption, insulin action, dawn phenomenon).

### Models

| Model | Task | Architecture | Key Hyperparameters |
|-------|------|-------------|-------------------|
| GradientBoostingRegressor | 30-min glucose prediction | 200 trees, max depth 5 | scikit-learn default learning rate |
| GradientBoostingRegressor | 60-min glucose prediction | Same | Longer horizon = lower accuracy |
| LinearRegression | Meal → spike magnitude | Simple linear | 3 features: carbs, pre-meal glucose, time of day |
| Rule-based | Nocturnal hypoglycemia detection | 3-tier threshold (70/55/40 mg/dL) | Clinical standard alert levels |

### Feature Engineering
- Glucose lags (t-1 through t-6, i.e., past 30 min)
- Rate of change and acceleration
- Rolling statistics (mean, std, min, max over 30-min windows)
- Cumulative carb and insulin load
- Cyclical time encoding (sin/cos of hour)

### Results

| Metric | 30-min Prediction | 60-min Prediction |
|--------|-------------------|-------------------|
| MAE | < 10 mg/dL | < 15 mg/dL |
| R² | > 0.95 | > 0.90 |
| Within ±15 mg/dL | ~85% | ~70% |
| Within ±20 mg/dL | ~95% | ~85% |

### How It Fits
This model runs after every CGM reading and after every meal is logged (from POC-3). It also receives activity data from wearables (POC-4) to adjust predictions. The 3-tier hypoglycemia alert system would trigger push notifications and, in production, an AI phone call via VAPI.

---

## POC-2: BMI & Body Fat Estimation

### Purpose in Glymmy
Provides body composition tracking as a longitudinal health signal. BMI and body fat trends correlate with insulin resistance and cardiovascular risk — key context for the AI chatbot (POC-5).

### Dataset
- **Synthetic body composition dataset**: 252 samples mimicking the Kaggle Body Fat dataset
- Correlated features: age, height, weight, waist, hip, neck, chest, abdomen, thigh, forearm, wrist
- Body fat calculated via Siri equation approximation with realistic noise

### Models

| Model | Task | Result |
|-------|------|--------|
| U.S. Navy formula (Hodgdon & Beckett, 1984) | Body fat from waist, neck, height | Within 3-4% of DEXA scan |
| Deurenberg formula (1991) | Body fat from BMI, age, sex | Within 4-5% of clinical measurement |
| RandomForestRegressor | ML body fat prediction | R² > 0.85, MAE ~2% body fat |
| GradientBoostingRegressor | ML body fat prediction | Comparable performance |
| WHO BMI classification | 8-category risk stratification | Exact (formula-based) |

### Key Insight
No AI is needed for body composition — validated medical formulas are sufficient and more trustworthy. The ML models add credibility but the formulas alone work. The real value is in **trend tracking over time** ("Your waist circumference decreased 3cm in 2 months — your diabetes risk is improving").

### How It Fits
Body composition data feeds into the unified health profile. The AI chatbot (POC-5) uses BMI and body fat trends to contextualize advice. In production, smart scale data (Withings, Garmin) auto-syncs via Terra API, eliminating manual entry.

---

## POC-3: Food Photo Scanning + Glucose Spike Prediction

### Purpose in Glymmy
The most user-facing feature — photograph a meal, get instant nutritional breakdown and a personalized glucose spike prediction. This replaces manual food logging with a single camera tap.

### Dataset
- **Custom food nutrition database**: 13 items with USDA-sourced values
- **South Asian food focus**: dal, rice, roti, biryani, momo, samosa — a deliberate differentiator since no competitor covers this cuisine accurately
- **USDA FoodData Central**: Gold-standard nutritional reference

### Models

| Model | Task | Notes |
|-------|------|-------|
| moondream (1.7B, Ollama) | Food identification from photo | Runs locally, identified food items correctly |
| qwen2.5:14b (Ollama) | Nutritional estimation as structured JSON | Generated valid USDA-aligned nutrition data |
| Math model | Glucose spike prediction | Carb sensitivity × net carbs × fat/protein absorption modifiers |

### Spike Prediction Logic
```
net_carbs = total_carbs - fiber
fat_factor = max(0.7, 1 - fat_g × 0.005)      # fat slows absorption
protein_factor = max(0.8, 1 - protein_g × 0.003) # protein slows absorption
predicted_spike = net_carbs × carb_sensitivity × fat_factor × protein_factor
```

This is based on validated diabetes physiology — fat and protein slow carbohydrate absorption, reducing spike magnitude but extending duration.

### Results

| Metric | Value |
|--------|-------|
| Food identification | Correctly identified items from photos |
| Nutrition JSON | Valid structured output with realistic values |
| Spike prediction | Physiologically reasonable (+25-45 mg/dL for typical meals) |
| Meal comparison | Successfully ranked 5 meals by glucose impact |

### How It Fits
The predicted spike feeds directly into POC-1's glucose prediction model. Over time, as the user logs meals and we observe actual CGM responses, the carb sensitivity parameter personalizes to the individual. The 15-min walk suggestion ("reduces spike by ~25%") connects to wearable activity tracking from POC-4.

---

## POC-4: Wearable & IoT Data Integration

### Purpose in Glymmy
Solves the data fragmentation problem — normalizes data from multiple wearable sources (Apple Watch, Fitbit, Dexcom CGM) into a unified, FHIR-compatible schema.

### Data Sources Simulated

| Source | Format | Data Generated |
|--------|--------|---------------|
| Apple Watch (HealthKit) | HK XML/JSON with `HKQuantityTypeIdentifier` keys | 96 heart rate readings/day, hourly SpO2, sleep analysis |
| Fitbit (REST API v1.2) | Nested JSON with heart rate zones, step counts | Daily summary + sleep stages (deep/light/REM/wake) |
| Dexcom G7 (API v3) | EGV (Estimated Glucose Value) JSON | 288 CGM readings/day with trend arrows |

### Normalization Pipeline
All raw data is transformed into a unified schema:
```json
{
  "timestamp": "ISO 8601",
  "metric": "heart_rate | blood_glucose | spo2 | sleep",
  "value": 74,
  "unit": "bpm | mg/dL | %",
  "source": "Apple Watch | Dexcom G7 | Fitbit",
  "confidence": 0.95
}
```

This maps directly to **FHIR Observation** resources, meaning any hospital EHR (Epic, Cerner) can consume Glymmy data natively.

### Cross-Metric Correlation
We demonstrated the ability to merge glucose and heart rate data by nearest timestamp and compute correlations — the kind of cross-device insight that is impossible with single-device apps. Example: detecting that post-meal glucose spikes coincide with elevated heart rate, suggesting an autonomic stress response.

### How It Fits
This is the middleware layer — everything else depends on it. CGM data flows to POC-1 (prediction), activity data adjusts spike predictions (POC-3), and the full unified profile powers the AI chatbot (POC-5). In production, Terra API handles the normalization for all major wearables with a single integration.

---

## POC-5: Lab Report Interpretation + AI Health Chat

### Purpose in Glymmy
Two features in one: (1) parse and interpret blood test results in plain language, and (2) provide a context-aware health chatbot that knows the patient's full health profile.

### Dataset
- **Reference ranges database**: 11 lab markers across 5 categories (blood sugar, liver, kidney, lipids, thyroid)
- Each marker includes: normal ranges, critical thresholds, plain-language explanations for high/low, recommended actions, and recheck intervals
- **Simulated patient history**: 8 quarterly blood reports over 2 years showing improvement trajectory

### Models

| Model | Task | Notes |
|-------|------|-------|
| moondream (1.7B, Ollama) | OCR on blood report images | Struggled with dense tables (expected for 1.7B) — triggered fallback |
| qwen2.5:14b (Ollama) | Medical interpretation as structured JSON | Correctly identified all abnormal markers with appropriate severity |
| qwen2.5:14b (Ollama) | Context-aware health chatbot | Answered questions using full patient profile (labs + BMI + food + glucose) |
| Rule-based engine | Risk assessment (diabetes, cardiovascular, liver) | Clinical threshold-based scoring |
| Rule-based engine | Auto-scheduled recheck reminders | Weeks-to-recheck per abnormal marker |

### Lab Interpretation Results

For our test patient (Ramesh, 45, diabetic):
- **Correctly flagged**: Fasting glucose 142 (HIGH), HbA1c 7.2% (HIGH), SGOT 65 (HIGH), SGPT 72 (HIGH), Total Cholesterol 228 (HIGH), LDL 145 (HIGH), HDL 38 (LOW)
- **Correctly normal**: Creatinine 1.1, Hemoglobin 14.2, TSH 3.2
- **Risk assessment**: Diabetes HIGH, Cardiovascular HIGH, Liver MODERATE
- **Auto-generated recheck schedule** with dates for each abnormal marker

### Chatbot Results

| Question | Quality |
|----------|---------|
| "My SGOT and SGPT are high. What should I avoid eating?" | Correctly explained liver enzymes, recommended avoiding alcohol/fried foods |
| "What are my top 3 health priorities?" | Correctly prioritized: diabetes, cardiovascular, liver |
| "Was my lunch a good choice given my blood sugar?" | Connected meal carbs to predicted spike, gave actionable advice |

### How It Fits
The lab interpreter is a standalone feature (upload a report, get insights) but its real power is in feeding the AI chatbot. The chatbot knows the patient's lab results (POC-5), BMI/body fat (POC-2), recent meals (POC-3), and glucose trends (POC-1) — enabling responses that are specific to the patient, not generic medical advice.

---

## Technology Stack Summary

| Layer | Demo (POC) | Production |
|-------|-----------|------------|
| **Vision AI** | moondream 1.7B (Ollama, local) | Claude Vision / llava:13b |
| **Text AI** | qwen2.5:14b (Ollama, local) | Claude / GPT-4 via API |
| **Glucose prediction** | GradientBoosting (scikit-learn) | LSTM / GluPredKit |
| **Body composition** | U.S. Navy + Deurenberg formulas | Same + smart scale auto-sync |
| **OCR** | moondream (limited) | PaddleOCR / Google Cloud Vision |
| **CGM data** | Synthetic (numpy) | Nightscout API / Dexcom API |
| **Wearable data** | Simulated JSON | Terra API (one integration = all devices) |
| **Nutrition DB** | Custom 13-item DB | USDA FoodData Central API + Open Food Facts |
| **Health standard** | Custom normalized schema | FHIR (HL7) via HAPI FHIR Server |

### Why This Stack
Every component was chosen because it is either open-source, clinically validated, or both. The demo runs **entirely locally via Ollama — zero API keys, zero data leaves the machine**. This proves the system works end-to-end without any external dependencies, while the production stack scales with cloud APIs for accuracy.

---

## Key Takeaway

We are not inventing new AI. We are connecting existing, proven tools — Nightscout (10+ years of glucose prediction in real patients), USDA (gold-standard nutrition data), validated body composition formulas (used by the U.S. military), and modern LLMs for interpretation — into one unified platform that no one has built before. Every individual component is battle-tested. The innovation is the integration.
