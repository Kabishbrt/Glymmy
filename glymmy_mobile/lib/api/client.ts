import Constants from "expo-constants";

import type {
  ChatResponse,
  FoodAnalysisResponse,
  LabEventsResponse,
  LabInterpretation,
  LatestCgmResponse,
  UserProfile,
  UserWearablesResponse,
} from "@/lib/api/types";

const extra =
  (Constants.expoConfig?.extra as Record<string, string | undefined> | undefined) || {};

export const API_URL =
  process.env.EXPO_PUBLIC_API_URL ||
  extra.EXPO_PUBLIC_API_URL ||
  "http://localhost:8000";

export const isDemoMode = () =>
  (process.env.EXPO_PUBLIC_ENABLE_DEMO_MODE || extra.EXPO_PUBLIC_ENABLE_DEMO_MODE || "true") !==
  "false";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }

  return res.json() as Promise<T>;
}

export const api = {
  me: {
    profile: () => request<UserProfile>("/api/v1/users/me"),
    devices: () => request<UserProfile["devices"]>("/api/v1/users/me/devices"),
    latestCgm: () => request<LatestCgmResponse>("/api/v1/users/me/cgm/latest"),
    wearables: (limit = 288) =>
      request<UserWearablesResponse>(`/api/v1/users/me/wearables?limit=${limit}`),
  },
  food: {
    analyzeText: (description: string) =>
      request<FoodAnalysisResponse>("/api/v1/food/analyze-text", {
        method: "POST",
        body: JSON.stringify({ description }),
      }),
  },
  labs: {
    list: (patientId: string) =>
      request<LabEventsResponse>(`/api/v1/labs/${patientId}?limit=20`),
    interpret: (patientId: string) =>
      request<LabInterpretation>(`/api/v1/labs/${patientId}/interpret`, {
        method: "POST",
      }),
  },
  chat: {
    send: (message: string, patientId?: string | null) =>
      request<ChatResponse>("/api/v1/chat", {
        method: "POST",
        body: JSON.stringify({ patient_id: patientId ?? null, message, history: [] }),
      }),
  },
};
