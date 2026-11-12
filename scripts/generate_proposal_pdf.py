#!/usr/bin/env python3
"""
Generate a publication-grade Hackathon Proposal PDF for Glymmy.
Harvard Health Systems Innovation Lab (HSIL) Hackathon 2026.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable,
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print total page count."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(
                45, 11 * inch - 32, "Glymmy — AI Glycemic Companion & SF-LG Smartwatch UI"
            )
            self.drawRightString(
                8.5 * inch - 45, 11 * inch - 32, "Harvard HSIL Hackathon 2026"
            )
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(45, 11 * inch - 36, 8.5 * inch - 45, 11 * inch - 36)

        # Footer (all pages)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * inch - 45, 28, page_text)
        self.drawString(
            45,
            28,
            "Confidential — Prepared for Harvard Health Systems Innovation Lab (HSIL)",
        )
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(45, 38, 8.5 * inch - 45, 38)

        self.restoreState()


def build_pdf(filename="Glymmy_Hackathon_Proposal.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=45,
        rightMargin=45,
        topMargin=46,
        bottomMargin=46,
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette
    PRIMARY = colors.HexColor("#0F172A")    # Slate 900
    ACCENT = colors.HexColor("#2563EB")     # Blue 600
    ACCENT_LIGHT = colors.HexColor("#EFF6FF")
    EMERALD = colors.HexColor("#059669")    # Emerald 600
    SLATE = colors.HexColor("#334155")      # Slate 700
    MUTED = colors.HexColor("#64748B")      # Slate 500
    BORDER = colors.HexColor("#E2E8F0")     # Slate 200

    # Typography Styles
    styles.add(
        ParagraphStyle(
            name="DocSuperTitle",
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            textColor=ACCENT,
            textTransform="uppercase",
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="DocTitle",
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=PRIMARY,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="DocSubTitle",
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            textColor=SLATE,
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="H1_Custom",
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=17,
            textColor=PRIMARY,
            spaceBefore=14,
            spaceAfter=6,
            keepWithNext=True,
        )
    )
    styles.add(
        ParagraphStyle(
            name="H2_Custom",
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=14,
            textColor=ACCENT,
            spaceBefore=9,
            spaceAfter=4,
            keepWithNext=True,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Body_Custom",
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=SLATE,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Body_Bold",
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=13,
            textColor=PRIMARY,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Callout",
            fontName="Helvetica-Oblique",
            fontSize=9.5,
            leading=14,
            textColor=PRIMARY,
        )
    )
    styles.add(
        ParagraphStyle(
            name="TableHeader",
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11,
            textColor=colors.white,
            alignment=0,
        )
    )
    styles.add(
        ParagraphStyle(
            name="TableCell",
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=SLATE,
        )
    )
    styles.add(
        ParagraphStyle(
            name="TableCellBold",
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=11,
            textColor=PRIMARY,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Badge",
            fontName="Helvetica-Bold",
            fontSize=7.5,
            leading=10,
            textColor=EMERALD,
        )
    )

    story = []

    # ── HEADER BANNER ───────────────────────────────────────────────────────────
    story.append(
        Paragraph("Harvard Health Systems Innovation Lab (HSIL) • Global Hackathon 2026", styles["DocSuperTitle"])
    )
    story.append(
        Paragraph("Glymmy: Unified AI Glycemic Companion & Smartwatch Interface", styles["DocTitle"])
    )
    story.append(
        Paragraph(
            "<b>Proposal Track:</b> Chronic Disease Management & Multimodal AI | <b>Team:</b> Glymmy | <b>Date:</b> November 2026",
            styles["DocSubTitle"],
        )
    )
    story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceBefore=0, spaceAfter=10))

    # ── EXECUTIVE SUMMARY CALLOUT ───────────────────────────────────────────────
    exec_summary_text = (
        "<b>Executive Hook:</b> Over 537 million people manage diabetes globally, yet their critical health data is "
        "scattered across disconnected silos: CGM apps, smartwatch fitness trackers, unread lab PDFs, and manual diaries. "
        "<b>Glymmy</b> is an AI-powered unified health companion that fuses Continuous Glucose Monitoring, wearable biometrics "
        "(HR, sleep, steps), and computer vision food logging into local predictive intelligence (Gemma 4). "
        "Its signature frontend innovation is the <b>SF-LG (Space-Filling Line Graph) Greedy Space Allocation Engine</b>, "
        "delivering non-occluding, actionable clinical intelligence directly onto circular smartwatch displays."
    )
    callout_data = [[Paragraph(exec_summary_text, styles["Callout"])]]
    callout_table = Table(callout_data, colWidths=[doc.width])
    callout_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), ACCENT_LIGHT),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#93C5FD")),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(callout_table)
    story.append(Spacer(1, 10))

    # ── SECTION 1: PROBLEM STATEMENT ───────────────────────────────────────────
    story.append(Paragraph("1. The Problem: Data Fragmentation & Clinical Inefficiency", styles["H1_Custom"]))
    story.append(
        Paragraph(
            "Managing Type 1 and Type 2 diabetes requires continuous synthesis of high-frequency biological signals. "
            "However, patients and clinicians face three compounding bottlenecks:",
            styles["Body_Custom"],
        )
    )

    prob_data = [
        [
            Paragraph("Siloed Data Domain", styles["TableHeader"]),
            Paragraph("Current Patient Experience", styles["TableHeader"]),
            Paragraph("Clinical Limitation / Unmet Need", styles["TableHeader"]),
        ],
        [
            Paragraph("<b>Continuous Glucose (CGM)</b>", styles["TableCellBold"]),
            Paragraph("Dexcom or Libre app shows numbers and simple alerts.", styles["TableCell"]),
            Paragraph("Isolated from meal composition, heart rate, and insulin timing.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>Wearable Biometrics</b>", styles["TableCellBold"]),
            Paragraph("Apple Watch/Garmin tracks HR, sleep, and steps.", styles["TableCell"]),
            Paragraph("Data is siloed as generic fitness, ignoring glycemic impact and nocturnal hypoglycemia.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>Food & Nutrition</b>", styles["TableCellBold"]),
            Paragraph("Manual logging in calorie counters or photo albums.", styles["TableCell"]),
            Paragraph("High friction, no automated carbohydrate estimation, no predictive spike guidance.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>Diagnostic Labs</b>", styles["TableCellBold"]),
            Paragraph("Paper reports or portal PDFs every 3–6 months.", styles["TableCell"]),
            Paragraph("Patients cannot interpret biomarkers (HbA1c, eGFR, lipid panels) between appointments.", styles["TableCell"]),
        ],
    ]
    prob_table = Table(prob_data, colWidths=[1.8 * inch, 2.5 * inch, 2.7 * inch])
    prob_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(prob_table)
    story.append(Spacer(1, 10))

    # ── SECTION 2: THE GLYMMY PLATFORM ARCHITECTURE ────────────────────────────
    story.append(Paragraph("2. The Glymmy Solution & Technical Architecture", styles["H1_Custom"]))
    story.append(
        Paragraph(
            "Glymmy unifies raw multimodal inputs into a private, local-first intelligence pipeline. "
            "Rather than inventing proprietary hardware, Glymmy leverages devices patients already own.",
            styles["Body_Custom"],
        )
    )

    arch_data = [
        [
            Paragraph("System Layer", styles["TableHeader"]),
            Paragraph("Technologies Used", styles["TableHeader"]),
            Paragraph("Functional Capability", styles["TableHeader"]),
        ],
        [
            Paragraph("<b>Multimodal Ingestion</b>", styles["TableCellBold"]),
            Paragraph("BLE GATT, HealthKit, Nightscout/xDrip+ API", styles["TableCell"]),
            Paragraph("Streams 5-min glucose, 10-min vitals (HR, SpO2, sleep, steps) and photo uploads.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>AI & Predictive Core</b>", styles["TableCellBold"]),
            Paragraph("Gemma 4 (Local via Ollama), ChromaDB RAG", styles["TableCell"]),
            Paragraph("Multimodal vision for meal carb extraction, post-prandial spike forecasting, and clinical QA.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>Backend Platform</b>", styles["TableCellBold"]),
            Paragraph("FastAPI, Python 3.12, Pydantic v2, uv", styles["TableCell"]),
            Paragraph("Sub-50ms API endpoints, asynchronous SSE alert streaming, Dubosson data normalization.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>Clinical Data Sharing</b>", styles["TableCellBold"]),
            Paragraph("HL7 FHIR R4 Bundle + QR Generator", styles["TableCell"]),
            Paragraph("Encodes longitudinal glucose profile into a 10-second QR scan for doctor visits.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>Frontend Clients</b>", styles["TableCellBold"]),
            Paragraph("Next.js 16 Web Dashboard + Vite Smartwatch", styles["TableCell"]),
            Paragraph("Comprehensive clinical web portal and standalone circular smartwatch interactive UI.", styles["TableCell"]),
        ],
    ]
    arch_table = Table(arch_data, colWidths=[1.8 * inch, 2.3 * inch, 2.9 * inch])
    arch_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(arch_table)
    story.append(Spacer(1, 10))

    # ── SECTION 3: SMARTWATCH COMPANION & SF-LG ALGORITHM ──────────────────────
    story.append(
        Paragraph("3. Core Innovation: SF-LG Smartwatch Space Allocation Engine", styles["H1_Custom"])
    )
    story.append(
        Paragraph(
            "A critical bottleneck on modern smartwatches is viewport occlusion: on a 300×300px circular bezel, "
            "displaying actionable advice typically forces the line graph to shrink or covers the data. "
            "Glymmy implements the <b>Space-Filling Line Graph (SF-LG) Greedy Space Allocation Algorithm</b>:",
            styles["Body_Custom"],
        )
    )

    sflg_desc = (
        "<b>Algorithm Operation:</b><br/>"
        "• <b>Coordinate Projection:</b> Maps glucose readings (40–240 mg/dL) onto bounded circular SVG coordinates.<br/>"
        "• <b>Valleys Discovery:</b> Scans all X-axis slices (width ≥ 38px) and computes local curve extrema (Ymin, Ymax).<br/>"
        "• <b>Candidate Rectangles:</b> Identifies vacant 'headroom' above the curve and 'footroom' below the curve.<br/>"
        "• <b>Greedy Area Allocation:</b> Sorts candidates by area descending and non-overlappingly assigns the top two pockets to host dynamic contextual cards."
    )
    story.append(Paragraph(sflg_desc, styles["Body_Custom"]))

    feature_data = [
        [
            Paragraph("Interactive Watch Scenario", styles["TableHeader"]),
            Paragraph("Allocated Valley & Trigger", styles["TableHeader"]),
            Paragraph("Clinical Impact & User Interaction", styles["TableHeader"]),
        ],
        [
            Paragraph("<b>S4: Post-Meal Spike & Walk Advisor</b><br/><i>(Signature Feature)</i>", styles["TableCellBold"]),
            Paragraph("Valley Above Curve<br/>Triggered by Meal Pin (52g carbs)", styles["TableCell"]),
            Paragraph("Shows predicted peak (192 mg/dL). User clicks 'Simulate 15-min Walk' — the CGM curve dynamically blunts to 138 mg/dL (-25 mg/dL) in real time.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>S1: Point Vitals Correlation</b>", styles["TableCellBold"]),
            Paragraph("Largest Valley<br/>Triggered by Point Tap", styles["TableCell"]),
            Paragraph("Reveals glucose value, trend vector (↗/↘/→), plus correlated Heart Rate (bpm) and active Insulin on Board (IOB).", styles["TableCell"]),
        ],
        [
            Paragraph("<b>S2: Rapid Drop & Rule of 15</b>", styles["TableCellBold"]),
            Paragraph("Second Largest Valley<br/>Ambient Pulsing Alert", styles["TableCell"]),
            Paragraph("Expands to clinical rescue: 'Rule of 15: Eat 15g fast carbs & retest in 15m' with tachycardia monitoring.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>S3: Comparative Analysis</b>", styles["TableCellBold"]),
            Paragraph("Two Largest Valleys<br/>Tap 2 Points", styles["TableCell"]),
            Paragraph("Displays Point A vs Point B with exact glycemic delta (Δ mg/dL) and time elapsed.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>Ambient Bezel Complications</b>", styles["TableCellBold"]),
            Paragraph("Top Apex Arc (Y: 8px to 28px)", styles["TableCell"]),
            Paragraph("Centered complication stack: Time (10:09) flanked by Time-in-Range (TIR 84%) and IOB (1.4U), cleanly contoured inside the circular bezel.", styles["TableCell"]),
        ],
    ]
    feature_table = Table(feature_data, colWidths=[2.2 * inch, 2.1 * inch, 2.7 * inch])
    feature_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(feature_table)
    story.append(Spacer(1, 10))

    # ── SECTION 4: CLINICAL VALIDATION & DATASETS ──────────────────────────────
    story.append(Paragraph("4. Clinical Grounding, Datasets & Validation", styles["H1_Custom"]))
    story.append(
        Paragraph(
            "Glymmy is calibrated against validated, real-world clinical datasets rather than arbitrary heuristics:",
            styles["Body_Custom"],
        )
    )

    ds_data = [
        [
            Paragraph("Dataset / Cohort", styles["TableHeader"]),
            Paragraph("Data Contents", styles["TableHeader"]),
            Paragraph("Application in Glymmy Pipeline", styles["TableHeader"]),
        ],
        [
            Paragraph("<b>GlucoBench (Dubosson)</b>", styles["TableCellBold"]),
            Paragraph("9 T1D patients with continuous CGM, insulin bolus/basal, HR, and accelerometer.", styles["TableCell"]),
            Paragraph("Calibrates post-meal spike kinetics, exercise dips, and physiological insulin modeling.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>GlucoBench (Hall et al.)</b>", styles["TableCellBold"]),
            Paragraph("57 individuals (healthy, prediabetic, diabetic) over longitudinal periods.", styles["TableCell"]),
            Paragraph("Establishes glucotype subclassification and personalized food response variations.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>MIMIC-IV Clinical Demo</b>", styles["TableCellBold"]),
            Paragraph("100 intensive care patients, 107,000 lab events with reference intervals.", styles["TableCell"]),
            Paragraph("Powers the RAG diagnostic interpreter for blood work (lipid profiles, metabolic panels).", styles["TableCell"]),
        ],
    ]
    ds_table = Table(ds_data, colWidths=[2.0 * inch, 2.5 * inch, 2.5 * inch])
    ds_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(ds_table)
    story.append(Spacer(1, 10))

    # ── SECTION 5: LIVE DEMONSTRATION & PROTOTYPE PLAN ─────────────────────────
    story.append(Paragraph("5. Live Demonstration Plan (3-Minute Presentation)", styles["H1_Custom"]))
    story.append(
        Paragraph(
            "All functional components are operational locally without cloud or API dependencies:",
            styles["Body_Custom"],
        )
    )

    demo_data = [
        [
            Paragraph("Timing", styles["TableHeader"]),
            Paragraph("Stage & Live Demo Endpoint", styles["TableHeader"]),
            Paragraph("Key Action & Narrative Flow", styles["TableHeader"]),
        ],
        [
            Paragraph("<b>0:00 – 0:30</b>", styles["TableCellBold"]),
            Paragraph("Problem & Ramesh Persona", styles["TableCell"]),
            Paragraph("Introduce Ramesh (45, T2D, Kathmandu) managing 4 fragmented apps. Hook the judges.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>0:30 – 1:15</b>", styles["TableCellBold"]),
            Paragraph("Food Scanner & Gemma 4<br/><code>localhost:3000</code>", styles["TableCell"]),
            Paragraph("Photograph meal (dal, rice, roti). AI predicts +38 mg/dL spike in 60m and recommends a 15-min walk.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>1:15 – 2:05</b>", styles["TableCellBold"]),
            Paragraph("<b>SF-LG Smartwatch Demo</b><br/><code>localhost:3001</code>", styles["TableCellBold"]),
            Paragraph("Demonstrate greedy space allocation on the circular screen. Click 'Simulate 15-min Walk' — watch curve flatten in real time.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>2:05 – 2:35</b>", styles["TableCellBold"]),
            Paragraph("Clinical Protocols (S1 & S2)<br/><code>localhost:3001</code>", styles["TableCell"]),
            Paragraph("Showcase correlated Heart Rate + IOB on point tap; expand 'Rule of 15' rescue card for rapid drops.", styles["TableCell"]),
        ],
        [
            Paragraph("<b>2:35 – 3:00</b>", styles["TableCellBold"]),
            Paragraph("FHIR QR Share & Conclusion<br/><code>localhost:8000/docs</code>", styles["TableCell"]),
            Paragraph("Generate 10-second FHIR QR code for doctor appointments. Zero new hardware. One unified companion.", styles["TableCell"]),
        ],
    ]
    demo_table = Table(demo_data, colWidths=[1.1 * inch, 2.5 * inch, 3.4 * inch])
    demo_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(demo_table)
    story.append(Spacer(1, 12))

    # ── SECTION 6: IMPLEMENTATION ROADMAP ──────────────────────────────────────
    story.append(Paragraph("6. Implementation Roadmap & Feasibility", styles["H1_Custom"]))
    roadmap_data = [
        [
            Paragraph("<b>Phase</b>", styles["TableHeader"]),
            Paragraph("<b>Milestones Achieved / Targeted</b>", styles["TableHeader"]),
            Paragraph("<b>Target Horizon</b>", styles["TableHeader"]),
        ],
        [
            Paragraph("<b>Hackathon MVP</b>", styles["TableCellBold"]),
            Paragraph("• Working SF-LG Smartwatch engine with dynamic spike blunting<br/>• FastAPI backend with 9,900+ seeded records<br/>• Next.js dashboard & Gemma 4 RAG pipeline", styles["TableCell"]),
            Paragraph("<font color='#059669'><b>Completed</b></font>", styles["TableCellBold"]),
        ],
        [
            Paragraph("<b>Clinical V1</b>", styles["TableCellBold"]),
            Paragraph("• Direct BLE GATT integration for Dexcom G6/G7 and FreeStyle Libre<br/>• HealthKit/WearOS on-device native bridge<br/>• PaddleOCR blood report batch importer", styles["TableCell"]),
            Paragraph("Months 1 – 3", styles["TableCell"]),
        ],
        [
            Paragraph("<b>Scale & Systems</b>", styles["TableCellBold"]),
            Paragraph("• Multi-language localization (Nepali, Hindi, Spanish)<br/>• EHR integration via SMART on FHIR<br/>• Prospective clinical trial measuring TIR improvement", styles["TableCell"]),
            Paragraph("Months 4 – 12", styles["TableCell"]),
        ],
    ]
    roadmap_table = Table(roadmap_data, colWidths=[1.4 * inch, 4.3 * inch, 1.3 * inch])
    roadmap_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(roadmap_table)

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated: {filename}")


if __name__ == "__main__":
    output_path = os.path.abspath("Glymmy_Hackathon_Proposal.pdf")
    build_pdf(output_path)

