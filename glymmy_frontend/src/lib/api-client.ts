import type {
  ChatHistoryResponse,
  ChatResponse,
  DeviceReadingsResponse,
  FoodAnalysisResponse,
  GlucoseSeriesResponse,
  HealthInventory,
  HealthStatus,
  LabEventsResponse,
  LabInterpretation,
  LatestCgmResponse,
  NotificationResponse,
  PatientListResponse,
  RemindersResponse,
  SavedLabReport,
  ScanResponse,
  ShareConfig,
  ShareResponse,
  SharedData,
  SpikePredictionRequest,
  SpikePredictionResponse,
  TaskResponse,
  UserProfile,
  UserWearablesResponse,
} from "./api-types";
import { isMockMode, mockApi } from "./mock-data";

const API_URL = process.env.NEXT_PUBLIC_API_URL || (typeof window !== "undefined" ? "" : "http://localhost:8000");

/**
 * Token provider — set by the AuthProvider component so every API call
 * automatically includes the Clerk JWT. When null, requests go without auth.
 */
let _getToken: (() => Promise<string | null>) | null = null;

export function setTokenProvider(fn: () => Promise<string | null>) {
  _getToken = fn;
}

async function authHeaders(): Promise<Record<string, string>> {
  if (!_getToken) return {};
  const token = await _getToken();
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const auth = await authHeaders();
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...auth,
      ...(init?.headers || {}),
    },
    cache: "no-store",
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  health: (): Promise<HealthStatus> =>
    isMockMode() ? mockApi.health() : req<HealthStatus>("/health"),
  patients: {
    list: (): Promise<PatientListResponse> =>
      isMockMode() ? mockApi.patients.list() : req<PatientListResponse>("/api/v1/patients"),
    profile: (id: string) =>
      isMockMode() ? mockApi.patients.profile(id) : req(`/api/v1/patients/${id}/profile`),
    qr: (id: string) =>
      isMockMode() ? mockApi.patients.qr(id) : req(`/api/v1/patients/${id}/qr`),
  },
  glucose: {
    series: (patientId: string, limit = 500): Promise<GlucoseSeriesResponse> =>
      isMockMode()
        ? mockApi.glucose.series(patientId)
        : req<GlucoseSeriesResponse>(`/api/v1/glucose/${patientId}?limit=${limit}`),
    predict: (body: SpikePredictionRequest): Promise<SpikePredictionResponse> =>
      isMockMode()
        ? mockApi.glucose.predict(body)
        : req<SpikePredictionResponse>("/api/v1/glucose/predict", {
            method: "POST",
            body: JSON.stringify(body),
          }),
    hypoCheck: (patientId: string) =>
      isMockMode()
        ? mockApi.glucose.hypoCheck(patientId)
        : req(`/api/v1/glucose/${patientId}/hypo-check`),
  },
  food: {
    scan: async (file: File, patientId?: string): Promise<FoodAnalysisResponse> => {
      if (isMockMode()) return mockApi.food.scan();
      const form = new FormData();
      form.append("image", file);
      if (patientId) form.append("patient_id", patientId);
      const auth = await authHeaders();
      const res = await fetch(`${API_URL}/api/v1/food/scan`, {
        method: "POST",
        body: form,
        headers: { ...auth },
      });
      if (!res.ok) throw new Error(`Food scan failed: ${res.status}`);
      return res.json();
    },
    analyzeText: (description: string, patientId?: string): Promise<FoodAnalysisResponse> =>
      isMockMode()
        ? mockApi.food.scan()
        : req<FoodAnalysisResponse>("/api/v1/food/analyze-text", {
            method: "POST",
            body: JSON.stringify({ description, patient_id: patientId }),
          }),
  },
  labs: {
    list: (patientId: string): Promise<LabEventsResponse> =>
      isMockMode()
        ? mockApi.labs.list(patientId)
        : req<LabEventsResponse>(`/api/v1/labs/${patientId}`),
    interpret: (patientId: string): Promise<LabInterpretation> =>
      isMockMode()
        ? mockApi.labs.interpret(patientId)
        : req<LabInterpretation>(`/api/v1/labs/${patientId}/interpret`, {
            method: "POST",
          }),
  },
  wearables: {
    get: (patientId: string) =>
      isMockMode()
        ? mockApi.wearables.get(patientId)
        : req(`/api/v1/wearables/${patientId}`),
  },
  chat: {
    send: (patientId: string | null, message: string): Promise<ChatResponse> =>
      isMockMode()
        ? mockApi.chat.send(message)
        : req<ChatResponse>("/api/v1/chat", {
            method: "POST",
            body: JSON.stringify({ patient_id: patientId, message, history: [] }),
          }),
  },

  // ── Authenticated /users/me endpoints ──────────────────────────────────
  me: {
    profile: (): Promise<UserProfile> => req<UserProfile>("/api/v1/users/me"),
    update: (body: Record<string, unknown>) =>
      req("/api/v1/users/me", {
        method: "PATCH",
        body: JSON.stringify(body),
      }),
    devices: (): Promise<UserProfile["devices"]> =>
      req<UserProfile["devices"]>("/api/v1/users/me/devices"),
    pairDevice: (body: { type: string; vendor: string; model?: string }) =>
      req("/api/v1/users/me/devices", {
        method: "POST",
        body: JSON.stringify(body),
      }),
    wearables: (params?: {
      device_type?: string;
      limit?: number;
      start?: string;
      end?: string;
    }): Promise<UserWearablesResponse> => {
      const qs = new URLSearchParams();
      if (params?.device_type) qs.set("device_type", params.device_type);
      if (params?.limit) qs.set("limit", String(params.limit));
      if (params?.start) qs.set("start", params.start);
      if (params?.end) qs.set("end", params.end);
      const q = qs.toString() ? `?${qs.toString()}` : "";
      return req<UserWearablesResponse>(`/api/v1/users/me/wearables${q}`);
    },
    deviceReadings: (
      deviceId: string,
      params?: { limit?: number; start?: string; end?: string },
    ): Promise<DeviceReadingsResponse> => {
      const qs = new URLSearchParams();
      if (params?.limit) qs.set("limit", String(params.limit));
      if (params?.start) qs.set("start", params.start);
      if (params?.end) qs.set("end", params.end);
      const q = qs.toString() ? `?${qs.toString()}` : "";
      return req<DeviceReadingsResponse>(
        `/api/v1/users/me/wearables/${deviceId}${q}`,
      );
    },
    ingestReadings: (deviceId: string, readings: Record<string, unknown>[]) =>
      req(`/api/v1/users/me/devices/${deviceId}/readings`, {
        method: "POST",
        body: JSON.stringify(readings),
      }),
    latestCgm: (): Promise<LatestCgmResponse> =>
      req<LatestCgmResponse>("/api/v1/users/me/cgm/latest"),
    notifications: (): Promise<NotificationResponse> =>
      req<NotificationResponse>("/api/v1/users/me/notifications"),
    acknowledgeNotification: (id: string, body: { action: string; snooze_minutes?: number }) =>
      req(`/api/v1/users/me/notifications/${id}/acknowledge`, {
        method: "POST",
        body: JSON.stringify(body),
      }),
    reminders: (): Promise<RemindersResponse> =>
      req<RemindersResponse>("/api/v1/users/me/reminders"),
    dismissReminder: (id: string, body: { action: string; snooze_days?: number }) =>
      req(`/api/v1/users/me/reminders/${id}/dismiss`, {
        method: "POST",
        body: JSON.stringify(body),
      }),
    chatMe: (message: string, history: Array<{ role: string; content: string }> = []): Promise<ChatResponse> =>
      req<ChatResponse>("/api/v1/chat/me", {
        method: "POST",
        body: JSON.stringify({ message, history }),
      }),
    chatHistory: (): Promise<ChatHistoryResponse> =>
      req<ChatHistoryResponse>("/api/v1/chat/me/history"),
    clearChatHistory: () =>
      req("/api/v1/chat/me/history", { method: "DELETE" }),
    inventory: (): Promise<HealthInventory> =>
      req<HealthInventory>("/api/v1/users/me/inventory"),
    updateInventory: (data: Partial<HealthInventory>) =>
      req("/api/v1/users/me/inventory", {
        method: "PATCH",
        body: JSON.stringify(data),
      }),
    addInventoryItem: (category: string, item: Record<string, unknown>) =>
      req(`/api/v1/users/me/inventory/${category}`, {
        method: "POST",
        body: JSON.stringify(item),
      }),
    removeInventoryItem: (category: string, index: number) =>
      req(`/api/v1/users/me/inventory/${category}/${index}`, {
        method: "DELETE",
      }),
    createShare: (config: ShareConfig): Promise<ShareResponse> =>
      req<ShareResponse>("/api/v1/users/me/share", {
        method: "POST",
        body: JSON.stringify(config),
      }),
    uploadLabReport: async (file: File): Promise<SavedLabReport> => {
      const form = new FormData();
      form.append("image", file);
      const auth = await authHeaders();
      const res = await fetch(`${API_URL}/api/v1/users/me/lab-reports`, {
        method: "POST",
        body: form,
        headers: { ...auth },
      });
      if (!res.ok) throw new Error(`Lab report upload failed: ${res.status}`);
      return res.json();
    },
    labReports: (): Promise<SavedLabReport[]> =>
      req<SavedLabReport[]>("/api/v1/users/me/lab-reports"),
    alertStream: (): EventSource => {
      return new EventSource(`${API_URL}/api/v1/users/me/alerts/stream`);
    },
  },

  // ── Share (public) ────────────────────────────────────────────────────
  share: {
    getData: (token: string): Promise<SharedData> =>
      req<SharedData>(`/api/v1/share/${token}`),
  },

  // ── Task queue ────────────────────────────────────────────────────────
  tasks: {
    submitFoodPredict: async (file?: File, description?: string): Promise<{ task_id: string }> => {
      const form = new FormData();
      if (file) form.append("image", file);
      if (description) form.append("description", description);
      const auth = await authHeaders();
      const res = await fetch(`${API_URL}/api/v1/tasks/food-predict`, {
        method: "POST",
        body: form,
        headers: { ...auth },
      });
      if (!res.ok) throw new Error(`Task submit failed: ${res.status}`);
      return res.json();
    },
    getStatus: (taskId: string): Promise<TaskResponse> =>
      req<TaskResponse>(`/api/v1/tasks/${taskId}`),
  },

  // ── Document scan endpoints ───────────────────────────────────────────
  scan: {
    auto: async (file: File): Promise<ScanResponse> => {
      const form = new FormData();
      form.append("image", file);
      const auth = await authHeaders();
      const res = await fetch(`${API_URL}/api/v1/scan`, {
        method: "POST",
        body: form,
        headers: { ...auth },
      });
      if (!res.ok) throw new Error(`Scan failed: ${res.status}`);
      return res.json();
    },
    labReport: async (file: File): Promise<ScanResponse> => {
      const form = new FormData();
      form.append("image", file);
      const auth = await authHeaders();
      const res = await fetch(`${API_URL}/api/v1/scan/lab-report`, {
        method: "POST",
        body: form,
        headers: { ...auth },
      });
      if (!res.ok) throw new Error(`Lab report scan failed: ${res.status}`);
      return res.json();
    },
    prescription: async (file: File): Promise<ScanResponse> => {
      const form = new FormData();
      form.append("image", file);
      const auth = await authHeaders();
      const res = await fetch(`${API_URL}/api/v1/scan/prescription`, {
        method: "POST",
        body: form,
        headers: { ...auth },
      });
      if (!res.ok) throw new Error(`Prescription scan failed: ${res.status}`);
      return res.json();
    },
    foodLabel: async (file: File): Promise<ScanResponse> => {
      const form = new FormData();
      form.append("image", file);
      const auth = await authHeaders();
      const res = await fetch(`${API_URL}/api/v1/scan/food-label`, {
        method: "POST",
        body: form,
        headers: { ...auth },
      });
      if (!res.ok) throw new Error(`Food label scan failed: ${res.status}`);
      return res.json();
    },
  },
};
