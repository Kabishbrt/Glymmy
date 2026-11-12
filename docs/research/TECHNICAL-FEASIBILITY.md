# Glymmy — Technical Documentation

> One document covering all POCs, what AI we tested, what works, and what we'd use in production.

---

## POC Overview

| POC | Feature | AI Used (Demo) | AI for Production | Status |
|-----|---------|----------------|-------------------|--------|
| POC-1 | Glucose Spike Prediction | GradientBoosting (scikit-learn) | LSTM / GluPredKit + real CGM data | Validated |
| POC-2 | BMI & Body Fat | No AI — validated medical formulas | Same formulas + auto-sync from smart scale | Validated |
| POC-3 | Food Photo Scanning | Simulated pipeline + USDA DB | Claude Vision / llava:13b + USDA API | Validated |
| POC-4 | Blood Report Analysis | moondream (vision) + qwen2.5 (text) | PaddleOCR + Claude / GPT-4 | Validated |
| POC-5 | AI Health Chat | qwen2.5:14b (local, Ollama) | Claude / GPT-4 with RAG over patient data | Validated |
| Live Demo | All above combined | moondream + qwen2.5 (fully local, zero API keys) | Cloud LLMs + on-device fallback | Validated |

---

## POC-1: Glucose Spike Prediction

### What We Built
- Generated 14 days of synthetic CGM data (288 readings/day, every 5 min)
- 3 meals/day with varying carb loads (30-100g), insulin doses, circadian rhythm
- Feature engineering: glucose lags, rate of change, rolling stats, cumulative carbs/insulin, time encoding
- Trained GradientBoosting for 30-min and 60-min ahead prediction
- Personalized meal → spike model (carbs + pre-meal glucose + time of day → spike magnitude)
- Nocturnal hypoglycemia detection with 3-tier alert system

### AI/Models Tested (Demo)
| What | Tool | Why |
|------|------|-----|
| 30-min glucose predictor | `GradientBoostingRegressor` (scikit-learn, 200 trees, depth 5) | Best for tabular time-series, no GPU needed |
| 60-min glucose predictor | Same architecture | Slightly lower accuracy at longer horizon |
| Meal → spike model | `LinearRegression` (scikit-learn) | Simple, interpretable, captures carb sensitivity |
| Hypo detection | Rule-based thresholds (70/55/40 mg/dL) | Clinical standard |

### Results
| Metric | 30-min Prediction | 60-min Prediction |
|--------|-------------------|-------------------|
| MAE | < 10 mg/dL | < 15 mg/dL |
| R² | > 0.95 | > 0.90 |
| Within ±15 mg/dL | ~85% | ~70% |
| Within ±20 mg/dL | ~95% | ~85% |

### What We'd Use in Production
| Component | Production Tool | Why Better |
|-----------|----------------|-----------|
| Prediction model | **LSTM neural network** or **Personalized DIY Predictor** (github.com/antorguez95) | Captures temporal sequences better; validated on 29 real T1D patients |
| Alternative | **GluPredKit** (open-source framework) | Supports multiple ML models, handles data fetching/processing/evaluation |
| CGM data source | **Nightscout REST API** (real CGM data) | 30k+ active users, supports Dexcom G6/G7, Libre 1/2/3 |
| Meal data | Food scanning pipeline (POC-3) auto-populates carb intake | No manual entry needed |
| Activity data | **Terra API** → heart rate, steps | Adds exercise as a prediction feature |
| Reference algorithm | **OpenAPS oref0** | Powers open-source artificial pancreas systems used by thousands daily for 10+ years |

### Key Evidence It Will Work
- OpenAPS has been predicting glucose in production for 10+ years in real diabetic patients
- GluPredKit benchmarked on public CGM datasets (OhioT1DM)
- Scripps Research (2025): AI combining CGM + diet + activity detects hidden diabetes risk that HbA1c misses
- 87% of CGM users change food choices based on glucose spike feedback

---

## POC-2: BMI & Body Fat

### What We Built
- BMI calculator with full WHO classification (8 categories from Severe Thinness to Obese III)
- Body fat estimation via 2 validated formulas:
  - U.S. Navy method (Hodgdon & Beckett, 1984): uses waist, neck, height
  - Deurenberg method (1991): uses BMI, age, sex
- ML-based body fat predictor (Random Forest on 252-sample synthetic dataset)
- 12-month health trend tracking visualization

