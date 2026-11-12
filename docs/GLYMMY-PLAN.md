# Glymmy — AI-Powered Unified Health Data Platform

> **Hackathon:** Harvard Health Systems Innovation Lab (HSIL) 7th Hackathon
> **Dates:** April 10-11, 2026
> **Theme:** "Building High-Value Health Systems: Leveraging Artificial Intelligence"
> **Approach:** Full ideation (pitch deck + mockups + live AI demo, no app code)
> **Team Composition:** Mixed / non-technical backgrounds

---

## Table of Contents
1. [One-Liner & Elevator Pitch](#1-one-liner--elevator-pitch)
2. [Problem Statement](#2-problem-statement)
3. [Hackathon Challenge Mapping](#3-hackathon-challenge-mapping)
4. [System Architecture](#4-system-architecture)
5. [AI Features Deep Dive](#5-ai-features-deep-dive)
6. [Pitch Script (3 Minutes)](#6-pitch-script-3-minutes)
7. [Business Case](#7-business-case)
8. [Judging Strategy & Q&A Prep](#8-judging-strategy--qa-prep)
9. [Live AI Demo Guide](#9-live-ai-demo-guide)
10. [Preparation Timeline & Checklist](#10-preparation-timeline--checklist)

---

## 1. One-Liner & Elevator Pitch

**Name:** Glymmy

**Product Description:** Glymmy is an AI-powered health companion that unifies data from CGMs, wearables, lab reports, and food photos into a single intelligent platform — predicting glucose spikes before they happen, interpreting blood work in plain language, and giving personalized, actionable health insights so chronic disease patients can stop juggling disconnected apps and start making informed decisions with their doctors.

**One-liner:** One platform that connects all your health devices, lab reports, and food intake — then uses AI to predict risks, explain results, and share data with your doctor instantly.

**Elevator pitch (30 seconds):**
"Today, a diabetic patient juggles 5 disconnected apps — one for glucose, one for heart rate, one for food, separate lab portals, and WhatsApp to share reports with doctors. Glymmy unifies all of this into a single AI-powered platform. It scans your food and predicts glucose spikes. It reads your blood reports and explains what SGOT and SGPT mean in plain language. It detects dangerous blood sugar drops while you sleep. And when it's time to see a doctor, one QR code shares your entire health history. One platform. All your health data. AI that actually helps you act."

---

## 2. Problem Statement

### The Core Problem: Health Data Fragmentation

A chronic disease patient today — especially a diabetic — lives across multiple disconnected systems:

| What they track | Where it lives | The problem |
|----------------|---------------|-------------|
| Blood glucose (CGM) | Dexcom/Libre app | No connection to food or activity data |
| Heart rate, SpO2, sleep | Apple Watch / Fitbit / Ring app | Siloed from medical records |
| Food intake | MyFitnessPal / manual notes | No link to glucose impact |
| Lab results (blood work) | Hospital portal / paper reports | Patient can't interpret abnormal values |
| Doctor communication | WhatsApp / email / phone | No structured data sharing |
| Insulin intake | Separate insulin tracker app | Not correlated with meals or glucose |

**Consequences of fragmentation:**
- Patients can't connect the dots: "What did I eat that caused yesterday's spike?"
- Doctors get incomplete pictures during 15-minute consultations
- Abnormal lab markers (SGOT/SGPT elevated) go unexplained — patients don't know what to do
- Nocturnal hypoglycemia events are detected but not contextualized ("you skipped your bedtime snack")
- Preventive interventions are missed because no system sees the full picture

**Scale of the problem:**
- 537 million adults living with diabetes worldwide (IDF Diabetes Atlas, 2021)
- Projected to reach 783 million by 2045
- Cardiovascular disease is the #1 killer globally — monitoring requires multi-device data integration
- The average chronic disease patient uses 3-5 health apps that don't talk to each other

### Target User Persona

**Primary:** Ramesh, 45, Type 2 diabetic in Kathmandu
- Uses a CGM (Libre) and a smartwatch
- Gets blood work done every 3 months
- Wants to understand what foods spike his sugar
- Shares reports with his doctor via WhatsApp photos
- Doesn't understand what "SGOT: 65 U/L" means
- Worries about low blood sugar at night

**Secondary:** Any chronic disease patient managing multiple health data streams, caregivers, and doctors who need consolidated patient data.

---

## 3. Hackathon Challenge Mapping

Your idea directly addresses **7 of the 11 hackathon challenges** (excluding #1 EHR Analysis, #5 Too Much Information, #6 Shortage of Healthcare Workers, and #11 AI in Pediatrics):

### Challenge #2: Diagnosis & Monitoring Improvements
> *"What AI-driven diagnostic or monitoring tools can be developed to detect patient changes earlier, allowing for timely treatment adjustments to prevent negative outcomes?"*

**How Glymmy addresses this:**
- Real-time CGM + wearable data aggregation for continuous monitoring
- AI-powered glucose spike prediction based on food intake + activity patterns
- Hypoglycemia detection during sleep with contextual alerts
- Trend analysis across weeks/months to detect deterioration early

### Challenge #3: Intelligent Support Chatbots
> *"Which AI and Large Language Models can be used to develop a chatbot that assists patients and medical staff?"*

**How Glymmy addresses this:**
- AI chatbot that answers questions about the user's own health data
- "Why did my sugar spike yesterday?" → data-aware, personalized response
- Explains medical terms and lab results in plain language
- Can guide patients to appropriate next steps (schedule appointment, recheck labs)

### Challenge #4: Fragmentation of Care
> *"What systems or models could be implemented to overcome these issues?"*

**How Glymmy addresses this:**
- Single platform unifying CGM, wearables, food tracking, lab reports, and insulin logs
- Cloud-based storage so data persists across device changes
- Standardized data format that any doctor can access

### Challenge #7: Fragmented Care Pathways
> *"How can healthcare systems use AI to address fragmented care pathways by enhancing coordination, communication, and continuity?"*

**How Glymmy addresses this:**
- QR code sharing gives any doctor instant access to full health history
- Doctor consultation portal shows unified patient timeline
- Historical blood report inventory with trend analysis
- Seamless transition between providers — data follows the patient

### Challenge #8: Health Literacy
> *"How can we leverage AI to improve overall health literacy?"*

**How Glymmy addresses this:**
- AI interprets lab reports in plain language: "Your liver enzyme SGOT is high. Here's what that means and what to do."
- Food scanning educates: "This meal has 80g of carbs — expect a glucose rise of ~40 mg/dL"
- Chatbot answers health questions in context of the patient's own data

### Challenge #9: Preventive Health Engagement
> *"How can AI be used to create personalized preventive health programs that analyze individual health data?"*

**How Glymmy addresses this:**
- Food scanning + calorie/macro tracking for dietary management
- BMI computation from height/weight with trend tracking
- AI call reminders when lab rechecks are due
- Proactive alerts: "Your fasting glucose has been trending up 5% this month — consider scheduling a check-up"

### Challenge #10: Breaking Communication Barriers
> *"What are additional ways AI could enhance communication between patients and their care teams?"*

**How Glymmy addresses this:**
- QR-based instant health data sharing (no more WhatsApp photos of reports)
- AI-generated health summaries that doctors can quickly scan
- Automated AI calls for reminders in the patient's preferred language
- Chatbot as 24/7 first point of contact for health questions

---

## 4. System Architecture

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    HIPAA & SOC COMPLIANCE LAYER                  │
│              (End-to-end encryption, consent management)         │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              LAYER 1: DATA SOURCES (INPUT)                │   │
│  │                                                           │   │
│  │  ┌─────────┐ ┌───────────┐ ┌──────────┐ ┌────────────┐  │   │
│  │  │   CGM   │ │Smart Watch│ │  Food    │ │  Manual    │  │   │
│  │  │ (Libre, │ │ / Ring    │ │ Scanner  │ │  Input     │  │   │
│  │  │ Dexcom) │ │(Apple,    │ │ (Phone   │ │(Height,   │  │   │
│  │  │         │ │ Fitbit)   │ │  Camera) │ │ Weight)   │  │   │
│  │  └────┬────┘ └─────┬─────┘ └────┬─────┘ └─────┬──────┘  │   │
│  │       │             │            │              │          │   │
│  │  ┌────┴────┐ ┌──────┴──────┐ ┌──┴───┐ ┌───────┴───────┐ │   │
│  │  │Blood    │ │BP, HR, SpO2,│ │Food  │ │Lab Reports,   │ │   │
│  │  │Sugar    │ │Sleep Data   │ │Photo │ │Insulin Logs   │ │   │
│  │  └────┬────┘ └──────┬──────┘ └──┬───┘ └───────┬───────┘ │   │
│  └───────┼─────────────┼───────────┼─────────────┼──────────┘   │
│          │             │           │             │               │
│          ▼             ▼           ▼             ▼               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │            LAYER 2: AI PROCESSING ENGINE                  │   │
│  │                                                           │   │
│  │  ┌─────────────────┐  ┌──────────────────────────────┐   │   │
│  │  │ Food Photo AI   │  │ Glucose Spike Prediction      │   │   │
│  │  │ Photo → Calories│  │ CGM + Food → Predict spike    │   │   │
│  │  │ Protein, Fat,   │  │ + suggest intervention        │   │   │
│  │  │ Carbs, Portions │  │                               │   │   │
│  │  └─────────────────┘  └──────────────────────────────┘   │   │
│  │                                                           │   │
│  │  ┌─────────────────┐  ┌──────────────────────────────┐   │   │
│  │  │ Lab Interpreter │  │ Hypoglycemia Detection        │   │   │
│  │  │ SGOT/SGPT flag  │  │ Sleep + CGM → Alert if        │   │   │
│  │  │ → Plain English │  │ blood sugar drops < 70 mg/dL  │   │   │
│  │  │ + Recheck remind│  │ + contextual "why"            │   │   │
│  │  └─────────────────┘  └──────────────────────────────┘   │   │
│  │                                                           │   │
│  │  ┌─────────────────┐  ┌──────────────────────────────┐   │   │
│  │  │ BMI Calculator  │  │ Health Chatbot                │   │   │
│  │  │ Height + Weight │  │ "Why did my sugar spike?"     │   │   │
│  │  │ → BMI + Fat %   │  │ Data-aware AI responses       │   │   │
│  │  │ + Trend tracking│  │                               │   │   │
│  │  └─────────────────┘  └──────────────────────────────┘   │   │
│  │                                                           │   │
│  │  ┌──────────────────────────────────────────────────────┐│   │
│  │  │ AI Calls & Reminders                                 ││   │
│  │  │ Abnormal labs → auto-call patient for recheck        ││   │
│  │  │ Medication reminders, appointment scheduling         ││   │
│  │  └──────────────────────────────────────────────────────┘│   │
│  └──────────────────────────────────────────────────────────┘   │
│          │                                                       │
│          ▼                                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │            LAYER 3: SHARING & COMMUNICATION               │   │
│  │                                                           │   │
│  │  ┌─────────────┐ ┌──────────────┐ ┌───────────────────┐ │   │
│  │  │QR Code Share│ │Doctor Portal │ │Blood Report       │ │   │
│  │  │Scan to view │ │View patient  │ │Historical         │ │   │
│  │  │full health  │ │unified data  │ │Inventory &        │ │   │
│  │  │history      │ │(with consent)│ │Trend Analysis     │ │   │
│  │  └─────────────┘ └──────────────┘ └───────────────────┘ │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │            LAYER 4: PLATFORM                              │   │
│  │  Cross-platform: iOS, Android, Web                        │   │
│  │  Cloud: AWS/GCP for storage, compute, AI inference        │   │
│  │  APIs: Dexcom, Apple HealthKit, Google Fit, Lab portals   │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Ingest:** CGM sends blood sugar readings every 5 min. Smartwatch syncs vitals hourly. User snaps food photos at meals. Lab reports uploaded/pulled from portals.
2. **Process:** AI engine correlates data across sources. Runs prediction models. Flags anomalies.
3. **Act:** Sends alerts (spike prediction, hypoglycemia, lab recheck). Chatbot answers queries. Generates health summaries.
4. **Share:** Patient generates QR code → Doctor scans → Sees unified dashboard with full history.

---

## 5. AI Features Deep Dive

### Feature 1: Food Photo Scanning + Spike Prediction

**User Story:**
Ramesh takes a photo of his lunch — a plate of rice with chicken curry and dal.

**What the AI does:**
1. Analyzes the food photo using multimodal AI (e.g., Claude Vision / GPT-4V)
2. Identifies items: "Rice (1.5 cups), Chicken Curry (1 serving), Dal (1 bowl)"
3. Returns nutritional breakdown:
   - Calories: ~650 kcal
   - Carbs: 80g | Protein: 35g | Fat: 20g | Fiber: 5g
4. Cross-references with Ramesh's CGM data and historical patterns
5. Predicts: "Based on your history, this meal is likely to cause a glucose spike of ~40 mg/dL peaking in 90 minutes"
6. Suggests: "Consider a 15-minute walk after eating to reduce the spike by ~25%"

**Why it's novel:**
- MyFitnessPal requires manual food logging (tedious, inaccurate)
- No existing app connects food photo → nutritional analysis → glucose spike prediction in one flow
- The prediction is personalized based on the individual's CGM history, not generic glycemic index data

**Technical approach:**
- Multimodal LLM (Claude/GPT-4V) for food identification and portion estimation
- Historical CGM data + meal logs to build personalized glucose response model
- Simple heuristic initially: carb load × personal carb sensitivity factor → predicted spike

---

### Feature 2: Lab Report AI Interpreter

**User Story:**
Ramesh uploads his quarterly blood report. It shows SGOT: 65 U/L (normal: 8-45) and SGPT: 72 U/L (normal: 7-56).

**What the AI does:**
1. Parses the blood report (PDF/image) using OCR + AI
2. Identifies abnormal markers and flags them visually (red indicators)
3. Generates plain-language explanation:
   > "Your liver enzymes (SGOT and SGPT) are elevated above normal range. This could indicate:
   > - Fatty liver disease (most common cause)
   > - Medication side effects (check if any new medications)
   > - Alcohol consumption
   > - Viral hepatitis (less likely if vaccinated)
   >
   > **Recommended actions:**
   > 1. Reduce alcohol intake for 4 weeks
   > 2. Schedule a recheck blood test in 4-6 weeks
   > 3. Consult your doctor if values remain elevated
   >
   > *Note: This is informational, not a diagnosis. Please consult your healthcare provider.*"
4. Sets automatic reminder for recheck in 4 weeks
5. Stores the report in historical inventory for trend tracking

**Why it matters:**
- Most patients see "SGOT: 65" and have no idea what it means
- Doctors often don't have time to explain every marker in detail
- This bridges the health literacy gap — patient arrives at the doctor's office informed
- Historical tracking shows trends: "Your SGOT has been rising over the last 3 reports"

---

### Feature 3: Hypoglycemia Detection During Sleep

**User Story:**
Ramesh takes insulin at 10 PM and goes to sleep, forgetting his bedtime snack. At 2 AM, his CGM detects blood sugar dropping to 62 mg/dL and still falling.

**What the AI does:**
1. Monitors CGM readings during sleep hours (configurable)
2. Detects blood sugar below threshold (default: 70 mg/dL) with downward trend
3. Triggers escalating alerts:
   - **Level 1 (< 70 mg/dL):** Vibration alert on smartwatch + phone notification
   - **Level 2 (< 55 mg/dL):** Loud alarm + emergency contact notification
   - **Level 3 (< 40 mg/dL):** Emergency services alert
4. Provides contextual explanation:
   > "Your blood sugar is 62 mg/dL and dropping. Possible cause: You had 8 units of insulin at 10:12 PM but no bedtime snack recorded. Please consume 15g of fast-acting carbs (juice, glucose tablets)."
5. Logs the event for doctor review

**Why it's critical:**
- Nocturnal hypoglycemia is a leading cause of diabetes-related emergencies
- Existing CGMs alert on low sugar but don't explain WHY it happened
- Contextual AI connects insulin timing + missed meals to the event
- Emergency contact notification can save lives for patients living alone

---

### Feature 4: AI Health Chatbot

**User Story:**
Ramesh opens the app and asks: "Why did my sugar spike so much yesterday afternoon?"

**What the AI does:**
1. Retrieves Ramesh's data from yesterday: CGM readings, food log, activity, medications
2. Analyzes and responds:
   > "Your glucose peaked at 220 mg/dL at 2:35 PM yesterday. Here's what I found:
   >
   > **Likely cause:** You had naan bread + biryani rice at 1:15 PM (estimated 95g carbs — that's high). You also didn't walk after lunch.
   >
   > **Comparison:** On 3 similar days this month when you had a high-carb lunch BUT walked for 15 minutes afterward, your average spike was only 165 mg/dL — that's 25% lower.
   >
   > **Suggestion:** Try a post-lunch walk or swap one carb source (skip the naan OR the rice, not both). Your body responds well to light activity after meals."

**Capabilities:**
- Answers questions about personal health trends using actual data
- Explains medical concepts in simple terms
- Suggests actionable changes based on what's worked before for this patient
- Available 24/7 — no appointment needed for basic health questions
- Knows when to say "please consult your doctor" (anything beyond informational guidance)

---

### Feature 5: AI Call Reminders

**User Story:**
Ramesh's SGOT/SGPT were flagged high 3 months ago. He forgot to get a recheck.

**What the AI does:**
1. Tracks reminder schedule from lab interpreter (recheck in 4-6 weeks)
2. Sends progressive reminders:
   - **Week 4:** Push notification: "Your liver enzyme recheck is due this week"
   - **Week 5:** Second notification with option to schedule
   - **Week 6:** AI-powered phone call:
     > "Hi Ramesh, this is Glymmy. Your liver enzymes SGOT and SGPT were elevated 3 months ago, and a recheck was recommended. Would you like me to help you find a nearby lab? Press 1 for yes, 2 to snooze for one week."
3. Can also remind for:
   - Medication timing (insulin, daily pills)
   - Upcoming doctor appointments
   - Vaccination schedules
   - Routine screening due dates (annual eye exam, foot exam for diabetics)

**Why it matters:**
- Follow-up compliance is a huge problem — patients forget rechecks
- An AI call feels more personal than a push notification
- Multi-language support reaches patients who aren't app-savvy
- Reduces burden on clinic staff for follow-up calls

---

## 6. Pitch Script (3 Minutes)

### Slide 1 — Introduction (10 seconds)
> "Hi, we're Team [NAME]. We're building Glymmy — one platform that unifies all your health data and uses AI to turn it into action."

### Slide 2 — Problem Statement (20 seconds)
> "Meet Ramesh. He's 45, diabetic, and uses 5 different apps to track his health. His glucose data is in one app. His heart rate is in another. His food log is on paper. His blood reports sit in a hospital portal. And when he visits his doctor, he screenshots everything and sends it over WhatsApp.
>
> His data is everywhere. His insights are nowhere. And his doctor gets 15 minutes to make sense of it all."

### Slide 3 — The Solution (30 seconds)
> "Glymmy is a centralized platform that connects ALL of Ramesh's health data — CGM, smartwatch, food intake, lab reports, and insulin logs — into one place. But we don't just aggregate data. We use AI to make it actionable."
>
> [Show architecture diagram]

### Slide 4 — AI Features Walkthrough (30 seconds)
> "Five key AI features:
>
> **One** — Snap a photo of your food. AI tells you the calories, protein, and carbs — and predicts how much your glucose will spike.
>
> **Two** — Upload a blood report. AI flags abnormal values and explains what SGOT and SGPT mean in plain language.
>
> **Three** — Dangerous blood sugar drop at 2 AM? AI detects it, explains WHY it happened, and alerts your emergency contact.
>
> **Four** — Ask the chatbot 'why did my sugar spike yesterday?' — it analyzes your actual data and gives you a personalized answer.
>
> **Five** — Forgot your lab recheck? AI calls you with a reminder."

### Slide 5 — Demo (1 minute)
> "Let me show you this in action."
>
> [Live AI demo — see Section 9]
>
> - Demo 1: Food photo → AI returns nutritional breakdown + spike prediction
> - Demo 2: Blood report → AI flags SGOT/SGPT and explains in plain language

### Slide 6 — Implementation & Business Model (20 seconds)
> "537 million people live with diabetes globally. Our go-to-market:
> - **Phase 1:** Diabetes management — CGM integration + food AI + lab analysis
> - **Phase 2:** Expand to cardiovascular, general wellness
> - **Revenue:** Freemium (basic tracking free) + Premium AI features + B2B partnerships with hospitals and insurance providers
> - **Compliance:** Built with HIPAA and SOC standards from day one.
> - **Tech:** Integrates with Dexcom, Apple HealthKit, Google Fit APIs."

### Slide 7 — Closing (10 seconds)
> "Ramesh shouldn't need 5 apps to manage his health. With Glymmy, he needs one. Thank you."

---

## 7. Business Case

### Market Opportunity
- **537 million** adults with diabetes globally (IDF 2021), projected **783 million by 2045**
- **1.28 billion** adults with hypertension worldwide (WHO)
- **Global digital health market:** $330B in 2025, growing 25% CAGR
- **CGM market alone:** $12B+ by 2028

### Revenue Model
| Tier | Price | Features |
|------|-------|----------|
| **Free** | $0 | Manual data entry, basic dashboard, BMI calculator |
| **Premium** | $9.99/mo | AI food scanning, spike prediction, lab interpreter, chatbot, AI reminders |
| **Family** | $19.99/mo | Premium for up to 5 family members + caregiver dashboard |
| **B2B (Hospital)** | Custom | Bulk licenses, EHR integration, doctor portal, patient population analytics |
| **B2B (Insurance)** | Custom | Risk prediction data (anonymized), preventive engagement tools |

### Competitive Landscape
| Competitor | What they do | What they miss |
|-----------|-------------|---------------|
| **Apple Health** | Aggregates wearable data | No AI insights, no food scanning, no lab analysis, no doctor sharing |
| **MyFitnessPal** | Food logging + calorie counting | Manual entry only, no glucose correlation, no medical data |
| **Dexcom Clarity** | CGM data analysis | Only glucose — no food, no wearables, no labs |
| **One Drop** | Diabetes management | Limited AI, no food photo scanning, no lab interpretation |
| **Glymmy** | **All of the above + AI** | **Unified platform with predictive AI across all health data** |

### Implementation Roadmap
| Phase | Timeline | Focus |
|-------|----------|-------|
| **MVP** | Months 1-3 | Food scanner AI + CGM dashboard + manual data entry |
| **V1** | Months 4-6 | Lab report analyzer + chatbot + smartwatch integration |
| **V2** | Months 7-12 | QR sharing + doctor portal + AI call reminders |
| **Scale** | Year 2+ | Multi-language, EHR integration, insurance partnerships |

### Partnerships to Pursue
- **Device makers:** Dexcom, Abbott (Libre), Apple, Fitbit/Google, Oura
- **Healthcare systems:** Hospital chains for pilot programs
- **Insurance:** Preventive health data can reduce claims — value proposition for insurers
- **Pharmacies:** Integration for medication reminders and refills

---

## 8. Judging Strategy & Q&A Prep

### Scoring Strategy (Total: /30)

| Criterion (/5) | Strategy |
|----------------|----------|
| **1. Challenge** | Lead with the global diabetes burden (537M patients). Use the personal story of Ramesh. Show 5-app fragmentation visually. Cite WHO/Lancet data from the hackathon resources page (p.16). Make judges feel the pain. |
| **2. Technology & Innovation** | Emphasize what NO existing app does: food photo → nutritional analysis → personalized glucose spike prediction. The multimodal AI approach is novel. Connecting food, CGM, labs, and wearables with AI is the key differentiator. |
| **3. Implementation** | Show awareness of HIPAA/SOC from slide 1. Present the phased roadmap (MVP → V1 → V2 → Scale). Name specific APIs (Dexcom, Apple HealthKit). Show a sustainable business model (freemium + B2B). |
| **4. Team** | Each team member introduces themselves with their unique perspective. Highlight diversity of backgrounds as a strength — this solution needs clinical, technical, design, and business thinking. |
| **5. Pitch** | Practice until it's under 3 minutes. Use the story of Ramesh throughout (narrative thread). Clean visuals — architecture diagram + mockup screens. Live AI demo is the showstopper. |
| **6. Q&A** | See prepared answers below. Stay calm, acknowledge good questions, give structured answers. |

### Anticipated Judge Questions & Answers

**Q: "How is this different from Apple Health?"**
> A: "Apple Health aggregates data but doesn't think. It shows you numbers. Glymmy uses AI to connect those numbers — telling you that your 220 spike happened because of the naan + rice combo, and that walking for 15 minutes would have cut it by 25%. That predictive, personalized AI layer is what Apple Health doesn't do."

**Q: "What about data privacy? This is sensitive health data."**
> A: "Privacy is foundational, not an afterthought. We're designing with HIPAA compliance from day one — end-to-end encryption, explicit consent for every data share, audit trails, and data residency controls. The QR code sharing is consent-based — the patient generates it, and it expires after a set period. We never sell individual data."

**Q: "How accurate is the food photo analysis?"**
> A: "Current multimodal AI models can identify common foods with 80-90% accuracy. For our use case, we don't need clinical-grade precision — a ±15% calorie estimate is still vastly more useful than the alternative, which is that most patients don't log food at all because it's too tedious. We also allow users to correct AI estimates, which improves the model over time."

**Q: "Don't CGM apps already alert for low blood sugar?"**
> A: "They alert, but they don't explain. When Ramesh's Libre buzzes at 2 AM, it says 'Low glucose.' Glymmy says 'Low glucose. Likely cause: you took insulin at 10 PM but didn't eat your bedtime snack. Please consume 15g of fast-acting carbs.' That context is the difference between panic and informed action."

**Q: "How will you get device manufacturers to integrate?"**
> A: "Major platforms already offer APIs — Dexcom, Apple HealthKit, Google Fit, and Fitbit all have developer programs. We don't need proprietary partnerships for the MVP. For deeper integrations (like direct CGM data streaming), we'd pursue partnerships once we have user traction."

**Q: "What about regulatory approval?"**
> A: "Glymmy is a wellness and informational tool, not a diagnostic device. We clearly state that AI insights are not medical diagnoses. This puts us in the wellness app category initially, similar to how MyFitnessPal or Noom operate. If we move toward clinical decision support, we'd pursue FDA/CE regulatory pathways."

**Q: "Why would a doctor use this?"**
> A: "Doctors spend precious consultation time asking patients to recall data. With Glymmy, a patient walks in, the doctor scans a QR code, and instantly sees a consolidated dashboard: glucose trends, vitals, food patterns, lab history, medication adherence. That saves time and improves diagnostic accuracy."

**Q: "This seems too ambitious. Can you actually build all of this?"**
> A: "We're not building all of it at once. Our MVP is focused: food scanner AI + CGM dashboard + basic lab analysis. That alone is a differentiated product. The full vision unfolds over 12-18 months. The modular architecture means each feature is independent — we can ship incrementally."

---

## 9. Live AI Demo Guide

Even without building an app, you can do a powerful live demo during the pitch using existing AI tools. This requires zero coding.

### Setup (Before the pitch)
1. Open Claude.ai (or ChatGPT) on your laptop
2. Have a food photo ready on your phone (e.g., a plate of rice + curry)
3. Have a sample blood report image/PDF ready (with some abnormal values)
4. Have the browser tab ready to go — no login screens during demo

### Demo 1: Food Photo Analysis (30 seconds)

**Steps:**
1. Show the food photo to the audience
2. Paste/upload it into Claude with this prompt:

> "You are Glymmy, an AI health assistant. Analyze this food photo. Provide:
> 1. Identified food items with estimated portions
> 2. Nutritional breakdown (calories, carbs, protein, fat, fiber)
> 3. Glucose spike prediction for a Type 2 diabetic patient whose average post-meal spike is 35 mg/dL per 50g of carbs
> 4. One actionable suggestion to reduce the spike
> Format the response in a clean, app-like way."

**Expected output:** The AI will identify the food, give a nutritional breakdown, predict the spike, and suggest a post-meal walk or portion adjustment.

**What to say:** "This is what Ramesh sees when he takes a photo of his lunch. In 3 seconds, he knows exactly what he's eating and what it'll do to his blood sugar."

### Demo 2: Lab Report Interpreter (30 seconds)

**Steps:**
1. Show the blood report to the audience
2. Paste/upload it into Claude with this prompt:

> "You are Glymmy, an AI health assistant. Analyze this blood report. For each marker:
> 1. Show the value and normal range
> 2. Flag if abnormal (use a warning indicator)
> 3. Explain what it means in simple language a non-medical person can understand
> 4. Provide recommended actions
> Add a disclaimer that this is informational, not a diagnosis."

**Expected output:** Clean breakdown of each marker, abnormal values flagged, plain-language explanations, and next steps.

**What to say:** "Ramesh used to see 'SGOT: 65' and have no idea what it meant. Now he understands his own health."

### Demo 3 (Optional): Chatbot Interaction

If time permits, type a quick question:
> "My blood sugar spiked to 220 yesterday at 2:30 PM. I had rice and naan for lunch at 1 PM and didn't walk. On days when I walk after lunch, my spike is usually around 165. Why did this happen and what should I do differently?"

The AI will give a personalized, data-aware response — demonstrating the chatbot capability.

---

## 10. Preparation Timeline & Checklist

### Timeline

| Date | Task | Owner |
|------|------|-------|
| **March 23 - April 1** | Finalize team members. Assign roles (Pitcher, Designer, Business Lead, Technical Lead). Read this document thoroughly. | All |
| **April 1 - 5** | Create pitch deck slides (Google Slides/Canva). Clean up architecture diagram in Excalidraw. Create UI mockup screens. | Designer + All |
| **April 5 - 7** | Write business case details. Research competitor apps. Gather diabetes statistics for the pitch. | Business Lead |
| **April 7 - 8** | Practice the 3-minute pitch. Time it. Record and review. Prepare for Q&A. | Pitcher + All |
| **April 9** | Final dry run. Test live AI demo (Claude/ChatGPT). Ensure laptop, charger, food photo, blood report sample are ready. | All |
| **April 10 (Day 1)** | Attend opening panel. Refine idea based on insights. Consult mentors (ask for feedback on pitch + idea gaps). Polish materials. | All |
| **April 11 (Day 2)** | Morning: final pitch practice. Attend panel session. Afternoon: PITCH! | All |

### Deliverables Checklist

- [ ] **This document** — Read by all team members
- [ ] **Pitch deck** — 5-7 slides (Google Slides, Canva, or PowerPoint)
- [ ] **Architecture diagram** — Clean version of Excalidraw diagram
- [ ] **UI mockup screens** — 4-5 screens (dashboard, food scanner, lab reports, QR share, chatbot)
- [ ] **Food photo for demo** — A clear photo of a recognizable meal
- [ ] **Sample blood report** — With at least one abnormal marker
- [ ] **AI demo tested** — Run the prompts from Section 9 and verify they work well
- [ ] **Pitch practiced** — Timed at under 3 minutes, at least 3 rehearsals
- [ ] **Q&A prepared** — Each team member reads Section 8 answers
- [ ] **Team roles assigned** — Who presents which section, who handles Q&A

### Role Assignments Template

| Role | Person | Responsibility |
|------|--------|---------------|
| **Pitch Presenter** | _________ | Delivers the 3-minute pitch. Practices the most. |
| **Demo Operator** | _________ | Runs the live AI demo on laptop during pitch. |
| **Designer** | _________ | Creates pitch deck slides, architecture diagram, UI mockups. |
| **Business Lead** | _________ | Owns market data, business model, handles business Q&A. |
| **Technical Lead** | _________ | Answers technical Q&A (architecture, APIs, compliance). |

*(Roles can overlap — 3-5 team members recommended)*

---

## Quick Reference Card

| Item | Detail |
|------|--------|
| **Project** | Glymmy |
| **Hackathon** | HSIL 7th, Harvard, April 10-11 2026 |
| **Theme** | Building High-Value Health Systems Through AI |
| **Pitch** | 3 minutes, April 11 afternoon |
| **Judging** | 6 criteria, /30 total |
| **Challenges** | #2, #3, #4, #7, #8, #9, #10 (7 of 11) |
| **Key differentiator** | Food photo → spike prediction (no one else does this) |
| **Live demo** | Food photo AI + Lab report AI (using Claude, zero code) |
| **Business model** | Freemium + B2B (hospitals, insurance) |
| **Target market** | 537M diabetics globally |

---

## 11. Competitive Landscape Research

### The Big Finding: No Single App Does What Glymmy Proposes

**Every existing product covers only 1-3 of Glymmy's 5 pillars (CGM, wearables, food photo scanning, lab analysis, doctor sharing).** None unifies all five.

### Direct Competitors by Category

#### CGM + Metabolic Health Apps

| App | What it does | Price | Key user complaints | Gap Glymmy fills |
|-----|-------------|-------|--------------------|-----------------------|
| **Levels Health** | CGM tracking, meal logging with AI photo, Apple Health sync, annual blood panel | $125-$288/yr + CGM sensors | Meal entry is "arduous," app is buggy, frequent restarts needed | No lab AI interpretation, no doctor sharing, limited wearable integration |
| **Signos** | AI-powered CGM for weight loss, predicts glucose responses | $149-$299/mo | Customer service "non-existent," sensors fail within days, meal logging is "God-awful," called "way too expensive a toy" | No lab integration, no food photo scanning, no doctor sharing |
| **Nutrisense** | CGM tracking + registered dietitian access | $199-$399/mo + $100/mo for dietitian | App "overwhelming and not organized," charges for missed appointments, cancellation is extremely difficult, 6-month minimum | No wearable aggregation, no lab reports, no photo food scanning, no doctor sharing |
| **Abbott Lingo** | OTC CGM for wellness ($49/sensor) | $49/2 weeks or $249/12 weeks | Disconnects "several times per day," graph is "tiny, cannot be zoomed," customer support unresponsive (12+ days no reply) | No food tracking at all, no lab integration, no doctor sharing |
| **Veri** | Was a CGM metabolic app | **DISCONTINUED** — acquired by Oura, shut down Sept 2024 | N/A | Shows standalone CGM apps struggle to survive — market consolidating |

#### Food Photo Scanning Apps

| App | What it does | Accuracy | Key user complaints | Gap Glymmy fills |
|-----|-------------|----------|--------------------|-----------------------|
| **Cal AI** | Photo-based calorie tracking (1M+ downloads, 4.7 stars) | Claims 90%, tested ~82% | "Way off" for mixed meals — measured meal was 2x what Cal AI estimated. Meat underestimated by ~50%. Users call it a "scam" | Pure calorie counter. No CGM, no wearables, no labs, no health sharing |
| **SnapCalorie** | Photo calorie estimation (ex-Google Lens team) | Claims 16% error rate | Accuracy drops for stews, casseroles, complex dishes. Requires frequent manual correction | Standalone tool. No integration with anything |
| **SNAQ** | Photo-based carb counting for diabetics, connects to CGM | ~13g carb estimation error (44% in real-world) | No auto-save (safety concern for diabetics), pattern tracking features "haven't functioned properly" | Diabetes-only. No wearable data, no lab reports, no doctor sharing |
| **January AI** | "Digital twin" predicts glucose from food photo — even WITHOUT CGM | Varies widely | Banana predicted "low impact" but spiked user to 141. "Strange data readings." No human support. Concerns about eating disorders | No wearable integration, no lab analysis, no doctor sharing |

#### Lab Report AI Interpreters

| App | What it does | Key issues | Gap Glymmy fills |
|-----|-------------|-----------|----------------------|
| **Docus AI** | Upload blood/urine/stool tests for AI analysis | $300-$1,200/yr. Prone to parsing errors from complex PDFs | No CGM, no wearables, no food tracking, no QR sharing |
| **Kantesti (PIYA.AI)** | Claims 98.7-99.84% accuracy, 40-45 page reports, 75+ languages, 2M+ users | Free but standalone | No integration with any other health data |
| **SiPhox Health** | At-home blood testing + AI interpretation | Accuracy "questionable" — discrepancies of 300-600% for testosterone and vitamin D vs clinical labs. Lost a customer's sample with no HIPAA assurance | Hardware-dependent (their own kits only) |

#### Health Data Sharing with Doctors

| App | What it does | Gap |
|-----|-------------|-----|
| **Patient QR** | Medical records in phone wallet as QR code | Static records only. No real-time CGM/wearable data |
| **Sync.MD** | Collect, store, share medical records. QR sharing. Free. | Document-focused. No wearable, CGM, or food data |
| **Medaara** | QR-enabled patient app for medical records | Works offline but only handles documents, not continuous data |

### Critical Industry Stats

- **Only 10% of physicians** currently integrate wearable data into their EHR systems
- **87% of CGM users** change food choices based on glucose feedback (Scripps Research, 2025)
- CMS launched a **Health Technology Ecosystem Initiative** (July 2025) specifically to address data fragmentation
- AI food scanners' accuracy **drops significantly for mixed meals, homemade foods, and ethnic cuisines** — South Asian food is a blind spot

### 7 Strategic Gaps Glymmy Exploits

1. **No single app unifies all 5 data streams** — every competitor is siloed in 1-2 categories
2. **Food photo + CGM correlation is poorly executed everywhere** — SNAQ's features "don't work," Signos's logging is "God-awful," Levels requires manual entry
3. **Lab interpretation exists in isolation** — no app connects labs to CGM trends, food patterns, or wearable data
4. **Doctor sharing is stuck in the PDF era** — no live dashboard sharing via QR exists
5. **Pricing is brutal** — Signos $149-299/mo, Nutrisense $199-399/mo, January AI $288/mo. Affordable unified platform has clear opening
6. **Customer service is universally terrible** — Signos, Lingo, Nutrisense all face severe complaints
7. **South Asian / Indian food accuracy is a blind spot** — if targeting Nepal/India, training on local cuisine is a strong differentiator

---

## 12. Past HSIL Winners & What Made Them Win

### HSIL 2024 (5th Edition) Winners
| Team | What they built | Why they won |
|------|----------------|-------------|
| **SweetAudio** | ML model analyzing voice variables (pitch, intensity) to estimate blood glucose | Combined accessible tech (voice) with genuine clinical need — no new device required |
| **Sam.io** | AI chatbot helping mental health patients adhere to medications | Personalized follow-up care addressing a real adherence gap |

### HSIL 2025 (6th Edition) — Dhaka Hub Winners
| Team | What they built | Why they won |
|------|----------------|-------------|
| **NURIX** | Brain-computer interface for mental health | Leveraged emerging neurotechnology — bold and novel |
| **SMARTENDO** | Personalized care for endometriosis patients | Pragmatic, patient-centered design for an underserved condition |

### Comparable Hackathon Winners (Out-of-Pocket Healthcare AI 2025)
| Team | What they built | Why they won |
|------|----------------|-------------|
| **Copi** | Passively ingests child health data from texts/WhatsApp/photos into digital health profile | Won "I'm Using This Tomorrow" — immediate real-world utility |
| **Cartoon Care** | AI-generated personalized storybooks for children facing medical conditions | People's Choice — clinical value + emotional resonance |
| **Clinicians Unchained** | Autonomous AI making phone calls to insurers/pharmacies for prescription denials | Won for audacity and practical workflow automation |

### Patterns From Winners

1. **Workflow-embedded**: Insert into existing habits (WhatsApp, voice, text) — don't require new behavior
2. **Crystal-clear problem**: Judges *feel* the pain before seeing the solution
3. **Working demo beats slides**: Even a rough live prototype dramatically outperforms mockups
4. **Integration over invention**: "Stitching together existing tools" — not building monolithic systems
5. **Sustainable model**: Judges rate higher when survival beyond the hackathon is credible

---

## 13. Winning Strategy for Glymmy

### Critical Pivot: Build a Simple Live Demo

Based on winner analysis, **the single highest-impact thing you can do is show a working demo, not just mockups.** Past winners consistently had something live. This doesn't mean building an app — it means:

**Option: "Stitched Demo" (zero coding, maximum impact)**
1. Use Claude.ai live on stage for food photo analysis + lab report interpretation
2. Create a Canva/Google Slides "app mockup" that looks like a real app (clickable prototype)
3. Show a pre-recorded screen recording of a CGM dashboard (use Dexcom Clarity screenshots or similar)
4. Generate a real QR code that links to a Google Sheet/Notion page showing a patient health summary

This gives you 4 "live" moments in your pitch without writing a single line of code.

### Pitch Structure (Optimized for Scoring)

**Opening (15s) — Score: Challenge /5**
> "Every 5 seconds, someone dies from diabetes complications. Ramesh, a 45-year-old diabetic in Kathmandu, uses 5 different apps to manage his health. His data is everywhere. His insights are nowhere. And his doctor gets 15 minutes to make sense of it all."

*Why this works:* Statistic + human story + problem quantified. Judges feel urgency immediately.

**Solution (30s) — Score: Technology & Innovation /5**
> Show architecture diagram. Emphasize the ONE thing nobody else does:
> "When Ramesh photographs his lunch, Glymmy doesn't just count calories — it predicts his glucose spike in 90 minutes and tells him to take a 15-minute walk. No app on the market connects food photos to personalized glucose predictions."

*Why this works:* Clear differentiator. Judges can immediately see what's novel.

**Demo (60s) — Score: Pitch /5**
> Live AI demo: food photo → nutritional analysis → spike prediction
> Live AI demo: blood report → SGOT/SGPT flagged → plain language explanation
> Show QR code → scan → patient health summary page

*Why this works:* Live demos are memorable. Judges score "prototype demonstration" explicitly.

**Implementation (20s) — Score: Implementation /5**
> "537 million diabetics globally. Freemium model: free tracking, $9.99/mo for AI features. B2B partnerships with hospitals and insurers. HIPAA-compliant from day one. MVP in 3 months: food scanner + CGM dashboard."

*Why this works:* Hits every sub-criterion — demand, business model, obstacles, stakeholders.

**Close (15s) — Score: Q&A setup**
> "Ramesh shouldn't need 5 apps to manage his health. With Glymmy, he needs one. We're [team description — diverse backgrounds]. We're ready to build this."

### Mistakes to Avoid

1. **Don't over-scope in the pitch** — Focus on food scanning + spike prediction as the hero feature. Mention other features briefly, don't deep-dive all 5
2. **Don't skip the demo** — Even if it's just Claude on a laptop, show SOMETHING live
3. **Don't get technical in the pitch** — Save architecture details for Q&A
4. **Don't mention weaknesses proactively** — Let judges ask
5. **Don't have multiple speakers** — One presenter, one demo operator
6. **Don't read from slides** — Practice until you can deliver from memory
7. **Don't go over 3 minutes** — Overrunning signals you're not serious

### Q&A Killer Answers (Updated with Competitive Intel)

**"How is this different from Levels / Signos / Nutrisense?"**
> "Those apps cost $150-400/month and only do CGM. Signos users call their meal logging 'God-awful.' Nutrisense's app is described as 'overwhelming.' None of them analyze your blood reports, none predict glucose spikes from a food photo, and none let you share your full health picture with a doctor via QR code. We unify everything they do separately — at a fraction of the cost."

**"Doesn't January AI already predict glucose from food photos?"**
> "January AI predicts using generic glycemic index data. Users report a banana was predicted 'low impact' but spiked them to 141. Our approach uses YOUR personal CGM history to make predictions — personalized, not population-average. And January AI doesn't integrate lab reports, wearable data, or doctor sharing."

**"Food photo AI isn't accurate enough."**
> "You're right that accuracy varies — Cal AI claims 90% but tests at 82%. But here's the key insight: the alternative is that patients don't log food AT ALL because it's too tedious. An 80% accurate photo scan is infinitely better than 0% logging. And we allow users to correct estimates, which improves accuracy over time."

**"Only 10% of doctors use wearable data. Why would they adopt this?"**
> "Because we don't ask doctors to change their workflow. They scan a QR code — something they already do for payments and check-ins — and see a one-page summary. No new software to learn, no EHR integration required for the MVP. We meet doctors where they are."

---

## 14. Why This Platform Doesn't Exist Yet (And Why 2026 Is the Right Time)

### The Honest Answer

No single barrier is insurmountable. The reason no unified platform exists is that **all 7 barriers compound simultaneously** — and solving them all before running out of funding is why Google, Microsoft, and dozens of well-funded startups have failed.

### The 7 Barriers

#### Barrier 1: Technical Interoperability Is Genuinely Hard

Despite FHIR being the agreed standard, **84% of hospitals using FHIR APIs still struggle with seamless data exchange.** The problems:

- **Semantic interoperability is unsolved.** Two systems can both "speak FHIR" and still not understand each other — different organizations map lab results to different coding systems (SNOMED-CT, ICD-10, LOINC, proprietary codes).
- **Apple HealthKit is local-only.** No server-side API exists. Data stays on the phone. You can't query a user's Apple Health data from the cloud — the app must run on-device.
- **Wearable API fragmentation is severe.** Each vendor (Fitbit, Garmin, Oura, Whoop, Apple Watch) uses different auth flows, schemas, sync models, and rate limits. Teams estimate 2-3 weeks per integration but actually ship 3-6 months later.

**Failed example:** Tidepool (open-source diabetes data platform) has spent years building device integrations one at a time.

**Hackathon argument:** Use middleware like **Terra API** or **Vital** — they've already normalized wearable/CGM data across vendors. One integration instead of six. For clinical data, FHIR SMART on FHIR for EHR access. We're building an aggregation layer, not solving interoperability.

#### Barrier 2: Regulatory Minefield (HIPAA + FDA)

- **HIPAA compliance costs $45,000-$300,000** for initial development + $4,000-$12,000/year ongoing
- Average healthcare data breach cost: **$10.22 million** in the US (2025)
- **FDA classification is treacherous:** If your app makes claims like "your glucose response to this meal suggests..." it could be classified as Software as a Medical Device (SaMD), requiring 510(k) clearance

**Hackathon argument:** Position as a **general wellness + data visualization tool**, not a diagnostic tool. The FDA's **January 2026 updated guidance** specifically loosened oversight of general wellness devices and certain Clinical Decision Support software. We display data and let users share with doctors — we never make clinical claims. This keeps us in the unregulated category.

#### Barrier 3: Device Manufacturer Lock-In

Manufacturers benefit from keeping data captive:

| Device | Lock-in mechanism |
|--------|------------------|
| **Dexcom** | API access requires approval from Strategic Partnerships team. "Limited Access" allows only 5 authorized users in production. Full access requires a Data Licensing Agreement. |
| **Abbott Libre** | No direct NFC scanning from third-party apps (legal restriction). Data only through LibreView OAuth. |
| **Apple Health** | Local-only, no backend API. Apple will never provide a cloud API. |

**Hackathon argument:** For the demo, use Dexcom's **sandbox API** (provides simulated data without partnership approval). For production, use middleware (Terra, Vital) that has already negotiated these partnerships. Position our platform as beneficial to manufacturers — more engagement = more device sales.

#### Barrier 4: The Clinical vs. Consumer Data Gap

Clinical data and consumer wearable data exist in different universes:

| Dimension | Clinical Data | Consumer Wearable Data |
|-----------|--------------|----------------------|
| Standards | HL7/FHIR, LOINC, SNOMED-CT | Proprietary per vendor |
| Validation | FDA-regulated, lab-certified | Manufacturer self-validated |
| Format | Structured codes + narrative | JSON blobs, CSVs |
| Storage | EHR systems (Epic, Cerner) | Cloud APIs, phone-local |

There is **currently no standard for storing patient wellness data.** Comparing a Garmin heart rate to an Apple Watch heart rate to a clinical ECG is not straightforward — different sensors, algorithms, confidence intervals.

**Hackathon argument:** Build a normalization layer that converts each source into our own internal schema, clearly labeling source and confidence level. Transparency about data provenance is the feature, not a limitation.

#### Barrier 5: Doctors Won't Look at Your Data

- **No reimbursement:** Doctors are generally not paid for reviewing home-collected data
- **Information overload:** Patient-generated data requires accessing dashboards outside the EHR
- **Skepticism:** Clinicians express "more negative or skeptical feelings toward the data" vs patients' perceived benefits
- **47% of clinicians** report they cannot easily access patient info from outside organizations through their EHRs
- **Apple's "Share with Provider" feature** illustrates this perfectly — patients are confused, doctors don't know how to receive it

**Hackathon argument:** Don't build for doctor adoption initially. Build for the **patient-to-nutritionist/coach** use case first. For doctors, offer a one-page PDF/QR summary — not a firehose of data. Meet doctors where they are: a scannable report, not a new dashboard.

#### Barrier 6: 96.6% of Users Will Leave in 30 Days

The brutal retention numbers:
- **25% abandon** after a single use
- **53% uninstall** within 30 days
- Only **3.4% still active** at day 30
- **70% of nutrition app users** quit within 2 weeks if tracking feels complex
- Root causes: 40% UX problems, 35% content inadequacies, 25% design flaws

**Google Health's original failure** was fundamentally about this: nobody wants to manually enter health data.

**Hackathon argument:** Our value proposition is "fewer apps, not one more app." Passive data collection by default — auto-sync CGM, auto-sync wearable, auto-import labs. AI photo logging instead of manual food entry. The demo should show a user opening ONE app and seeing everything — not configuring six integrations.

#### Barrier 7: The Business Model Is Unsustainable

- **B2C (consumer subscription):** Low willingness to pay, extreme churn
- **B2B (sell to hospitals/insurers):** 6-18 month sales cycles, requires clinical validation
- **B2C2B (build user base, then sell to businesses):** Most promising but needs capital upfront

**The graveyard:**
| Company | Backed by | Fate |
|---------|----------|------|
| Google Health | Google ($billions) | Shut down 2011 — nobody wanted to manually enter records |
| Microsoft HealthVault | Microsoft | Shut down 2019 after 12 years — never found sustainable model |
| Revolution Health | Steve Case (AOL founder) | Lasted only a few years |
| Dossia Consortium | Employer consortium | Shut down 2016 after 10 years |
| Veri | VC-funded | Acquired and shut down by Oura, Sept 2024 |

**Hackathon argument:** B2C2B model. Free consumer layer for aggregation → paid B2B layer for clinicians/coaches → employer wellness program integration. Don't pitch as a subscription app. Pitch as a platform that makes health data portable and actionable — the business comes from providers who want to monitor their patients.

### Why 2026 Is Different: The Window Is Opening

| What changed | Impact |
|-------------|--------|
| **Cures Act enforcement is real** (fines up to $1M/violation, active Feb 2026) | EHR data access is finally improving |
| **FDA loosened digital health regulation** (Jan 2026 guidance) | Wellness apps have clearer safe harbor |
| **Middleware APIs matured** (Terra, Vital, Spike) | Wearable integration dropped from 6 months to weeks |
| **AI/LLMs enable new UX** | Photo food logging, conversational interfaces, personalized insights |
| **CGM going mainstream** (non-diabetic wellness market) | Larger addressable market beyond diabetics |
| **Post-COVID health awareness** | More people tracking more metrics than ever |

### The Pitch Line

> "Google tried this in 2008 and failed because they asked users to manually enter data. Microsoft tried for 12 years and couldn't find a business model. What's different now? Three things: AI can now eliminate manual data entry — snap a photo, your food is logged. Middleware APIs have solved the wearable integration problem. And the 21st Century Cures Act is finally forcing data silos open. The pieces that were missing for 15 years are now in place. Glymmy is built for 2026, not 2008."

---

## 15. Open-Source Tools, Models & Protocols — Technical Reference

### A. Glucose Prediction Models (Open Source)

| Tool | What it does | GitHub / Link | Tech |
|------|-------------|--------------|------|
| **Personalized DIY Glucose Prediction** | DL-based personalized glucose prediction up to 1 hour ahead from CGM data. Dockerized, validated on 29 T1D patients. | [GitHub](https://github.com/antorguez95/Personalized-AI-Based-Do-It-Yourself-Glucose-Prediction-tool) | Python, TensorFlow, Docker |
| **GlucoBench** | Curated CGM datasets + benchmark implementations for multiple ML models for glucose forecasting | [GitHub](https://github.com/IrinaStatsworthy/GlucoBench) | Python |
| **GluPredKit** | End-to-end pipeline: data fetching → processing → training → evaluation → real-time glucose predictions | [GitHub](https://github.com/topics/glucose-prediction) | Python |
| **Blood-Glucose-Prediction-LSTM** | LSTM-based blood glucose concentration prediction from CGM time series | [GitHub](https://github.com/dongsikchoi/Blood-Glucose-Prediction-LSTM) | Python, LSTM |
| **PhyPredict** | Physiological model + particle filter for glucose prediction | [GitHub](https://github.com/topics/glucose-prediction) | Python |
| **Awesome Diabetes Software** | Curated list of ALL open-source diabetes tools (CGM, prediction, insulin, analysis) | [GitHub](https://github.com/gcappon/awesome-diabetes-software) | Meta-list |

**Key research (2025):** A Nature paper describes a deep learning framework for virtual CGM and glucose prediction from life-log data — meaning prediction even without a CGM device, using food, activity, and sleep data.

### B. Food Recognition & Calorie Estimation Models

| Tool | What it does | GitHub / Link | Tech |
|------|-------------|--------------|------|
| **Indian Food Recognition + Calorie** | YOLOv5 transformer model for 36 Indian food classes. 95.3% accuracy, ±10 cal error | [GitHub](https://github.com/Yogeshpvt/Deep-Learning-Based-Food-Recognition-and-Calorie-Estimation-for-Indian-Food-Images) | YOLOv5, Python |
| **FoodNet** | Multi-task DL for ingredient recognition + calorie estimation simultaneously | [GitHub](https://github.com/Cheng-K/FoodNet) | Python, PyTorch |
| **Calorie-Predictor** | Mask R-CNN for food recognition + weight estimation → calorie prediction | [GitHub](https://github.com/Yiming-Miao/Calorie-Predictor) | Python, Mask R-CNN |
| **Caloriemate** | Self-hosted, privacy-focused AI calorie tracker using OpenRouter/Ollama + CLIP embeddings | [GitHub](https://github.com/ignoxx/caloriemate) | Python, Ollama |
| **Food.AI** | Real-time food detection on Android using MobileNetV2 SSD | [GitHub](https://github.com/jonathanyin12/Food.AI) | Android, TensorFlow |
| **FoodCalorieEstimation** | Transfer learning on Inception-v3 + Flask API + frontend | [GitHub](https://github.com/Nikhilchakravarthy1303/FoodCalorieEstimation) | Python, Flask |

**Indian Food Specific Research:**
- **IndianFoodNet:** 30 Indian food classes, published in IIETA journal
- **YOLOv8 Indian Food Model:** 92.7% mAP, ±5% calorie estimation error vs professionally calculated values
- **South Indian Food CNN:** Real-time calorie estimation for 11 South Indian dishes (IEEE 2024)

**Nutritional Databases (APIs):**
- **USDA FoodData Central** — Gold standard, free API, but limited coverage of South Asian foods
- **Open Food Facts** — Open-source, crowd-sourced, 3M+ products, includes barcode scanning
- **Nutritionix API** — Commercial, largest restaurant food database
- **Edamam API** — Commercial, nutrition analysis from text/recipe input

### C. BMI / Body Fat Estimation Models

| Tool | What it does | GitHub / Link | Tech |
|------|-------------|--------------|------|
| **BodyScan** | Estimate body fat % from a single photo | [GitHub](https://github.com/arvkr/BodyScan) | Python, CV |
| **face-to-bmi-vit** | Predict BMI from a face photo. 39.5% better than previous benchmarks | [GitHub](https://github.com/liujie-zheng/face-to-bmi-vit) | Python, ViT |
| **Digital Scale (2025 paper)** | BMI estimation from smartphone camera images, trained on large real-world dataset | [arXiv](https://arxiv.org/html/2508.20534v1) | Deep Learning |
| **bodyfat-estimation-mlp** | Neural network for body fat % from anthropometric measurements (height, weight, waist, etc.) | [GitHub](https://github.com/ChanMeng666/bodyfat-estimation-mlp) | Python, MLP |
| **OpenScale** | Open-source Android app for weight & body metrics tracking with Bluetooth scale support | [GitHub](https://github.com/oliexdev/openScale) | Android, Java |

### D. Wearable Data — How to Get the Data

#### Option 1: Middleware APIs (Recommended for Production)

| Platform | Devices Supported | Key Features | Pricing | Notes |
|----------|------------------|-------------|---------|-------|
| **[Terra API](https://tryterra.co/)** | 500+ sources (Garmin, Fitbit, Apple, Google, Polar, Oura, Eight Sleep, Dexcom, Abbott) | Unified REST API, real-time webhooks, HIPAA/GDPR/SOC2 compliant | Free tier available, paid plans scale | Y Combinator backed. Best for consumer wearables. |
| **[Vital (now Junction)](https://www.tryvital.io/)** | 500+ devices + lab testing API | Wearables + lab orders in one API | Free tier, paid plans | Recently rebranded to Junction. Unique lab testing integration. |
| **[Validic](https://validic.com/)** | Enterprise-grade, 500+ devices | Used by health systems, pharma | Enterprise pricing | Best for B2B/clinical use cases |

**How they work:** You integrate ONE SDK/API → User connects their device through an OAuth flow → Middleware normalizes all data into a standard JSON schema → You get webhooks with heart rate, sleep, activity, glucose, etc. in a unified format.

#### Option 2: Open-Source Tools (Free, DIY)

| Tool | What it does | Link | Supports |
|------|-------------|------|----------|
| **[Nightscout](https://github.com/nightscout/cgm-remote-monitor)** | Open-source CGM data visualization & storage in the cloud. The gold standard for DIY CGM data. | [nightscout.github.io](http://nightscout.github.io/) | Dexcom G5/G6/G7/ONE, Libre, Medtronic, Eversense |
| **[xDrip+](https://github.com/NightscoutFoundation/xDrip)** | Android app that reads CGM data directly and uploads to Nightscout, Tidepool, MongoDB, or InfluxDB | [GitHub](https://github.com/NightscoutFoundation/xDrip) | Dexcom G6/G7/ONE/Stelo, Libre |
| **[Gadgetbridge](https://gadgetbridge.org/)** | Open-source Android app that replaces vendor apps for smartwatches/bands. No cloud, no tracking. | [GitHub](https://codeberg.org/Freeyourgadget/Gadgetbridge) | Xiaomi Mi Band, Amazfit, Pinetime, Fossil, Casio, 80+ devices |
| **[OpenScale](https://github.com/oliexdev/openScale)** | Open-source body metrics tracker with Bluetooth scale support | [GitHub](https://github.com/oliexdev/openScale) | Xiaomi, Yunmai, Sanitas, 20+ Bluetooth scales |
| **[Tidepool](https://www.tidepool.org/)** | Open-source diabetes data platform. Aggregates CGM + insulin pump data. | [GitHub](https://github.com/tidepool-org) | Dexcom, Medtronic, Tandem, Omnipod, Libre |
| **[Open mHealth](https://www.openmhealth.org/)** | Open standard (IEEE 1752.1) for mobile health data + FHIR mapping | [openmhealth.org](https://www.openmhealth.org/) | Standard, not a device tool |

#### Option 3: Direct Device APIs (If you need specific devices)

| Device | API Access | Auth | Data Available | Limitations |
|--------|-----------|------|---------------|-------------|
| **Dexcom** | [developer.dexcom.com](https://developer.dexcom.com) | OAuth 2.0 | Glucose (EGV), calibrations, events | Sandbox free (5 users). Production requires partnership approval. |
| **Abbott Libre** | Via LibreView OAuth | OAuth | Glucose readings | No direct NFC access. Must go through LibreView. |
| **Apple HealthKit** | iOS SDK only | On-device permission | HR, steps, sleep, workouts, glucose, SpO2, everything | **Local only — no cloud API.** App must run on iPhone. |
| **Google Health Connect** | Android SDK | On-device permission | HR, steps, sleep, nutrition, body measurements | Android 14+ built-in. Local API, similar to HealthKit. |
| **Fitbit** | [dev.fitbit.com](https://dev.fitbit.com) | OAuth 2.0 | HR, sleep, SpO2, steps, activity | Rate limited. Intraday data requires special access. |
| **Garmin** | [developer.garmin.com](https://developer.garmin.com) | OAuth | HR, stress, sleep, SpO2, body battery | Push API (Garmin pushes to your server). Registration required. |
| **Oura Ring** | [cloud.ouraring.com/docs](https://cloud.ouraring.com/docs) | OAuth 2.0 + Personal Access Token | Sleep, readiness, activity, HR, HRV, SpO2, temperature | Free for personal use. |
| **Samsung Health** | Samsung Health SDK | SDK | HR, sleep, steps, stress | Limited to Samsung devices. SDK access requires approval. |

### E. Communication Protocols — How Wearables Actually Talk

#### BLE (Bluetooth Low Energy) — The Universal Protocol

**Every** modern health wearable uses BLE. Here's how it works:

```
┌──────────────┐     BLE (Bluetooth Low Energy)      ┌──────────────┐
│  Wearable    │ ──────────────────────────────────── │  Phone       │
│  (CGM, Watch)│   GATT Profile (structured data)    │  (Your App)  │
└──────────────┘                                      └──────────────┘
```

**GATT (Generic Attribute Profile)** — The data structure:
- **Services** = containers grouping related data (e.g., "Heart Rate Service")
- **Characteristics** = individual data values (e.g., "Heart Rate Measurement")
- Bluetooth SIG defines **standard health profiles:**
  - Heart Rate Profile (UUID: 0x180D)
  - Blood Pressure Profile (UUID: 0x1810)
  - Glucose Profile (UUID: 0x1808)
  - Health Thermometer (UUID: 0x1809)
  - Pulse Oximeter (UUID: 0x1822)
  - Body Composition (UUID: 0x181B)

**In practice:** Most commercial wearables (Fitbit, Apple Watch, Garmin) do NOT expose raw BLE GATT to third parties. They encrypt BLE communication and force you through their cloud API. **Open-source tools like Gadgetbridge reverse-engineer these protocols** to read data directly.

#### Other Protocols

| Protocol | Use | Details |
|----------|-----|---------|
| **IEEE 11073 PHD** | Medical-grade devices | Standard for Personal Health Devices. Maps to BLE GATT health profiles. Used in clinical-grade devices. |
| **FHIR (HL7)** | Clinical data exchange | The standard for EHR interoperability. Can represent wearable data as FHIR Observations. |
| **Open mHealth + IEEE 1752.1** | Mobile health data standardization | JSON schemas for sleep, physical activity, heart rate, etc. Maps to FHIR. 6,000+ developers use it. |
| **ANT+** | Some fitness devices (Garmin) | Alternative to BLE for fitness sensors. Less common now. |
| **Wi-Fi / Cellular** | Smart scales, home devices | Some devices (Withings scales) upload directly via Wi-Fi. |

### F. Recommended Technical Stack for Glymmy

Based on all research, here's what's realistic:

| Layer | Tool | Why |
|-------|------|-----|
| **CGM Data** | Nightscout (open-source) or Terra API (commercial) | Nightscout is free and battle-tested by the diabetes community. Terra if you want multi-vendor support. |
| **Wearable Data** | Terra API or Google Health Connect + Apple HealthKit | Terra normalizes everything. Health Connect/HealthKit for on-device. |
| **Food Recognition** | Indian Food YOLOv5 model + Claude/GPT-4V for general foods | YOLOv5 model handles Indian food with 95% accuracy. LLM for everything else. |
| **Glucose Prediction** | Personalized DIY Glucose Prediction tool | Dockerized, validated, personal model per user. |
| **Lab Analysis** | Claude API (multimodal — reads report images/PDFs) | No open-source tool matches LLM quality for interpreting lab reports. |
| **BMI/Body Comp** | OpenScale + standard BMI formula + bodyfat-estimation-mlp | OpenScale for Bluetooth scales. MLP model for body fat from measurements. |
| **Data Standard** | Open mHealth JSON schemas → FHIR mapping | IEEE 1752.1 standard. Future-proofs for clinical integration. |
| **Health Chatbot** | Claude API with RAG over user's health data | Best conversational quality for health Q&A. |

### G. Key Insight for the Hackathon

**You don't need to build integrations from scratch.** The open-source ecosystem is rich:

1. **Nightscout + xDrip+** already solve CGM data collection and cloud storage (used by thousands of diabetics daily)
2. **Gadgetbridge** already reads data from 80+ wearable devices without vendor apps
3. **Terra API** already normalizes 500+ device sources into one API (free tier available)
4. **Open mHealth** already defines the JSON schemas for standardizing this data
5. **YOLOv5 Indian food model** already recognizes 36 Indian food classes at 95% accuracy
6. **Claude/GPT-4V** already does food photo analysis and lab report interpretation

**The innovation isn't building new ML models — it's stitching these existing tools into one coherent platform with a unified UX.** This is exactly what past hackathon winners did (see Section 12: "it was much more about stitching together different tools to do interesting things").
