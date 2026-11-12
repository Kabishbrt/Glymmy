export interface Device {
  id: string;
  user_id: string;
  type: "cgm" | "smartwatch" | "heart_rate_monitor" | "activity_tracker";
  vendor:
    | "dexcom"
    | "libre"
    | "apple_watch"
    | "garmin"
    | "fitbit"
    | "oura"
    | "whoop";
  model?: string | null;
  paired_at: string;
}

export interface UserProfile {
  id: string;
  name: string;
  email?: string | null;
  age?: number | null;
  weight_kg?: number | null;
  height_cm?: number | null;
  diagnosis?: string | null;
  a1c?: number | null;
  created_at: string;
  devices: Device[];
}

export interface FoodAnalysisResponse {
  items: Array<{
    name: string;
    portion: string;
    calories: number;
    carbs_g: number;
    protein_g: number;
    fat_g: number;
    fiber_g: number;
  }>;
  total: {
    calories: number;
    carbs_g: number;
    protein_g: number;
    fat_g: number;
    fiber_g: number;
  };
  glucose_prediction: {
    predicted_spike_mg_dl: number;
    net_carbs_g: number;
    time_to_peak_min: number;
    with_walk_spike_mg_dl: number;
    risk: "low" | "moderate" | "high";
    explanation: string;
  };
  source: string;
}

export interface WearableReading {
  timestamp: string;
  glucose_mg_dl?: number;
  trend?: string;
  heart_rate_bpm?: number;
  steps?: number;
  spo2_pct?: number;
}

export interface DeviceReadingsResponse {
  device: Device;
  readings: WearableReading[];
  count: number;
}

export interface UserWearablesResponse {
  user_id: string;
  devices: DeviceReadingsResponse[];
}

export interface LatestCgmResponse {
  user_id: string;
  device_id: string;
  latest_reading: {
    timestamp: string;
    glucose_mg_dl: number;
    trend?: string | null;
  };
}

export interface LabEventsResponse {
  patient_id: string;
  events: Array<{
    test: string;
    value?: number | null;
    raw_value?: string | null;
    unit?: string | null;
    ref_low?: number | null;
    ref_high?: number | null;
    flag: string;
    charttime?: string | null;
  }>;
  total: number;
}

export interface LabInterpretation {
  patient_id: string;
  summary: string;
  abnormal_markers: Array<{
    test: string;
    value: number;
    unit?: string | null;
    normal_range: string;
    status: string;
    severity: string;
    explanation: string;
    actions: string[];
  }>;
  risk_assessment: {
    diabetes_risk: string;
    cardiovascular_risk: string;
    liver_risk: string;
    kidney_risk: string;
  };
  recommendations: string[];
  follow_up: string;
}

export interface ChatResponse {
  response: string;
  sources: Array<{
    title: string;
    source: string;
    score?: number | null;
  }>;
}