### AI/Models Tested (Demo)
| What | Tool | Why |
|------|------|-----|
| BMI | Direct formula: `weight / height²` | WHO standard, no AI needed |
| Body fat | U.S. Navy + Deurenberg formulas | Clinically validated, no AI needed |
| ML body fat | `RandomForestRegressor` + `GradientBoostingRegressor` (scikit-learn) | Proves ML can predict BF% from simple measurements |

### Results
| Metric | Value |
|--------|-------|
| BMI calculation | Exact (formula-based) |
| Navy body fat accuracy | Within 3-4% of clinical DEXA scan |
| Deurenberg accuracy | Within 4-5% of clinical measurement |
| ML body fat R² | > 0.85 |
| ML body fat MAE | ~2% body fat |

### What We'd Use in Production
| Component | Production Tool | Why Better |
|-----------|----------------|-----------|
| Weight input | Auto-sync from **Withings / Garmin smart scale** via Terra API | No manual entry, daily tracking |
| Height input | One-time user input or from health records | Static measurement |
| Waist/hip/neck | Periodic user measurement (guided by app) | Could explore AR body measurement in future |
| Trend tracking | Time-series database (InfluxDB or Supabase) | Persistent storage, fast queries |

### Key Evidence It Will Work
- These formulas are used by the U.S. military and WHO globally — no validation risk
- Smart scale integration is a solved problem (Terra API supports Withings, Garmin, Renpho)
- The value is not in the calculation — it's in the **trend tracking + AI insights** ("Your waist circumference decreased 3cm in 2 months — your diabetes risk is improving")

---

## POC-3: Food Photo Scanning + Nutrition

### What We Built
- Comprehensive food nutrition database (13 items with South Asian focus: dal, rice, roti, biryani, momo, samosa, etc.)
- Full pipeline simulation: food identification → nutritional lookup → glucose spike prediction
- Glucose spike predictor from meal composition (net carbs × carb sensitivity × fat/protein absorption modifiers)
- Meal comparison feature (5 different meals compared side-by-side)
- Production API call template for Claude Vision

### AI/Models Tested (Demo)
| What | Tool | Why |
|------|------|-----|
| Food identification | **moondream** (1.7B vision model, Ollama) | Runs on laptop, identified food items from our sample image |
| Nutrition estimation | **qwen2.5:14b** (text model, Ollama) | Generated structured JSON with per-item nutrition data |
| Spike prediction | Math model (carb sensitivity × net carbs × absorption factors) | Based on validated diabetes physiology |
| Nutrition database | Custom-built (USDA + South Asian sources) | USDA FoodData Central is the gold standard |

### Results
| Metric | Value |
|--------|-------|
| moondream food identification | Correctly identified food items from diagram (limited by synthetic image) |
| qwen2.5 nutrition JSON | Generated valid JSON with realistic USDA-aligned values |
| Spike prediction | Physiologically reasonable (+25-45 mg/dL for typical meals) |
| Meal comparison | Successfully ranked 5 meals by glucose impact |

### What We'd Use in Production
| Component | Production Tool | Why Better |
|-----------|----------------|-----------|
| Food recognition | **Claude Vision** or **llava:13b** (via Ollama) | Much higher accuracy, handles complex/mixed dishes |
| Alternative | **Food-101 fine-tuned EfficientNet** + **YOLO for multi-item detection** | Faster inference, works offline on mobile |
| Nutrition lookup | **USDA FoodData Central API** + **Open Food Facts API** (3M+ products) + **custom South Asian DB** | Verified data, not LLM-generated estimates |
| Portion estimation | **Depth estimation** (iPhone LiDAR / stereo camera) or user adjustment slider | Reduces the ~20-30% portion estimation error |
| Spike prediction | Personalized model trained on user's own CGM + meal history | Accuracy improves with each meal logged |

### Key Evidence It Will Work
- **Cal AI** (1M+ downloads, 4.7 stars) — proves photo-based calorie tracking has market demand
- **SNAQ** — photo-based carb counting connected to CGMs already exists (but poorly executed)
- **January AI** — predicts glucose from food photos even without a CGM (clinically validated model)
- Food-101 benchmark is considered solved (90%+ accuracy with modern architectures)
- The gap: nobody combines accurate food scanning + CGM correlation + South Asian cuisine support

### Competitors & Their Problems (Why We're Better)
| Competitor | What They Do | Users Complain About |
|-----------|-------------|---------------------|
| Cal AI | Photo calorie tracking | "Accuracy way off for mixed meals", "90% of functions don't work" |
| SNAQ | Photo carb counting for diabetics | "Pattern tracking doesn't work", 44% error rate in real-world |
| January AI | Glucose prediction from food | "Banana predicted low impact but spiked to 141", costs $288/mo |
| Signos | CGM + food tracking | "Meal logging is God-awful", costs $149-299/mo |
| Nutrisense | CGM + dietitian | "App is overwhelming", $199-399/mo, hard to cancel |

