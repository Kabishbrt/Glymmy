# Real-World Datasets for Glymmy POC Demos

> Research compiled 2026-03-24. All datasets listed are free or academic-access unless noted.

---

## 1. CGM (Continuous Glucose Monitor) Data

### 1a. OhioT1DM Dataset
- **URL:** https://webpages.charlotte.edu/rbunescu/data/ohiot1dm/OhioT1DM-dataset.html
- **Size:** 12 participants (6 in 2018, 6 added in 2020), 8 weeks each
- **Contains:** CGM readings every 5 min, insulin (bolus + basal), self-reported meals with carb estimates, exercise/sleep/stress events, physiological sensor data from fitness bands
- **Format:** XML
- **License:** Data Use Agreement (DUA) required -- email researchers, typically approved for academic use within days
- **POC target:** POC-1 (Glucose Prediction) -- this is the gold standard for glucose prediction research
- **Also on Kaggle (mirror):** https://www.kaggle.com/datasets/ryanmouton/ohiot1dm

### 1b. GlucoBench (Preprocessed CGM Collection)
- **URL:** https://github.com/IrinaStatsLab/GlucoBench
- **Size:** 5 curated public CGM datasets, pre-processed into standardized CSV format
- **Contains:** CGM time series from multiple studies, ready for ML training with benchmark model implementations
- **License:** Varies by source dataset (all publicly available)
- **POC target:** POC-1 -- best "plug and play" option since data is already cleaned and formatted
- **Bonus:** Includes benchmark ML models for glucose prediction out of the box

### 1c. Awesome-CGM (Dataset Directory)
- **URL:** https://github.com/IrinaStatsLab/Awesome-CGM
- **Size:** 17+ datasets linked, covering T1D, T2D, and healthy subjects
- **Key freely downloadable datasets within:**
  - Hall (2018): 57 healthy/pre-diabetic subjects
  - Dubosson (2018): 9 T1D subjects with meal annotations
  - Broll (2021): 5 T2D subjects
  - Colas (2019): 208 healthy/T2D subjects
- **License:** Each dataset has its own terms; most are open or DUA-based
- **POC target:** POC-1 -- use as a directory to find the right dataset for your specific need

### 1d. OpenAPS Data Commons
- **URL:** https://openaps.org/outcomes/data-commons/
- **Hosted on:** https://www.openhumans.org/activity/openaps-data-commons/
- **Size:** 183+ participants, 46,070+ days of data, 10M+ CGM data points
- **Contains:** CGM readings, insulin dosing (bolus + basal), algorithmic decision data from open-source automated insulin delivery systems
- **License:** Application required -- must agree to share findings back with the OpenAPS community
- **POC target:** POC-1 -- largest freely available diabetes dataset; excellent for demonstrating real-world scale

### 1e. Tidepool Big Data Donation Project
- **URL:** https://www.tidepool.org/bigdata
- **Size:** 50,000+ donors (largest real-world diabetes dataset)
- **Contains:** CGM data, insulin pump data, glucose values from diverse diabetes devices
- **License:** Licensing agreement required -- contact bigdata@tidepool.org. Some subsets available at no cost for researchers
- **POC target:** POC-1 -- if approved, this is the most comprehensive dataset available

### 1f. Kaggle CGM Datasets (Quick Access)
- **GlucoBench on Kaggle:** https://www.kaggle.com/datasets/omenkj/glucobench-glucose-monitoring-and-lifestyle-data
- **Blood Glucose Level Readings:** https://www.kaggle.com/datasets/ashmitcajla/dataset-for-blood-glucose-level-readings
- **License:** Varies (check each), most CC0 or CC-BY
- **POC target:** POC-1 -- fastest to download for a quick demo

---

## 2. Food / Nutrition Datasets

### 2a. Nutrition5k (Google Research) -- TOP PICK
- **URL:** https://github.com/google-research-datasets/Nutrition5k
- **Download:** Google Cloud Storage bucket (direct download)
- **Size:** 5,000+ plates of food
- **Contains:** RGB images (side-angle rotating videos + overhead RGB-D), per-ingredient mass, calories, macronutrients (fat, protein, carbs), ingredient lists with USDA-sourced nutritional data
- **Format:** Images + CSV metadata
- **License:** Creative Commons 4.0 (CC BY 4.0) -- free for any purpose including commercial
- **POC target:** POC-3 (Food Scanning) -- this is the ideal dataset: real food images WITH nutritional ground truth

