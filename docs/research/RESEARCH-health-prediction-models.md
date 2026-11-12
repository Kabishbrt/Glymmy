# Health Prediction Models, Food Scanning, & Wearable IoT Tools — Research Report

> **For:** Glymmy / HealthSync AI — Harvard HSIL Hackathon 2026
> **Date:** March 24, 2026

---

## TL;DR — Yes, All the Pieces Exist

| What you need | Open-source / accessible? | Best option |
|---|---|---|
| Glucose spike prediction | ✅ Yes | LSTM/CNN on OhioT1DM dataset, **GluPredKit** framework |
| BMI / Body fat prediction | ✅ Yes | Random Forest or formula-based (U.S. Navy, Jackson-Pollock) |
| Food photo → calorie/macro | ✅ Yes | **Food-101 + EfficientNet/YOLO** or just use **multimodal LLM** (Claude/GPT-4V) |
| Wearable IoT data (all watches) | ✅ Via middleware | **Terra API** (commercial) or **Open Wearables** (open-source) |
| Data protocol/standard | ✅ Open standards | **HL7 FHIR** + **Open mHealth** schemas |

---

## 1. Glucose Prediction Models

### Open-Source Models & Frameworks

| Project | Models Used | Dataset | What It Does |
|---|---|---|---|
| **[GluPredKit](https://github.com/miriamkw/GluPredKit)** | Double LSTM, Multitask CNN, Naive Linear | OhioT1DM, OpenAPS | Full Python framework: data handling → training → evaluation. Ready to plug in. |
| **Glucose-Level-Prediction** (GitHub) | ARIMA, RNN, CNN | OhioT1DM | Compares univariate (ARIMA/RNN) and multivariate (CNN/RNN with insulin + meals) |
| **GlucoseProject** (GitHub) | LSTM, CNN | OhioT1DM | Straightforward LSTM/CNN implementation for glucose forecasting |
| **glucose-prediction** (ethanstovall) | RNN/LSTM | Dexcom Clarity + MyFitnessPal | Predicts high/low episodes using HR + glucose + food + insulin |

### Key Dataset: OhioT1DM
- 12 Type 1 diabetic patients, 8 weeks each
- 5-minute CGM readings, finger-stick BG, insulin doses, meal logs (carb estimates), fitness band data
- **Most widely used open dataset for glucose prediction research**

### Also Useful: OpenAPS Dataset
- Open-source artificial pancreas system data
- CGM + insulin + carb intake data from real patients

### Prediction Horizons
Models typically predict 15, 30, or 60 minutes ahead (some up to 48 hours).

### Input Features That Improve Accuracy
CGM readings alone give ~OK results. Adding **insulin doses + carb intake + meal timing + heart rate + activity** significantly improves predictions.

> [!TIP]
> **For the hackathon:** GluPredKit is the most "ready to use" framework. You can train a model on the OhioT1DM dataset and demo it predicting glucose spikes from meal + insulin data. No need to build from scratch.

---

## 2. BMI, Height, Body Fat Prediction Models

### BMI Prediction
BMI itself is just a formula (`weight_kg / height_m²`), so "prediction" here means either:
- **Classifying** individuals into BMI categories (underweight / normal / overweight / obese) from other features
- **Predicting** future BMI based on trends

Open-source models on GitHub use **XGBoost, Logistic Regression, Random Forest** on features like age, height, weight, sex.

### Body Fat Percentage Prediction

| Approach | How It Works | Open-Source Example |
|---|---|---|
| **Formula-based** | U.S. Navy formula, Jackson-Pollock 4-site, Durnin-Womersley skinfold | Python + Streamlit calculator implementations |
| **ML from measurements** | Random Forest / Ridge / Bayesian Ridge on waist circumference, hip, weight, etc. | Kaggle Body Fat Prediction Dataset → FastAPI backend |
| **Image-based** | Monocular depth estimation from a single photo → body measurements → body fat % | PyTorch project using OpenCV + object detection |

### Accuracy Notes
- ML models from anthropometric measurements: **R² ~73-74%**
- Key predictor: **abdominal circumference** is the strongest single feature
- Image-based: experimental, but impressive for a demo

> [!TIP]
> **For the hackathon:** Use formula-based calculation (U.S. Navy or Jackson-Pollock) for production accuracy. For the **demo wow-factor**, show the image-based body fat estimation — it's visually impressive even if less accurate.

---

## 3. Food Photo Scanning — Models & Approaches

### Two Approaches (Both Viable)

#### Approach A: Traditional CV Models (Open-Source)
| Model/Project | Architecture | What It Does |
|---|---|---|
| **Food-101 + EfficientNet** (Hugging Face) | EfficientNet-B0 + YOLO v8 | 101 food categories + object detection + portion estimation → USDA nutrition lookup |
| **ViT + Mask R-CNN** (GitHub) | Vision Transformer + Mask R-CNN | 251 food categories + precise segmentation for portion size → calorie calculation |
| **FoodNet** | Multi-task deep learning | Detects food categories + ingredients → estimates calories and macros |
| **YOLO-based projects** | YOLOv4/v5 | Object detection for food items → calorie estimation |

**Key Dataset:** Food-101 (101 food categories, 101,000 images)

#### Approach B: Multimodal LLMs (What You're Already Planning)
- Claude Vision / GPT-4V can identify food, estimate portions, and return nutritional breakdown
- **~80-90% accuracy** for common foods
- **Drops for mixed meals, stews, and ethnic cuisines** (South Asian food is a known blind spot)
- No ML pipeline needed — just an API call

> [!IMPORTANT]
> **For the hackathon:** Use Approach B (multimodal LLM) for the live demo — it works right now with zero setup. Mention Approach A models in your architecture slides to show you have a path to a dedicated, optimized model that handles South Asian cuisine better.

---

## 4. Wearable IoT Data — How to Get Data from Watches & Devices

### The Core Question: "Is there a universal protocol?"

**Short answer: No single universal protocol exists, but there are middleware APIs that solve this.**

### How It Actually Works

```
                    ┌─────────────────────┐
                    │                     │
     ┌──────┐      │   Middleware API     │      ┌──────────────┐
     │Apple │──────►│   (Terra, Vital,    │─────►│ Your App     │
     │Watch │      │    Open Wearables)   │      │ (Glymmy)│
     └──────┘      │                     │      └──────────────┘
     ┌──────┐      │  Normalizes all     │
     │Fitbit│──────►│  data into ONE     │
     └──────┘      │  standard format    │
     ┌──────┐      │                     │
     │Garmin│──────►│                     │
     └──────┘      │                     │
     ┌──────┐      │                     │
     │ Oura │──────►│                     │
     └──────┘      └─────────────────────┘
```

### Available Middleware Options

| Middleware | Type | Devices Supported | Pricing | Key Feature |
|---|---|---|---|---|
| **[Terra API](https://tryterra.co)** | Commercial | 99% of wearables (Apple, Garmin, Fitbit, Oura, Samsung, Dexcom, Libre) | Free tier available | Already mentioned in your plan. Real-time streaming, normalized data |
| **[Vital](https://www.tryvital.io)** | Commercial | Major wearables + lab results | Free tier | Combines wearable + lab data in one API |
| **[Open Wearables](https://openwearables.io)** | **Open-source** | Apple Health, Samsung Health Connect, Garmin, Polar, Suunto, Whoop | Free / self-hosted | **Self-host for full data control. Single API, deduplicated data** |

### Native/Direct APIs (If You Don't Want Middleware)

| Platform | How to Access | Limitations |
|---|---|---|
| **Apple HealthKit** | iOS SDK only, on-device only | No cloud/server API. Data stays on phone. App must run on iOS device |
| **Google Health Connect** (replaced Google Fit) | Android SDK, open-source | Local storage only on Android. Replaced Google Fit SDK |
| **Fitbit Web API** | REST API, OAuth 2.0 | Requires Fitbit developer account. Rate limited |
| **Garmin Connect API** | REST API | Requires developer partnership |
| **Dexcom API** | REST API, sandbox available | "Limited Access" = only 5 production users. Full access needs Data Licensing Agreement |
| **Abbott Libre (LibreView)** | OAuth only via LibreView | No direct NFC scanning from 3rd-party apps |

> [!WARNING]
> **Direct APIs are fragmented** — each vendor has different auth flows, data schemas, sync models, and rate limits. Teams estimate 2-3 weeks per integration but actually ship 3-6 months later. **Use middleware unless you have a strong reason not to.**

### Open-Source Hardware
- **Bangle.js2**: Fully open-source smartwatch. Gives access to raw sensor data (accelerometer, HR, GPS). Good for research, not consumer-facing.

---

## 5. Health Data Protocols & Standards

### The Protocol Stack for Health Data

| Standard | What It Does | Open-Source? |
|---|---|---|
| **HL7 FHIR** | Universal healthcare data exchange format. Maps wearable data into "FHIR Observations" that EHRs understand | ✅ Yes |
| **Open mHealth** | Standardized schemas for mobile health data. Bridges wearable → clinical data. IEEE-backed | ✅ Yes |
| **LOINC** | Universal codes for lab tests and clinical measurements | ✅ Yes |
| **SNOMED-CT** | Clinical terminology for symptoms, diagnoses, procedures | Licensed (free in some countries) |
| **IEEE 11073** | Medical device communication standard (for connecting devices to health systems) | Standard (not open-source per se) |

### How They Fit Together

```
Wearable Data (proprietary JSON) 
    → Open mHealth Schema (standardized JSON)
        → FHIR Observation (clinical-grade format)
            → EHR System (Epic, Cerner, etc.)
```

> [!TIP]
> **For the hackathon:** Mention FHIR + Open mHealth in your architecture slides. Say "We normalize all wearable data into FHIR Observations using Open mHealth schemas — this means any hospital EHR can consume our data without custom integration." That's a powerful technical credibility signal to judges.

---

## 6. Recommended Tech Stack for Glymmy

### For the Demo (Hackathon Day)
| Feature | Tool | Why |
|---|---|---|
| Food scanning | Claude Vision / GPT-4V API | Works now, no training needed |
| Glucose prediction | Pre-trained model on OhioT1DM (via GluPredKit) | Can show real predictions |
| Lab report interpreter | Claude / GPT-4V with prompt | Already in your plan |
| BMI/body fat | Simple formula calculation | Trivial to implement |
| Wearable data | Dexcom sandbox API + simulated data | Free, no partnership needed |

### For Production (Post-Hackathon)
| Feature | Tool | Why |
|---|---|---|
| Food scanning | Fine-tuned EfficientNet on Food-101 + South Asian food dataset | Better accuracy for target market |
| Glucose prediction | LSTM trained on user's personal CGM data | Personalized predictions |
| Wearable integration | Terra API or Open Wearables | One integration = all devices |
| Data standard | FHIR + Open mHealth | EHR compatibility |
| Lab parsing | OCR (Tesseract) + LLM interpretation | Handles PDF/image reports |

---

## 7. Key Takeaways for the Pitch

1. **"We don't need to build ML from scratch"** — Open-source models (GluPredKit, Food-101, etc.) and open datasets (OhioT1DM) exist. We fine-tune and integrate, not reinvent.

2. **"The wearable integration problem is solved"** — Middleware APIs like Terra and Open Wearables have already negotiated partnerships with device manufacturers. One API call = data from every major wearable.

3. **"We use open health data standards"** — FHIR + Open mHealth means any hospital can consume our data. This isn't a proprietary silo — it's an interoperability platform.

4. **"Personalized predictions beat generic ones"** — Existing food scanners use population-average glycemic index. We train on YOUR CGM data to predict YOUR response. The model gets better with each meal you log.

5. **"2026 timing is right"** — FDA loosened digital health regulation (Jan 2026), FHIR became mandatory, middleware APIs matured. The infrastructure pieces that were missing are now in place.