---

## POC-4: Blood Report Analysis

### What We Built
- Image-based lab report reading (moondream vision model)
- Smart fallback when OCR quality is poor (quality detection + structured fallback)
- AI interpretation of abnormal markers with severity, explanation, and action
- Multi-organ risk assessment (diabetes, cardiovascular, liver)
- Top recommendations + follow-up schedule

### AI/Models Tested (Demo)
| What | Tool | Why |
|------|------|-----|
| Report OCR | **moondream** (1.7B vision, Ollama) | Runs locally, attempted text extraction from report image |
| Fallback OCR | Structured simulation (demonstrates production OCR pipeline) | moondream too small for dense table text |
| Interpretation | **qwen2.5:14b** (text, Ollama) | Generated structured JSON with medical interpretation |
| Risk scoring | Rule-based + AI hybrid | Clinical thresholds for diabetes/CVD/liver risk |

### Results
| Metric | Value |
|--------|-------|
| moondream OCR on dense table | Poor — hallucinated repeated values (expected for 1.7B model) |
| Fallback + qwen2.5 interpretation | Correctly identified all abnormal markers, appropriate severity ratings |
| Risk assessment | Accurately flagged high diabetes risk (glucose 142 + HbA1c 7.8%) and liver concern (SGOT 65 + SGPT 72) |
| Recommendations | Clinically reasonable (diet changes, medication review, follow-up labs) |

### What We'd Use in Production
| Component | Production Tool | Why Better |
|-----------|----------------|-----------|
| OCR (photo reports) | **PaddleOCR** (open-source, 80+ languages) or **Google Cloud Vision OCR** | Purpose-built for text extraction, much higher accuracy on tables |
| OCR (PDF reports) | **PyMuPDF** / **pdfplumber** (extract text directly from digital PDFs) | Near-perfect accuracy on structured PDFs |
| Lab data integration | **Health Gorilla API** (connects to Quest Diagnostics, Labcorp) | Structured HL7/FHIR data, no OCR needed |
| Interpretation | **Claude** / **GPT-4** with medical knowledge + rule-based validation | Higher accuracy, can cite medical references |
| Validation layer | Rule-based checks (e.g., glucose > 500 → likely OCR error, hemoglobin > 20 → impossible) | Catches AI/OCR errors before showing to user |

### Key Evidence It Will Work
- **Docus AI** — already does lab report interpretation in production (300k+ users)
- **Kantesti** — claims 98.7% accuracy on lab interpretation (2M+ users, free)
- **SiPhox Health** — offers free lab upload + AI analysis
- The interpretation part is the easy part (rule-based: value vs. range). The hard part is OCR, which PaddleOCR solves.

### Competitors & Their Problems
| Competitor | Problem |
|-----------|---------|
| Docus AI | Prone to PDF parsing errors, $300-1200/yr |
| SiPhox Health | 300-600% accuracy discrepancies on some markers |
| All of them | Standalone — none connect lab results to CGM trends, food, or wearable data |

---

## POC-5: AI Health Chatbot

### What We Built
- Context-aware health chatbot that knows the patient's:
  - Lab results (from POC-4)
  - BMI / body fat (from POC-2)
  - Recent food intake (from POC-3)
  - Glucose trends (from POC-1)
- Answered 3 demo questions with personalized, data-aware responses
- Included medical disclaimers automatically

### AI/Models Tested (Demo)
| What | Tool | Why |
|------|------|-----|
| Chat model | **qwen2.5:14b** (Ollama, local) | Best local model for medical knowledge + structured reasoning |
| Context injection | System prompt with full patient health profile | Simple RAG — all data fits in context window |

### Results
| Question | Quality of Response |
|----------|-------------------|
| "My SGOT and SGPT are high. What should I avoid eating?" | Correctly explained liver enzymes, recommended avoiding alcohol/fried foods, suggested follow-up |
| "What are my top 3 health priorities?" | Correctly prioritized: diabetes management, cardiovascular risk, liver health |
| "Was my lunch a good choice given my blood sugar?" | Connected meal carbs to predicted spike, gave actionable advice |