### 2b. Food-101
- **URL:** https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/
- **Also:** https://huggingface.co/datasets/ethz/food101 | https://www.kaggle.com/datasets/dansbecker/food-101
- **Size:** 101,000 images across 101 food categories (750 train + 250 test per class)
- **Contains:** Food images only (NO nutritional data) -- useful for food classification/recognition
- **Format:** JPEG images, 512px max side
- **License:** Open (research use)
- **POC target:** POC-3 -- use for food recognition model, pair with USDA data for nutrition lookup

### 2c. FoodX-251
- **URL:** https://arxiv.org/abs/1907.06167 (paper) | Available via iFood-2019 Kaggle challenge
- **Size:** 251 food categories, 158k images (120k train + 12k val + 28k test)
- **Contains:** Fine-grained food images with human-verified labels
- **License:** Non-commercial research and educational use only
- **POC target:** POC-3 -- larger category set than Food-101, better for diverse food recognition

### 2d. USDA FoodData Central
- **URL:** https://fdc.nal.usda.gov/download-datasets/
- **API:** https://fdc.nal.usda.gov/api-guide/ (free API key signup)
- **Size:** 300,000+ food items across multiple databases (Foundation Foods, SR Legacy, Branded Foods, FNDDS)
- **Contains:** Detailed nutritional composition per food item -- calories, macros, micronutrients, vitamins, minerals
- **Format:** CSV and JSON bulk downloads
- **License:** Public domain (CC0) -- no restrictions whatsoever
- **POC target:** POC-3 -- essential lookup table to pair with any food recognition model. Use API for real-time nutrition lookup in demo

### 2e. Indian Food Datasets (South Asian)
- **Indian Food Images Dataset:** https://www.kaggle.com/datasets/iamsouravbanerjee/indian-food-images-dataset
- **Indian Food and Recipes (with images):** https://www.kaggle.com/datasets/kishanpahadiya/indian-food-and-its-recipes-dataset-with-images
- **Indian Food Classification (80 categories):** https://www.kaggle.com/datasets/l33tc0d3r/indian-food-classification (~4,000 images)
- **Size:** Varies, 20-80 food categories, hundreds to thousands of images
- **Contains:** Indian food images with category labels; some include recipe data
- **License:** Kaggle standard (check each, mostly CC-BY or CC0)
- **POC target:** POC-3 -- critical for Glymmy's South Asian user base. Pair with USDA for nutritional values

---

## 3. Lab Report / Blood Test Datasets

### 3a. MIMIC-IV Demo (No Credentialing Required) -- TOP PICK FOR DEMO
- **URL:** https://physionet.org/content/mimic-iv-demo/2.2/
- **Also on Kaggle:** https://www.kaggle.com/datasets/montassarba/mimic-iv-clinical-database-demo-2-2
- **Also on Hugging Face:** https://huggingface.co/datasets/physionet/mimic-iv-demo
- **Size:** 100 patients, 15.5 MB uncompressed
- **Contains:** Full lab results (labevents table), diagnoses, procedures, prescriptions, ICU data -- everything from MIMIC-IV but for 100 patients
- **Format:** CSV files
- **License:** Open access -- NO credentialing required (unlike full MIMIC-IV)
- **POC target:** POC-5 (Lab Report Interpreter) -- perfect for demo. Real hospital lab data, freely downloadable

### 3b. MIMIC-IV (Full)
- **URL:** https://physionet.org/content/mimiciv/3.1/
- **Size:** ~300,000+ hospital admissions, millions of lab results
- **Contains:** Complete EHR data including all laboratory measurements (CBC, metabolic panels, liver function, etc.), diagnoses, medications
- **License:** Credentialed access required (PhysioNet account + CITI training course, typically takes 1-2 days)
- **POC target:** POC-5 -- if you need scale beyond the demo

### 3c. Kaggle Lab Test Datasets
- **Laboratory Test Results (Anonymized):** https://www.kaggle.com/datasets/pinuto/laboratory-test-results-anonymized-dataset
  - Contains: Ferritin, HbA1c, IgE, Insulin, TSH, Free T4, Hemoglobin, WBC, Platelets, MCV, RDW, glucose, bilirubin
  - Includes reference ranges, status (Normal/High/Low), and recommended follow-up
  - License: CC0 Public Domain
  - Great for demo -- has exactly the fields Glymmy needs (test name, result, reference range, interpretation)

- **Complete Blood Count (CBC):** https://www.kaggle.com/datasets/ahmedelsayedtaha/complete-blood-count-cbc-test

- **Hematology CBC from MIMIC-III:** https://www.kaggle.com/datasets/ashlingovindasamy/hematology-complete-blood-count-dataset-mimic-iii

- **Predicting Blood Analysis:** https://www.kaggle.com/datasets/bonastreyair/predicting-blood-analysis

- **POC target:** POC-5 -- multiple options for different lab test types

