// TypeScript types mirroring the backend Pydantic schemas.

export interface Patient {
  id: string;
  source: string;
  dataset?: string | null;
  name: string;
  diagnosis?: string | null;
  age?: number | null;
  bmi?: number | null;
  a1c?: number | null;
  num_readings?: number | null;
  num_lab_events?: number | null;
  num_abnormal?: number | null;
}

export interface PatientListResponse {
  patients: Patient[];
  total: number;
}

export interface GlucoseReading {
  timestamp: string;
  glucose_mg_dl: number;
  heart_rate?: number | null;
  activity?: number | null;
}

export interface GlucoseSummary {
  count: number;
  mean: number;
  min: number;
  max: number;
  time_in_range_pct: number;
  last_reading?: number | null;
  last_reading_at?: string | null;
}

export interface GlucoseSeriesResponse {
  patient_id: string;
  summary: GlucoseSummary;
  readings: GlucoseReading[];
}

export interface MealInput {
  carbs_g: number;
  protein_g: number;
  fat_g: number;
  fiber_g: number;
}

export interface SpikePredictionRequest {
  patient_id: string;
  meal: MealInput;
  pre_meal_glucose?: number | null;
}

export interface SpikePredictionResponse {
  predicted_spike_mg_dl: number;
  net_carbs_g: number;
  time_to_peak_min: number;
  with_walk_spike_mg_dl: number;
  risk: "low" | "moderate" | "high";
  explanation: string;
}

export interface FoodItem {
  name: string;
  portion: string;
  calories: number;
  carbs_g: number;
  protein_g: number;
  fat_g: number;
  fiber_g: number;
}

export interface FoodAnalysisResponse {
  items: FoodItem[];
  total: {
    calories: number;
    carbs_g: number;
    protein_g: number;
    fat_g: number;
    fiber_g: number;
  };
  glucose_prediction: SpikePredictionResponse;
  source: string;
}

export interface LabEvent {
  test: string;
  category?: string | null;
  value?: number | null;
  raw_value?: string | null;
  unit?: string | null;
  ref_low?: number | null;
  ref_high?: number | null;
  flag: string;
  charttime?: string | null;
}

export interface LabEventsResponse {
  patient_id: string;
  events: LabEvent[];
  total: number;
}

export interface AbnormalMarker {
  test: string;
  value: number;
  unit?: string | null;
  normal_range: string;
  status: string;
  severity: string;
  explanation: string;
  actions: string[];
}

export interface LabInterpretation {
  patient_id: string;
  summary: string;
  abnormal_markers: AbnormalMarker[];
  risk_assessment: {
    diabetes_risk: string;
    cardiovascular_risk: string;
    liver_risk: string;
    kidney_risk: string;
  };
  recommendations: string[];
  follow_up: string;
}

export interface ChatSource {
  title: string;
  source: string;
  score?: number | null;
}

export interface ChatResponse {
  response: string;
  sources: ChatSource[];
}

export interface HealthStatus {
  status: string;
  app: string;
  version: string;
  providers: {
    llm: string;
    cgm: string;
    labs: string;
    storage: string;
  };
}

// ── User & device types (from /users/me endpoints) ──────────────────────────

export type DeviceType = "cgm" | "smartwatch" | "heart_rate_monitor" | "activity_tracker";
export type DeviceVendor = "dexcom" | "libre" | "apple_watch" | "garmin" | "fitbit" | "oura" | "whoop";