### What We'd Use in Production
| Component | Production Tool | Why Better |
|-----------|----------------|-----------|
| Chat model | **Claude** or **GPT-4** via API | Higher accuracy, better medical reasoning, supports tool use |
| Context / memory | **RAG with vector DB** (ChromaDB / Pinecone) | Scales to months/years of patient history |
| Safety layer | **Guardrails AI** or custom rules | Prevents dangerous medical advice, enforces disclaimers |
| Voice interface | **VAPI** or **Bland.ai** | AI phone calls for reminders ("Time to check your glucose") |
| Multilingual | Claude/GPT-4 natively, or fine-tuned local models | Support Nepali, Hindi, Bengali for South Asian users |

### Key Evidence It Will Work
- Hackathon challenge #3 is literally "Intelligent Support Chatbots" — we're directly answering this
- ChatGPT / Claude already answer medical questions well; the innovation is **patient-specific context**
- The difference between "What does high SGOT mean?" (generic) and "Your SGOT is 65 which is 44% above normal, and combined with your SGPT of 72, this suggests mild liver stress — here's what to do" (Glymmy)

---

## Wearable & CGM Data Integration

### How We Actually Get Data from Devices

| Data Source | Protocol | Tool | What We Get |
|-------------|----------|------|-------------|
| Dexcom G6/G7 | BLE → xDrip+ → Nightscout | **xDrip+** (open-source Android app) | Glucose every 5 min, trend arrows |
| Libre 1/2/3 | NFC/BLE → LibreLink → Nightscout | **Nightscout** (open-source cloud) | Glucose readings, sensor data |
| Apple Watch | BLE → HealthKit → our app | **Apple HealthKit** (iOS SDK) | HR, SpO2, sleep, steps, ECG |
| Fitbit / Garmin / Oura | Cloud API → Terra → our app | **Terra API** (middleware) | HR, HRV, sleep, steps, SpO2 |
| Smart scales | BLE/WiFi → Health Connect / Terra | **Google Health Connect** or **Terra** | Weight, body fat %, BMI |

### BLE Communication (How Wearables Actually Talk)

All modern health wearables use **Bluetooth Low Energy (BLE)** with standardized GATT profiles:

```
[Wearable Device]
    ↓ BLE (Bluetooth Low Energy)
[GATT Profile: Heart Rate 0x180D / Glucose 0x1808 / etc.]
    ↓ standardized data packets
[Phone App: xDrip+ / HealthKit / Health Connect]
    ↓ REST API or local DB
[Glymmy App]
```

These are open Bluetooth SIG standards — not proprietary. xDrip+ and Gadgetbridge already implement them.

### Nightscout API (Our Primary CGM Data Source)

```python
import requests

# Get last 24 hours of glucose readings
nightscout_url = "https://your-nightscout.herokuapp.com"
response = requests.get(f"{nightscout_url}/api/v1/entries.json", params={
    "count": 288,  # 24 hours × 12 readings/hour
    "token": "your-api-secret"
})

# Returns:
# [{"sgv": 142, "date": 1711123200, "direction": "Flat"}, ...]
```

---

## Privacy & Compliance Summary

| Concern | How We Handle It |
|---------|-----------------|
| Data storage | Encrypted at rest (AES-256), in transit (TLS 1.3) |
| FDA status | **General wellness** product — exempt per Jan 2026 FDA guidance |
| HIPAA | Cloud provider with BAA, audit logs, access controls |
| Patient data ownership | Export anytime (FHIR bundle), delete anytime |
| Demo data | Fully local via Ollama — zero data leaves the machine |
| Clinical claims | Never diagnostic. Always "consult your doctor." |

---

## Full Open-Source Stack

| Layer | Tool | License |
|-------|------|---------|
| AI Runtime | Ollama | MIT |
| Vision AI | moondream / llava | Apache 2.0 |
| Text AI | Qwen 2.5 (14B) | Apache 2.0 |
| CGM Data | Nightscout + xDrip+ | AGPL-3.0 / GPL-3.0 |
| Wearable Bridge | Gadgetbridge | AGPL-3.0 |
| Health Standard | HAPI FHIR Server | Apache 2.0 |
| ML Models | scikit-learn | BSD-3 |
| Visualization | matplotlib + seaborn | BSD / MIT |
| Nutrition DB | USDA FoodData Central | Public Domain |
| Food DB | Open Food Facts | ODbL |
| Package Manager | uv | MIT / Apache |

---

> **The core insight:** We are not inventing new AI. We are connecting existing, proven tools (Nightscout + Terra + Ollama + USDA + validated formulas) into one unified platform that no one has built before. Every individual component is battle-tested. The innovation is the integration.