### 3d. Symile-MIMIC (Multimodal)
- **URL:** https://physionet.org/content/symile-mimic/1.0.0/
- **Contains:** Chest X-rays + ECGs + up to 50 common blood lab results per sample (derived from MIMIC-IV + MIMIC-CXR)
- **License:** Credentialed access (PhysioNet)
- **POC target:** POC-5 -- useful if you want to show cross-modal health data analysis

---

## 4. Wearable / IoT Health Data

### 4a. LifeSnaps Fitbit Dataset -- TOP PICK
- **URL:** https://www.kaggle.com/datasets/skywescar/lifesnaps-fitbit-dataset
- **Paper:** https://www.nature.com/articles/s41597-022-01764-x
- **Size:** 71 participants, 4+ months, 71M+ rows of data, 35+ data types
- **Contains:** Heart rate, steps, sleep phases, temperature, SpO2, heart rate variability, stress scores, plus survey data (mood, personality, anxiety)
- **Device:** Fitbit Sense smartwatch
- **License:** CC BY 4.0
- **POC target:** POC-4 (Wearable IoT Data) -- richest wearable dataset available. Has modern metrics (HRV, SpO2, stress) that match what Glymmy would ingest

### 4b. FitBit Fitness Tracker Data (Classic)
- **URL:** https://www.kaggle.com/datasets/arashnic/fitbit
- **Size:** 30 users, ~45 MB, minute-level data
- **Contains:** Steps, heart rate, sleep monitoring, physical activity, calories burned
- **Format:** CSV
- **License:** CC0 Public Domain
- **POC target:** POC-4 -- smaller but instantly downloadable, good for quick demo

### 4c. PMData (Lifelogging + Wearable)
- **URL:** https://datasets.simula.no/pmdata/
- **Size:** 16 participants, 5 months
- **Contains:** Heart rate, activity levels (sedentary/light/moderate/vigorous), resting heart rate, sleep data with quality scores, deep sleep minutes, plus sports activity logs and subjective wellbeing reports
- **Device:** Fitbit Versa 2
- **Format:** CSV and JSON
- **License:** CC BY 4.0
- **POC target:** POC-4 -- good for showing longitudinal health trends

### 4d. Apple Watch and Fitbit Data
- **URL:** https://www.kaggle.com/datasets/aleespinosa/apple-watch-and-fitbit-data
- **Contains:** Combined data from both Apple Watch and Fitbit devices
- **License:** Kaggle standard
- **POC target:** POC-4 -- useful for showing multi-device data unification (core Glymmy feature)

### 4e. CAPTURE-24
- **URL:** Referenced in PMC (https://pmc.ncbi.nlm.nih.gov/articles/PMC11484779/)
- **Contains:** Large-scale wrist-worn activity tracker data collected in the wild for human activity recognition
- **POC target:** POC-4 -- activity recognition from wearable sensors

---

## Recommended Dataset Stack for Hackathon Demo

For the April 10-11 hackathon, here is the fastest path to real data in each POC:

| POC | Primary Dataset | Backup | Time to Access |
|-----|----------------|--------|----------------|
| **POC-1: Glucose Prediction** | GlucoBench (pre-processed) | Kaggle CGM datasets | Instant (GitHub clone) |
| **POC-3: Food Scanning** | Nutrition5k + USDA API | Food-101 + Indian Food datasets | Instant (GCS download + API key) |
| **POC-5: Lab Report Interpreter** | MIMIC-IV Demo + Kaggle Lab Results | Full MIMIC-IV (if time for credentialing) | Instant (demo) / 1-2 days (full) |
| **POC-4: Wearable IoT** | LifeSnaps Fitbit | FitBit Fitness Tracker Data | Instant (Kaggle download) |

### Quick-Start Commands

```bash
# GlucoBench (CGM data)
git clone https://github.com/IrinaStatsLab/GlucoBench.git

# Nutrition5k (food + nutrition)
# Browse: https://console.cloud.google.com/storage/browser/nutrition5k_dataset
# Or use gsutil:
# gsutil -m cp -r gs://nutrition5k_dataset/nutrition5k_dataset ./nutrition5k

# USDA FoodData Central (nutrition lookup)
# Get API key: https://fdc.nal.usda.gov/api-key-signup/
# Bulk download: https://fdc.nal.usda.gov/download-datasets/

# MIMIC-IV Demo (lab results)
wget -r -N -c -np https://physionet.org/files/mimic-iv-demo/2.2/

# Kaggle datasets (need kaggle CLI configured)
pip install kaggle
kaggle datasets download -d skywescar/lifesnaps-fitbit-dataset
kaggle datasets download -d pinuto/laboratory-test-results-anonymized-dataset
kaggle datasets download -d arashnic/fitbit
```