export interface Device {
  id: string;
  user_id: string;
  type: DeviceType;
  vendor: DeviceVendor;
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

export interface CGMReading {
  timestamp: string;
  glucose_mg_dl: number;
  trend?: string | null;
}

export interface SmartwatchReading {
  timestamp: string;
  heart_rate_bpm?: number | null;
  spo2_pct?: number | null;
  steps?: number | null;
  calories_burned?: number | null;
  sleep_stage?: string | null;
  skin_temp_c?: number | null;
}

export interface HeartRateMonitorReading {
  timestamp: string;
  heart_rate_bpm: number;
  hrv_ms?: number | null;
  rr_interval_ms?: number | null;
}

export interface ActivityTrackerReading {
  timestamp: string;
  steps: number;
  distance_m: number;
  calories_burned: number;
  active_minutes: number;
  floors_climbed: number;
}

export type WearableReading =
  | CGMReading
  | SmartwatchReading
  | HeartRateMonitorReading
  | ActivityTrackerReading;

export interface DeviceReadingsResponse {
  device: Device;
  readings: WearableReading[];
  count: number;
}

export interface UserWearablesResponse {
  user_id: string;
  devices: DeviceReadingsResponse[];
}

export interface AlertEvent {
  type: "hypo_warning" | "hypo_critical" | "hyper_warning" | "hyper_critical";
  severity: "moderate" | "high" | "critical";
  message: string;
  glucose_mg_dl: number;
  timestamp: string;
}

export interface ReadingEvent {
  type: "reading";
  timestamp: string;
  glucose_mg_dl: number;
  trend: string;
  device_id: string;
}

// ── Notification types ────────────────────────────────────────────────────────

export type NotificationType =
  | "hypo_critical"
  | "hypo_warning"
  | "hyper_critical"
  | "hyper_warning"
  | "prolonged_high"
  | "rapid_drop";

export interface Notification {
  id: string;
  type: NotificationType;
  severity: "critical" | "high" | "moderate";
  title: string;
  message: string;
  voice_text: string;
  glucose_mg_dl: number;
  timestamp: string;
  acknowledged: boolean;
  snoozed_until?: string | null;
}

export interface NotificationResponse {
  notifications: Notification[];
  has_critical: boolean;
  user_name: string;
}

// ── Reminder types ────────────────────────────────────────────────────────────

export type ReminderType =
  | "a1c_recheck"
  | "lipid_panel"
  | "eye_exam"
  | "foot_exam"
  | "kidney_function"
  | "blood_pressure"
  | "dental"
  | "general_checkup";

export interface Reminder {
  id: string;
  type: ReminderType;
  title: string;
  message: string;
  priority: "high" | "medium" | "low";
  due_context: string;
  dismissed: boolean;
  snoozed_until?: string | null;
}

export interface RemindersResponse {
  reminders: Reminder[];
  generated_at: string;
  user_name: string;
}

// ── Scan / OCR types ──────────────────────────────────────────────────────────

export type DocumentType = "lab_report" | "prescription" | "food_label" | "general";

export interface ExtractedField {
  key: string;
  value: string;
  unit?: string | null;
  reference_range?: string | null;
  flag?: string | null;
}

export interface LabReportResult {
  patient_name?: string | null;
  date?: string | null;
  lab_name?: string | null;
  tests: ExtractedField[];
  summary: string;
}

export interface PrescriptionResult {
  patient_name?: string | null;
  doctor_name?: string | null;
  date?: string | null;
  medications: Array<{
    name: string;
    dosage: string;
    frequency: string;
    duration: string;
  }>;
  notes?: string | null;
}

export interface FoodLabelResult {
  product_name?: string | null;
  serving_size?: string | null;
  calories?: number | null;
  carbs_g?: number | null;
  sugar_g?: number | null;
  protein_g?: number | null;
  fat_g?: number | null;
  fiber_g?: number | null;
  sodium_mg?: number | null;
  ingredients?: string[] | null;
}

export interface ScanResponse {
  document_type: DocumentType;
  raw_text: string;
  lab_report?: LabReportResult | null;
  prescription?: PrescriptionResult | null;
  food_label?: FoodLabelResult | null;
  confidence: number;
  source: string;
}

// ── Latest CGM response ───────────────────────────────────────────────────────

export interface LatestCgmResponse {
  user_id: string;
  device_id: string;
  latest_reading: CGMReading;
}

// ── Chat history ──────────────────────────────────────────────────────────────

export interface ChatHistoryResponse {
  messages: Array<{ role: string; content: string }>;
  total: number;
}

// ── Health Inventory ──────────────────────────────────────────────────────────

export interface Medication {
  name: string;
  dosage: string;
  frequency: string;
  prescriber?: string;
  start_date?: string;
  notes?: string;
}

export interface AllergyRecord {
  allergen: string;
  reaction: string;
  severity: "mild" | "moderate" | "severe";
}

export interface ConditionRecord {
  name: string;
  diagnosed_date?: string;
  status: "active" | "resolved" | "managed";
  notes?: string;
}

export interface EmergencyContactRecord {
  name: string;
  relationship: string;
  phone: string;
  email?: string;
}

export interface HealthInventory {
  blood_type?: string | null;
  medications: Medication[];
  allergies: AllergyRecord[];
  conditions: ConditionRecord[];
  emergency_contacts: EmergencyContactRecord[];
  insurance_provider?: string | null;
  insurance_id?: string | null;
  primary_physician?: string | null;
  notes?: string | null;
}

// ── Task queue ────────────────────────────────────────────────────────────────

export interface TaskResponse {
  task_id: string;
  status: "pending" | "processing" | "completed" | "failed";
  created_at: string;
  completed_at?: string | null;
  result?: unknown;
  error?: string | null;
}

// ── Share / QR ────────────────────────────────────────────────────────────────

export interface ShareConfig {
  include_profile?: boolean;
  include_glucose?: boolean;
  include_vitals?: boolean;
  include_medications?: boolean;
  include_conditions?: boolean;
}

export interface ShareResponse {
  share_token: string;
  share_url: string;
  qr_data_url: string;
  created_at: string;
}

export interface SharedData {
  user_name: string;
  shared_at: string;
  profile?: Record<string, unknown> | null;
  glucose_summary?: Record<string, unknown> | null;
  vitals?: Record<string, unknown> | null;
  medications?: Medication[] | null;
  conditions?: ConditionRecord[] | null;
}

// ── Saved lab reports ─────────────────────────────────────────────────────────

export interface SavedLabReport {
  report_id: string;
  scanned_at: string;
  document_type: string;
  lab_report?: LabReportResult | null;
  raw_text?: string;
  confidence?: number;
}
