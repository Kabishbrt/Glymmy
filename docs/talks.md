# Glymmy — 3-Minute Pitch Script

---

## Introduction (10 seconds)

"Hi, we're Team Glymmy — [names]. We're [brief team description, e.g., 'engineers, a designer, and a public health student']. We built Glymmy — think of it as your glycemic companion. The 'gly' is glycemic, the 'my' makes it yours."

---

## Problem Statement (20 seconds)

"A diabetic patient eats lunch and has no idea what's about to happen to their blood sugar. An athlete trains without knowing how yesterday's meal is affecting today's performance. Right now, glucose data lives in one app, food tracking in another, and lab results in a PDF nobody reads. There's no system that connects what you eat, how you move, and what your body does — and predicts what's coming next. That's what Glymmy does."

---

## Product (1 minute)

### Beat 1: The Integration Layer (~15s)

"Glymmy connects to devices you already own — your CGM streams glucose every 5 minutes via Bluetooth, your smartwatch sends heart rate and sleep data, and our food scanner uses your phone camera. Instead of building hardware, we built the middleware that pulls all these data streams into one unified profile using open health standards like FHIR."

*Key terms to drop: BLE/Bluetooth Low Energy, FHIR, Nightscout (30k+ users), Terra API*

### Beat 2: The AI Layer (~25s)

"Once we have unified data, AI does three things:

1. **Predicts** — you photograph your lunch, our vision model identifies the food, estimates carbs, and predicts your glucose spike 30-60 minutes ahead
2. **Interprets** — upload a blood report, OCR extracts the values, and AI explains what your SGOT of 65 actually means in plain language
3. **Alerts** — detects dangerous overnight blood sugar drops and tells you *why* it happened, not just that it happened"

*Key terms to drop: computer vision, gradient boosting / time-series ML, OCR + LLM pipeline*

### Beat 3: The Design Decision (~20s)

"We deliberately chose no new hardware, no manual data entry, and fully open-source foundations. Every component — Nightscout for CGM, PaddleOCR for reports, USDA database for nutrition — is battle-tested in production. OpenAPS has been predicting glucose for 10+ years in real patients. We're not inventing new AI. We're connecting proven tools that nobody has unified before."

---

## Demo (1 minute)

> "Let me show you Ramesh's morning with Glymmy."

| Time | Demo | What you say |
|------|------|-------------|
| 0-25s | **Food scan** — photograph a plate of food | "Ramesh photographs his breakfast. Glymmy identifies dal, rice, and roti — estimates 65g carbs — and predicts a glucose spike of +38 mg/dL in the next 90 minutes. It suggests a 15-minute walk to cut that by 25%." |
| 25-45s | **Chatbot** — ask a question about the meal | "Ramesh asks: 'Is this a good breakfast given my trends?' The AI knows his CGM history, his labs, his activity — and gives a personalized answer, not a generic one." |
| 45-60s | **Lab report scan** — upload/photo a blood report | "His doctor appointment is tomorrow. He uploads his blood report — Glymmy extracts every marker, flags his elevated liver enzymes, and generates a shareable summary via QR code for his doctor." |

---

## Wrap-up (30 seconds)

"To recap — Glymmy does three things nobody else combines:

**One** — predicts your glucose spike before it happens, based on what you eat and your personal trends.

**Two** — reads your lab reports and turns confusing numbers into plain-language insights you can act on.

**Three** — puts your entire health picture behind one QR code your doctor can scan in seconds.

No new hardware. No manual data entry. Just the devices you already own, connected by AI that actually understands your body. Ramesh shouldn't need five apps to manage his health. With Glymmy, he needs one. Thank you."
