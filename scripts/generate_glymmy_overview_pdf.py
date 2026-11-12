#!/usr/bin/env python3
"""
Generate a clean, publication-grade PDF containing the exact project overview,
architecture diagram, and smartwatch SF-LG feature showcase with embedded images.
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
    Image,
    Preformatted,
    HRFlowable,
    KeepTogether,
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Dynamic two-pass canvas for header, footer, and page numbers."""

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
                45, 11 * inch - 30, "Glymmy — AI Health Platform & Smartwatch SF-LG Interface"
            )
            self.drawRightString(
                8.5 * inch - 45, 11 * inch - 30, "Harvard HSIL Hackathon 2026"
            )
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(45, 11 * inch - 34, 8.5 * inch - 45, 11 * inch - 34)

        # Footer (all pages)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * inch - 45, 26, page_text)
        self.drawString(
            45,
            26,
            "Glymmy Project Overview • Built for Harvard Health Systems Innovation Lab",
        )
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(45, 36, 8.5 * inch - 45, 36)

        self.restoreState()


def build_pdf(filename="Glymmy_Overview_and_Smartwatch_Proposal.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=45,
        rightMargin=45,
        topMargin=44,
        bottomMargin=44,
    )

    styles = getSampleStyleSheet()

    # Brand Colors
    PRIMARY = colors.HexColor("#0F172A")    # Slate 900
    ACCENT = colors.HexColor("#2563EB")     # Blue 600
    ACCENT_LIGHT = colors.HexColor("#EFF6FF")
    SLATE = colors.HexColor("#334155")      # Slate 700
    MUTED = colors.HexColor("#64748B")      # Slate 500
    BORDER = colors.HexColor("#E2E8F0")     # Slate 200

    # Custom Typography
    styles.add(
        ParagraphStyle(
            name="Title_Main",
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=PRIMARY,
            spaceAfter=2,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Subtitle_Main",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=15,
            textColor=ACCENT,
            spaceAfter=2,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Tagline",
            fontName="Helvetica-Oblique",
            fontSize=9.5,
            leading=13,
            textColor=MUTED,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="H2_Section",
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=PRIMARY,
            spaceBefore=11,
            spaceAfter=5,
            keepWithNext=True,
        )
    )
    styles.add(
        ParagraphStyle(
            name="H3_Section",
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=ACCENT,
            spaceBefore=8,
            spaceAfter=4,
            keepWithNext=True,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Body_Text",
            fontName="Helvetica",
            fontSize=8.5,
            leading=12,
            textColor=SLATE,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Caption_Hero",
            fontName="Helvetica-Oblique",
            fontSize=8,
            leading=11,
            textColor=SLATE,
            alignment=1,  # Center
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Caption_Cell",
            fontName="Helvetica",
            fontSize=7.2,
            leading=9.5,
            textColor=SLATE,
            spaceBefore=3,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Header_Cell",
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=colors.white,
            alignment=0,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Grid_Feature",
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=11,
            textColor=PRIMARY,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Grid_Desc",
            fontName="Helvetica",
            fontSize=7.8,
            leading=10.5,
            textColor=SLATE,
        )
    )
    styles.add(
        ParagraphStyle(
            name="AsciiBlock",
            fontName="Courier",
            fontSize=5.3,
            leading=6.6,
            textColor=colors.HexColor("#1E293B"),
            spaceBefore=2,
            spaceAfter=4,
        )
    )

    story = []

    # ── HEADER & TITLE ──────────────────────────────────────────────────────────
    story.append(Paragraph("Glymmy", styles["Title_Main"]))
    story.append(Paragraph("Your glycemic companion — AI health platform", styles["Subtitle_Main"]))
    story.append(Paragraph("(glycemic + my — a unified health data platform)", styles["Tagline"]))
    story.append(
        Paragraph(
            "Glymmy connects CGM, wearables, food photos, and lab reports into one AI-powered health companion. "
            "It uses the multimodal <b>Gemma 4</b> model to turn raw clinical data into personalized, actionable insights — "
            "running locally by default, with zero paid dependencies.<br/><br/>"
            "<b>Built for the Harvard HSIL Hackathon 2026.</b>",
            styles["Body_Text"],
        )
    )
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceBefore=4, spaceAfter=8))

    # ── WHAT IT DOES TABLE ──────────────────────────────────────────────────────
    story.append(Paragraph("What it does", styles["H2_Section"]))

    features = [
        [
            Paragraph("Feature", styles["Header_Cell"]),
            Paragraph("Description", styles["Header_Cell"]),
        ],
        [
            Paragraph("<b>CGM Dashboard</b>", styles["Grid_Feature"]),
            Paragraph("Real-time glucose time-series, time-in-range (TIR), hypo/hyper alerts", styles["Grid_Desc"]),
        ],
        [
            Paragraph("<b>Smartwatch UI (SF-LG)</b>", styles["Grid_Feature"]),
            Paragraph("Circular 300x300 watch interface with <b>Space-Filling Line Graph (SF-LG)</b> greedy space allocation for post-meal walk advice & vitals", styles["Grid_Desc"]),
        ],
        [
            Paragraph("<b>Food Scanner</b>", styles["Grid_Feature"]),
            Paragraph("Photo or text → full nutrition breakdown + AI post-prandial glucose spike prediction", styles["Grid_Desc"]),
        ],
        [
            Paragraph("<b>Lab Interpreter</b>", styles["Grid_Feature"]),
            Paragraph("AI interpretation of blood reports with risk assessment", styles["Grid_Desc"]),
        ],
        [
            Paragraph("<b>Wearable Sync</b>", styles["Grid_Feature"]),
            Paragraph("CGM, Apple Watch, Garmin HR monitor, Fitbit activity tracker (HR, steps, sleep, SpO2)", styles["Grid_Desc"]),
        ],
        [
            Paragraph("<b>RAG Chat</b>", styles["Grid_Feature"]),
            Paragraph("Ask questions about your health data with cited clinical sources", styles["Grid_Desc"]),
        ],
        [
            Paragraph("<b>FHIR QR Share</b>", styles["Grid_Feature"]),
            Paragraph("Generate a QR code containing a FHIR bundle for doctor visits in 10 seconds", styles["Grid_Desc"]),
        ],
        [
            Paragraph("<b>Real-time Alerts</b>", styles["Grid_Feature"]),
            Paragraph("Multi-level alerts (Rule of 15 rescue protocol) & SSE push notifications", styles["Grid_Desc"]),
        ],
    ]

    features_table = Table(features, colWidths=[1.8 * inch, 5.2 * inch])
    features_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("TOPPADDING", (0, 0), (-1, -1), 3.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
            ]
        )
    )
    story.append(features_table)
    story.append(Spacer(1, 8))

    # ── SYSTEM ARCHITECTURE: BIDIRECTIONAL DATA FLOW ───────────────────────────
    story.append(Paragraph("System Architecture: Bidirectional Data Flow", styles["H2_Section"]))
    story.append(
        Paragraph(
            "Glymmy operates on a closed-loop feedback architecture: devices act as continuous physiological emitters "
            "(<b>Giving Side</b>), while the local AI engine processes correlations and delivers actionable micro-interventions "
            "back to the patient and clinician (<b>Receiving & Acting Side</b>).",
            styles["Body_Text"],
        )
    )

    ascii_arch = """┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                       1. SENSOR & INGESTION LAYER (GIVING / SENSING SIDE)                   │
│                                                                                             │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌────────────────┐ │
│  │    CGM Sensor    │    │ Smartwatch Vitals│    │ Phone Camera/Scan│    │  Blood Reports │ │
│  │ (Dexcom / Libre) │    │ (Apple / Garmin) │    │ (Food Photo/Log) │    │  (Lab PDF/OCR) │ │
│  │  Glucose 5m BLE  │    │  HR, Steps, Temp │    │ Macro Estimation │    │  HbA1c, Lipids │ │
│  └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘    └────────┬───────┘ │
└───────────┼───────────────────────┼───────────────────────┼───────────────────────┼─────────┘
            │                       │                       │                       │
            └───────────────────────┼───────────────────────┴───────────────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                          2. CORE PROCESSING & PREDICTIVE ENGINE                             │
│                     ┌───────────────────────────────────────────────┐                       │
│                     │       FastAPI Backend (:8000)                 │                       │
│                     │  • Time-Series Normalization (Dubosson)       │                       │
│                     │  • Post-Meal Spike Kinetics & Walk Blunting   │                       │
│                     │  • Rule-of-15 Hypo Threshold Engine (SSE)     │                       │
│                     └───────┬───────────────────────────────┬───────┘                       │
│                             │                               │                               │
│              ┌──────────────┴──────────────┐ ┌──────────────┴──────────────┐                │
│              │    Gemma 4 Multimodal LLM   │ │  ChromaDB Vector Store RAG  │                │
│              │   Local Vision & Inference  │ │ Clinical Context Retrieval  │                │
│              └─────────────────────────────┘ └─────────────────────────────┘                │
└─────────────────────────────────────────────┬───────────────────────────────────────────────┘
                                              │
                      ┌───────────────────────┴───────────────────────┐
                      ▼                                               ▼
┌───────────────────────────────────────────┐   ┌───────────────────────────────────────────┐
│  3. REAL-TIME INTERACTION (RECEIVING SIDE)│   │       4. CLINICAL SHARING & DESKTOP       │
│ ┌───────────────────────────────────────┐ │   │ ┌───────────────────────────────────────┐ │
│ │  Smartwatch UI (SF-LG Algorithm)      │ │   │ │  Next.js 16 Web Dashboard (:3000)     │ │
│ │  • Non-occluding Valleys Allocation   │ │   │ │  • Longitudinal Glycemic Analytics    │ │
│ │  • Post-Meal Walk Blunting Advisor    │ │   │ │  • Lab Interpreter & Trend Visuals    │ │
│ │  • Rule of 15 Emergency Hypo Rescue   │ │   │ └───────────────────────────────────────┘ │
│ │  • Correlated Vitals (HR, IOB, TIR)   │ │   │ ┌───────────────────────────────────────┐ │
│ └───────────────────────────────────────┘ │   │ │  Doctor FHIR R4 QR Code Share         │ │
│ ┌───────────────────────────────────────┐ │   │ │  • 10-Second Clinical Handoff         │ │
│ │  Smartphone App (Expo Mobile)         │ │   │ │  • Standardized Unified Health Bundle │ │
│ │  • Instant Push Alerts & Meal Advisor │ │   │ └───────────────────────────────────────┘ │
│ └───────────────────────────────────────┘ │   │                                           │
└───────────────────────────────────────────┘   └───────────────────────────────────────────┘"""

    arch_container = [[Preformatted(ascii_arch, styles["AsciiBlock"])]]
    arch_table = Table(arch_container, colWidths=[doc.width])
    arch_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#CBD5E1")),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(arch_table)
    story.append(Spacer(1, 8))

    # ── SMARTWATCH FEATURE: SF-LG GREEDY SPACE ALLOCATION ──────────────────────
    story.append(Paragraph("Smartwatch Feature: SF-LG Greedy Space Allocation", styles["H2_Section"]))
    story.append(
        Paragraph(
            "Small circular smartwatches (300×300px) present a severe UI challenge: standard cards or overlay "
            "complications occlude the glucose curve or get clipped by circular borders.<br/><br/>"
            "Glymmy implements the <b>SF-LG (Space-Filling Line Graph)</b> algorithm to solve this:<br/>"
            "• <b>Dynamic Valleys Discovery:</b> Scans the active CGM time-series curve to identify empty geometric headroom ('valleys above') and footroom ('valleys below').<br/>"
            "• <b>Greedy Area Allocation:</b> Sorts candidate rectangular pockets by area (width × height) and allocates the largest non-overlapping spaces to contextual micro-widgets.",
            styles["Body_Text"],
        )
    )

    # FIGURE 1: HERO IMAGE
    img_dir = "smart_watch_simulation_image"
    hero_path = os.path.join(img_dir, "meal_spike_and_walk.png")
    if os.path.exists(hero_path):
        hero_img = Image(hero_path, width=2.4 * inch, height=2.3 * inch)
        hero_caption = (
            "<b>Figure 1:</b> The SF-LG algorithm dynamically hosting the Post-Meal Spike & Walk Advisor "
            "in the empty valley above the CGM curve. Centered complications (TIR 84%, 10:09, IOB 1.4U) "
            "contour within the circular bezel."
        )
        hero_box = [
            [hero_img],
            [Paragraph(hero_caption, styles["Caption_Hero"])],
        ]
        hero_table = Table(hero_box, colWidths=[doc.width])
        hero_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]
            )
        )
        story.append(hero_table)
        story.append(Spacer(1, 6))

    # ── INTERACTIVE SMARTWATCH SCENARIOS SHOWCASE ──────────────────────────────
    story.append(Paragraph("Interactive Smartwatch Scenarios Showcase", styles["H2_Section"]))

    # Row 1: S4, S1, S2 (3 items)
    p_meal = os.path.join(img_dir, "meal_spike_and_walk.png")
    p_vitals = os.path.join(img_dir, "vitals.png")
    p_alert = os.path.join(img_dir, "rule_of_15_alert.png")

    def make_cell(img_path, title, caption_text, w=2.1 * inch, h=1.45 * inch):
        elements = [
            Paragraph(f"<b>{title}</b>", styles["Grid_Feature"]),
        ]
        if os.path.exists(img_path):
            elements.append(Image(img_path, width=w, height=h))
        elements.append(Paragraph(caption_text, styles["Caption_Cell"]))
        return elements

    row1 = [
        make_cell(
            p_meal,
            "🥗 S4: Meal Spike & Walk (Signature)",
            "<b>Post-Meal Walk Advisor:</b> Predicts peak (192 mg/dL); tapping <i>Simulate 15-min Walk</i> flattens curve in real time to 138 mg/dL (-25 mg/dL).",
            w=2.0 * inch,
            h=1.5 * inch,
        ),
        make_cell(
            p_vitals,
            "📊 S1: Point Vitals Correlation",
            "<b>Point Vitals:</b> Tap any point to surface correlated Heart Rate (bpm) and active Insulin on Board (IOB) from wearable fusion.",
            w=2.0 * inch,
            h=1.5 * inch,
        ),
        make_cell(
            p_alert,
            "⚠️ S2: Rule of 15 Hypo Protocol",
            "<b>Rule of 15 Rescue:</b> Ambient pulsing alert expands into clinical guidance (eat 15g fast carbs & retest in 15m) with tachycardia monitoring.",
            w=2.0 * inch,
            h=1.5 * inch,
        ),
    ]

    gallery_table_1 = Table([row1], colWidths=[2.33 * inch, 2.33 * inch, 2.34 * inch])
    gallery_table_1.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(gallery_table_1)
    story.append(Spacer(1, 6))

    # Row 2: S3, S5 (2 items)
    p_compare = os.path.join(img_dir, "compare.png")
    p_stream = os.path.join(img_dir, "live_stream.png")

    row2 = [
        make_cell(
            p_compare,
            "⚖️ S3: Comparative Analysis",
            "<b>Comparative Analysis:</b> Tap two points to compare exact glycemic delta (Δ mg/dL) and heart rate variations.",
            w=2.6 * inch,
            h=1.6 * inch,
        ),
        make_cell(
            p_stream,
            "⚡ S5: Live Streaming & Relocation",
            "<b>Live Streaming:</b> Live simulation where widgets smoothly glide and reposition as glycemic peaks and valleys shift.",
            w=2.6 * inch,
            h=1.6 * inch,
        ),
    ]

    gallery_table_2 = Table([row2], colWidths=[3.5 * inch, 3.5 * inch])
    gallery_table_2.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(gallery_table_2)

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated: {filename}")


if __name__ == "__main__":
    out = os.path.abspath("Glymmy_Overview_and_Smartwatch_Proposal.pdf")
    build_pdf(out)
