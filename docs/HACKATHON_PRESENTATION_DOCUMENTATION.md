# Glymmy: Unified AI Glycemic Companion & Smartwatch SF-LG Interface
**Harvard Health Systems Innovation Lab (HSIL) Hackathon 2026**  
**Team:** Glymmy  
**Live Prototype:** [http://localhost:3001](http://localhost:3001) (Smartwatch Simulation) & [http://localhost:3000](http://localhost:3000) (Web Platform)

---

## 1. Executive Summary & Pitch Hook

> *"A diabetic patient eats lunch and has no idea what is about to happen to their blood sugar. An athlete trains without knowing how yesterday’s meal impacts today's endurance. Today, glucose data lives in one app, food tracking in another, smartwatch vitals in a third, and lab results in an unread PDF. Glymmy connects what you eat, how you move, and what your body does — predicting what’s coming next on the devices you already wear."*

**Glymmy** is a unified glycemic intelligence platform that aggregates continuous glucose monitoring (CGM), smartwatch biometrics (heart rate, sleep, steps, skin temperature), computer vision food scanning, and clinical lab reports into an offline-first AI pipeline (powered by local Gemma 4).

Our **Smartwatch Companion** introduces a novel **Space-Filling Line Graph (SF-LG) Greedy Space Allocation Algorithm** designed specifically for circular watch faces ($300 \times 300\text{px}$). It dynamically identifies empty geometric "valleys" above and below the continuous glucose curve to display actionable intelligence (such as post-meal walk blunting, Rule-of-15 hypoglycemia rescue, and active insulin on board) **without occluding the clinical time-series**.

---

## 2. The Problem: Data Everywhere, Insights Nowhere

For the 537 million people living with diabetes worldwide:

| Fragmented Source | Where It Lives | The Clinical Bottleneck |
| :--- | :--- | :--- |
| **Blood Glucose (CGM)** | Dexcom / Libre proprietary apps | Siloed from food intake, heart rate, and medication logs |
| **Wearable Vitals** | Apple Watch / Garmin / Fitbit | Disconnected from glycemic impact; treated as generic fitness |
| **Nutrition & Meals** | Manual diary / MyFitnessPal | High friction, zero predictive correlation with glucose spikes |
| **Diagnostic Labs** | Hospital paper reports / PDFs | Patients cannot interpret HbA1c, lipid profiles, or eGFR |
| **Smartwatch UI** | Standard watch complications | Crowded circular screens clip data or hide critical alerts behind submenus |

---

## 3. The Glymmy Solution

```
┌─────────────────────────────────────────────────────────────────┐
│                    MULTIMODAL INPUT LAYER                       │
│  Continuous Glucose (CGM) │ Smartwatch Vitals │ Food Camera Scan│
└───────────────────────────────┬─────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI & PREDICTIVE ENGINE                       │
│ • Gemma 4 Multimodal LLM     • Food-to-Spike Gradient Boosting  │
│ • FHIR Data Normalization    • Dubosson Physiological Mapping   │
└───────────────────────────────┬─────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   INTERACTIVE OUTPUT CLIENTS                    │
│ • Next.js Web Dashboard       • FHIR Doctor QR Code Share       │
│ • 300x300 SF-LG Smartwatch UI with Greedy Valleys Allocation    │
└─────────────────────────────────────────────────────────────────┘
```

### Core Capabilities
1. **Multimodal Glucose Prediction:** When a user photographs a meal, the vision model extracts macronutrients and predicts glycemic spike magnitude and time-to-peak ($30\text{–}60\text{ min}$ ahead).
2. **Actionable Walk Advisor:** Calculates predicted post-meal spikes and quantifies spike reduction from light activity (e.g., *"A 15-minute walk reduces your spike by $25\text{ mg/dL}$"*).
3. **Nocturnal Hypo Guardian:** Correlates sleep stages with nocturnal dips below $70\text{ mg/dL}$, triggering escalating haptic vibrations on the smartwatch.
4. **Clinical QR Code Share:** Packages longitudinal glucose, labs, and vitals into a standardized FHIR bundle shareable with doctors in 10 seconds.

---

## 4. The Smartwatch Innovation: SF-LG Greedy Space Allocation

### The Circular Screen Challenge
Smartwatches feature small circular viewports ($300 \times 300\text{px}$). Traditional UI overlays either obscure the line graph, force tiny illegible complications, or push vital alerts off-screen.

### The SF-LG Algorithm
1. **Coordinate Projection:** Maps continuous glucose time-series ($40\text{–}240\text{ mg/dL}$) into circular SVG coordinates bounded within safe margins ($y: 58\text{px}\text{ to }242\text{px}$).
2. **Segment Scanning:** Iterates through all X-axis slices ($[x_i, x_j]$ with $\text{width} \ge 38\text{px}$) and computes the minimum and maximum physical Y values of the curve.
3. **Candidate Evaluation:**
   - **Valley Above:** Evaluates headroom between curve $Y_{\min}$ and the top safe bound ($H_{\text{above}} = Y_{\min} - Y_{\text{top}}$).
   - **Valley Below:** Evaluates footroom between curve $Y_{\max}$ and the bottom safe bound ($H_{\text{below}} = Y_{\text{bottom}} - Y_{\max}$).
4. **Greedy Selection:** Sorts candidate rectangles by area ($\text{width} \times \text{height}$) and greedily selects the largest non-overlapping spaces to host contextual widgets.

```
       ┌──────────────── 300x300 Circular Bezel ───────────────┐
       │                 [TIR 84%]  10:09  [IOB 1.4U]          │
       │                                                       │
       │     ┌───────────────────────────────────────────┐     │
       │     │ SF-LG VALLEY ABOVE: Lunch Spike Prediction│     │
       │     │ "Predicted Peak: 192 mg/dL"               │     │
       │     │ [ Simulate 15-min Walk (-25 mg/dL) ]      │     │
       │     └───────────────────────────────────────────┘     │
       │                /\                                     │
       │       CGM Line/  \     /\  (Active Glucose Curve)     │
       │              /    \___/  \                            │
       │  ───────────────────────────────────────────────────  │
       │  Target Range Band (70 - 180 mg/dL)                   │
       └───────────────────────────────────────────────────────┘
```

---

## 5. Hackathon Live Demo Script (3 Minutes)

| Time | Slide / Screen | Demo Action | Speaker Narration |
| :---: | :--- | :--- | :--- |
| **0:00 - 0:30** | Title & Hook | Show Ramesh persona | *"Meet Ramesh. He is a 45-year-old managing Type 2 diabetes. His data lives in 4 disconnected apps. Glymmy connects them into one."* |
| **0:30 - 1:15** | Food Scan & Prediction | Photograph meal on Web App | *"Ramesh photographs his lunch. Glymmy extracts 52g carbs and predicts a peak of 192 mg/dL in 45 minutes."* |
| **1:15 - 2:05** | **Smartwatch SF-LG Simulation** | **Open [http://localhost:3001](http://localhost:3001)** | *"Look at Ramesh's smartwatch. Rather than occluding his glucose graph, our SF-LG algorithm finds the empty visual valley above the curve. It displays his lunch spike prediction and gives him an immediate action: 'Simulate 15-min walk'. When we click it, you see the glucose curve dynamically flatten down to 138 mg/dL in real time."* |
| **2:05 - 2:35** | Hypo Protocol & Vitals | Switch to S1 (Point Vitals) & S2 (Rule of 15) | *"When Ramesh taps any point, he sees correlated heart rate and active insulin. In a rapid drop, the watch surfaces the clinical 'Rule of 15' rescue guidance without leaving the screen."* |
| **2:35 - 3:00** | Doctor QR Share & Close | Display FHIR QR bundle | *"At his 15-minute doctor visit tomorrow, Ramesh presents one QR code. No paper, no siloed logins. One unified companion."* |

---

## 6. Technical Architecture & Tech Stack

- **Smartwatch Simulation:** React 19, TypeScript, Vite, Tailwind CSS, Lucide Icons, SVG Space-Filling Allocation Engine.
- **Frontend Web Platform:** Next.js 16 (App Router), React 19, Recharts, Tailwind CSS v4, Clerk Auth.
- **Backend API:** FastAPI (Python 3.12+), Pydantic v2 schemas, Dubosson CGM & physiological wearable models, synthetic health generators.
- **AI & RAG Engine:** Gemma 4 (via local Ollama), ChromaDB vector store, FHIR R4 schema mapper.
- **Hardware Integration Protocols:** BLE GATT (Bluetooth Low Energy), Apple HealthKit bridge, Nightscout/xDrip+ API compatibility.

---

## 7. Clinical Impact & Judging Criteria Alignment

1. **Patient Safety:** Immediate, non-alarm-fatiguing visual prompts for the clinical "Rule of 15" prevent severe hypoglycemia events ($< 54\text{ mg/dL}$).
2. **Behavioral Modification:** Real-time spike blunting feedback motivates post-prandial walking, significantly improving Time-in-Range (TIR).
3. **No New Hardware Friction:** Operates over standard commercial smartwatches (Apple Watch, Wear OS, Garmin) and CGMs (Dexcom, FreeStyle Libre).
4. **Data Privacy:** Local-first architecture (Ollama + local model weights) guarantees zero sensitive health data leaves the patient's device without consent.

