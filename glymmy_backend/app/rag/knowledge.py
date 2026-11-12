"""Static medical knowledge documents used to seed the RAG index.

In production, these would be expanded with curated clinical guidelines,
patient-specific notes, and regional (South Asian) nutrition data.
"""

from __future__ import annotations

SEED_DOCUMENTS: list[dict[str, str]] = [
    {
        "id": "diabetes-basics",
        "title": "Type 2 Diabetes Basics",
        "source": "clinical-reference",
        "content": (
            "Type 2 diabetes is characterized by insulin resistance and high blood sugar. "
            "Key monitoring metrics include fasting glucose (<100 mg/dL normal), "
            "HbA1c (<5.7% normal, 5.7-6.4% prediabetic, ≥6.5% diabetic), and "
            "post-prandial glucose. Management involves diet, exercise, monitoring, "
            "and medication when needed."
        ),
    },
    {
        "id": "glucose-spikes",
        "title": "Glucose Spikes and Meal Composition",
        "source": "clinical-reference",
        "content": (
            "A glucose spike is a rapid rise in blood sugar after eating. Refined carbs "
            "cause the largest spikes; fiber, protein, and fat slow absorption. "
            "A 15-minute walk after a meal can reduce the peak by ~25%. "
            "Targets: post-meal glucose < 180 mg/dL, return to baseline within 3 hours."
        ),
    },
    {
        "id": "hypoglycemia",
        "title": "Hypoglycemia — Warning Signs",
        "source": "clinical-reference",
        "content": (
            "Hypoglycemia is blood glucose below 70 mg/dL. Symptoms: shakiness, sweating, "
            "confusion, rapid heartbeat. Below 55 mg/dL is severe. Nocturnal hypoglycemia "
            "is particularly dangerous — set alarms, eat a small bedtime snack if needed, "
            "and review insulin dosing with your doctor."
        ),
    },
    {
        "id": "liver-enzymes",
        "title": "SGOT (AST) and SGPT (ALT) — Liver Enzymes",
        "source": "clinical-reference",
        "content": (
            "SGOT (AST) and SGPT (ALT) are liver enzymes. Normal: SGOT 8-45 U/L, "
            "SGPT 7-56 U/L. Elevations can indicate fatty liver, alcohol use, "
            "medication side effects, or viral hepatitis. SGPT is more liver-specific. "
            "Mild elevation (<2x upper limit) is often from diet or medication; "
            "higher values need evaluation."
        ),
    },
    {
        "id": "lipids",
        "title": "Cholesterol and Cardiovascular Risk",
        "source": "clinical-reference",
        "content": (
            "Total cholesterol should be <200 mg/dL. LDL (bad) <100 for most, "
            "<70 for high-risk patients. HDL (good) >40 for men, >50 for women. "
            "Diabetic patients have elevated cardiovascular risk — target LDL <70. "
            "Mediterranean-style diet, regular aerobic exercise, and statin therapy "
            "when indicated help manage lipids."
        ),
    },
    {
        "id": "south-asian-foods",
        "title": "South Asian Foods and Glycemic Impact",
        "source": "nutrition-reference",
        "content": (
            "Common South Asian foods and their typical impact on glucose: "
            "White rice (high GI ~73), biryani (mixed ~65), roti/chapati (moderate ~62), "
            "dal/lentils (low ~42, slows glucose rise), paneer and grilled meats "
            "(protein, low GI). Pair rice with dal and vegetables to reduce the "
            "glycemic load. Fruits like mango and banana are higher GI — consume "
            "with protein or fat."
        ),
    },
    {
        "id": "kidney-function",
        "title": "Kidney Function — Creatinine and BUN",
        "source": "clinical-reference",
        "content": (
            "Creatinine (normal 0.7-1.3 mg/dL) and BUN (7-20 mg/dL) reflect kidney "
            "filtration. Diabetes is the leading cause of kidney disease — annual "
            "screening is critical. Stay hydrated, limit NSAIDs, manage blood pressure, "
            "and follow a moderate-protein diet."
        ),
    },
    {
        "id": "exercise-glucose",
        "title": "Exercise Effects on Glucose",
        "source": "clinical-reference",
        "content": (
            "Aerobic exercise (walking, cycling) lowers glucose both acutely and "
            "chronically by improving insulin sensitivity. 150 minutes/week of moderate "
            "activity is the standard target. A 15-minute post-meal walk can reduce "
            "post-prandial peaks by 25%. Resistance training helps long-term glucose "
            "control by increasing muscle mass."
        ),
    },
]
