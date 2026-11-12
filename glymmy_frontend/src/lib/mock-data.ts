// Mock API for standalone development when backend is not running.
// Toggle via NEXT_PUBLIC_MOCK_API=true

import type {
  ChatResponse,
  FoodAnalysisResponse,
  GlucoseSeriesResponse,
  HealthStatus,
  LabEventsResponse,
  LabInterpretation,
  PatientListResponse,
  SpikePredictionRequest,
  SpikePredictionResponse,
} from "./api-types";

export function isMockMode(): boolean {
  return process.env.NEXT_PUBLIC_MOCK_API === "true";
}

export const mockApi = {
  async health(): Promise<HealthStatus> {
    return {
      status: "ok",
      app: "Glymmy API (mock)",
      version: "0.1.0",
      providers: {
        llm: "ollama_gemma:gemma4:e4b",
        cgm: "glucobench",
        labs: "mimic-iv-demo",
        storage: "memory",
      },
    };
  },
  patients: {
    async list(): Promise<PatientListResponse> {
      return {
        patients: [
          {
            id: "dubosson_1.0",
            source: "dubosson",
            dataset: "GlucoBench/Dubosson",
            name: "T1D Patient 1",
            diagnosis: "Type 1 Diabetes",
            num_readings: 1413,
          },
          {
            id: "dubosson_2.0",
            source: "dubosson",
            dataset: "GlucoBench/Dubosson",
            name: "T1D Patient 2",
            diagnosis: "Type 1 Diabetes",
            num_readings: 1520,
          },
          {
            id: "mimic_10014354",
            source: "mimic",
            dataset: "MIMIC-IV Demo",
            name: "Patient 10014354",
            diagnosis: "Hospital patient",
            num_lab_events: 842,
            num_abnormal: 312,
          },
          {
            id: "hall_1636-69-032",
            source: "hall",
            dataset: "GlucoBench/Hall",
            name: "Hall Patient 1636-69-0",
            diagnosis: "Prediabetic",
            age: 52,
            bmi: 27.4,
            a1c: 6.1,
          },
        ],
        total: 4,
      };
    },
    async profile(id: string) {
      return { patient: { id, name: id }, glucose_summary: null };
    },
    async qr(id: string) {
      return { patient_id: id, qr_data_url: "", fhir_bundle: {} };
    },
  },
  glucose: {
    async series(patientId: string): Promise<GlucoseSeriesResponse> {
      const now = Date.now();
      const readings = Array.from({ length: 144 }, (_, i) => ({
        timestamp: new Date(now - (144 - i) * 10 * 60 * 1000).toISOString(),
        glucose_mg_dl:
          110 +
          35 * Math.sin(i / 8) +
          (i % 20 === 0 ? 45 : 0) +
          (Math.random() - 0.5) * 10,
      }));
      return {
        patient_id: patientId,
        summary: {
          count: readings.length,
          mean: 118.2,
          min: 72,
          max: 198,
          time_in_range_pct: 78.3,
          last_reading: readings[readings.length - 1].glucose_mg_dl,
          last_reading_at: readings[readings.length - 1].timestamp,
        },
        readings,
      };
    },
    async predict(body: SpikePredictionRequest): Promise<SpikePredictionResponse> {
      const net = Math.max(0, body.meal.carbs_g - body.meal.fiber_g);
      const spike = Math.round(net * 0.55 * 10) / 10;
      return {
        predicted_spike_mg_dl: spike,
        net_carbs_g: net,
        time_to_peak_min: 75,
        with_walk_spike_mg_dl: Math.round(spike * 0.75 * 10) / 10,
        risk: spike > 40 ? "high" : spike > 25 ? "moderate" : "low",
        explanation: `${net}g net carbs × 0.55 sensitivity. A 15-min walk cuts peak by 25%.`,
      };
    },
    async hypoCheck(patientId: string) {
      return {
        patient_id: patientId,
        hypo_events: 2,
        critical_events: 0,
        last_event: null,
        alert_level: "low",
      };
    },
  },
  food: {
    async scan(): Promise<FoodAnalysisResponse> {
      return {
        items: [
          { name: "Yellow Dal", portion: "1 bowl", calories: 198, carbs_g: 34, protein_g: 14, fat_g: 1.2, fiber_g: 8 },
          { name: "White Rice", portion: "1.5 cups", calories: 309, carbs_g: 67.5, protein_g: 6.5, fat_g: 0.6, fiber_g: 0.9 },
          { name: "Roti", portion: "2 pieces", calories: 208, carbs_g: 36, protein_g: 7, fat_g: 5, fiber_g: 5 },
        ],
        total: { calories: 715, carbs_g: 137.5, protein_g: 27.5, fat_g: 6.8, fiber_g: 13.9 },
        glucose_prediction: {
          predicted_spike_mg_dl: 58.2,
          net_carbs_g: 123.6,
          time_to_peak_min: 75,
          with_walk_spike_mg_dl: 43.6,
          risk: "high",
          explanation: "High-carb meal. A 15-min walk reduces peak by 25%.",
        },
        source: "mock",
      };
    },
  },
  labs: {
    async list(patientId: string): Promise<LabEventsResponse> {
      const events = [
        { test: "Glucose", value: 142, unit: "mg/dL", ref_low: 70, ref_high: 100, flag: "abnormal", charttime: new Date().toISOString() },
        { test: "Creatinine", value: 1.1, unit: "mg/dL", ref_low: 0.7, ref_high: 1.3, flag: "normal", charttime: new Date().toISOString() },
        { test: "Hemoglobin", value: 11.8, unit: "g/dL", ref_low: 13.5, ref_high: 17.5, flag: "abnormal", charttime: new Date().toISOString() },
        { test: "Potassium", value: 4.2, unit: "mEq/L", ref_low: 3.5, ref_high: 5.0, flag: "normal", charttime: new Date().toISOString() },
        { test: "Sodium", value: 138, unit: "mEq/L", ref_low: 136, ref_high: 145, flag: "normal", charttime: new Date().toISOString() },
        { test: "White Blood Cells", value: 12.4, unit: "K/uL", ref_low: 4.5, ref_high: 11.0, flag: "abnormal", charttime: new Date().toISOString() },
      ];
      return { patient_id: patientId, events, total: events.length };
    },
    async interpret(patientId: string): Promise<LabInterpretation> {
      return {
        patient_id: patientId,
        summary: "Reviewed 6 unique tests; flagged 3 as abnormal.",
        abnormal_markers: [
          {
            test: "Glucose",
            value: 142,
            unit: "mg/dL",
            normal_range: "70-100",
            status: "HIGH",
            severity: "moderate",
            explanation: "Elevated fasting glucose — may indicate prediabetes or diabetes if persistent.",
            actions: ["Reduce refined carb intake", "Increase daily activity", "Schedule HbA1c test"],
          },
          {
            test: "Hemoglobin",
            value: 11.8,
            unit: "g/dL",
            normal_range: "13.5-17.5",
            status: "LOW",
            severity: "mild",
            explanation: "Low hemoglobin indicates anemia — reduced oxygen-carrying capacity.",
            actions: ["Eat iron-rich foods", "Check iron, B12, and folate levels"],
          },
        ],
        risk_assessment: {
          diabetes_risk: "high",
          cardiovascular_risk: "moderate",
          liver_risk: "low",
          kidney_risk: "low",
        },
        recommendations: [
          "Discuss abnormal values with your primary care doctor.",
          "Re-test flagged markers in 4–6 weeks.",
          "Keep a consistent diet and activity log in Glymmy.",
        ],
        follow_up: "Re-check abnormal markers in 4–6 weeks unless otherwise advised.",
      };
    },
  },
  wearables: {
    async get(patientId: string) {
      return { patient_id: patientId, heart_rate: [], activity: [], insulin: [], source: "mock" };
    },
  },
  chat: {
    async send(message: string): Promise<ChatResponse> {
      return {
        response: `Hi! I'm Glymmy running in mock mode. You asked: "${message}". In real mode, I'd use your patient context plus medical knowledge via RAG to give you a personalized answer. Always consult a doctor for medical decisions.`,
        sources: [
          { title: "Glucose Spikes and Meal Composition", source: "clinical-reference", score: 0.87 },
          { title: "Type 2 Diabetes Basics", source: "clinical-reference", score: 0.74 },
        ],
      };
    },
  },
};
