import { useEffect, useState } from "react";
import { ActivityIndicator, RefreshControl, StyleSheet, Text, View } from "react-native";

import { Card } from "@/components/card";
import { MetricChip } from "@/components/metric-chip";
import { Screen } from "@/components/screen";
import { api } from "@/lib/api/client";
import type { LatestCgmResponse, UserProfile } from "@/lib/api/types";
import { colors } from "@/lib/theme";

export default function NowScreen() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [latest, setLatest] = useState<LatestCgmResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    try {
      setError(null);
      const [user, cgm] = await Promise.all([
        api.me.profile(),
        api.me.latestCgm().catch(() => null),
      ]);
      setProfile(user);
      setLatest(cgm);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load data.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  const glucose = latest?.latest_reading.glucose_mg_dl;
  const riskTone =
    glucose == null
      ? "neutral"
      : glucose < 70
        ? "danger"
        : glucose > 180
          ? "warning"
          : "success";

  return (
    <Screen
      title="Now"
      subtitle="Your mobile home should answer what is happening now, whether it is risky, and what to do next."
      scrollProps={{
        refreshControl: (
          <RefreshControl
            refreshing={refreshing}
            onRefresh={() => {
              setRefreshing(true);
              void load();
            }}
          />
        ),
      }}
    >
      <View style={styles.fill}>
        {loading ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color={colors.primary} />
          </View>
        ) : error ? (
          <Card title="Backend connection needed" subtitle={error}>
            <Text style={styles.body}>
              Start the FastAPI backend and make sure `EXPO_PUBLIC_API_URL` points at it.
            </Text>
          </Card>
        ) : (
          <View style={styles.content}>
            <Card title={`Hi, ${profile?.name ?? "there"}`}>
              <Text style={styles.heroValue}>
                {glucose != null ? `${Math.round(glucose)} mg/dL` : "No CGM paired"}
              </Text>
              <Text style={styles.heroMeta}>
                {latest?.latest_reading.trend
                  ? `Trend: ${latest.latest_reading.trend}`
                  : "Pair or sync a CGM to unlock live glucose."}
              </Text>
            </Card>

            <View style={styles.row}>
              <MetricChip
                label="Status"
                value={
                  glucose == null
                    ? "Pending"
                    : glucose < 70
                      ? "Low"
                      : glucose > 180
                        ? "Elevated"
                        : "In range"
                }
                tone={riskTone}
              />
              <MetricChip
                label="Diagnosis"
                value={profile?.diagnosis || "Not set"}
                tone="primary"
              />
            </View>

            <Card
              title="What to do next"
              subtitle="This is the core product voice for mobile: calm, clear, and actionable."
            >
              <Text style={styles.body}>
                {glucose == null
                  ? "Start in demo mode, pair a device, or sync HealthKit/Google Fit later."
                  : glucose < 70
                    ? "Treat a low first. Show fast-acting carbs, time since last meal, and a quick prompt to retest."
                    : glucose > 180
                      ? "Suggest a short walk, hydration, and checking the recent meal."
                      : "Reinforce stability and offer fast actions like log meal, ask Glymmy, or view trends."}
              </Text>
            </Card>

            <Card title="V1 notes">
              <Text style={styles.body}>
                The backend already exposes `/users/me/cgm/latest` and a foreground SSE alert stream.
                This screen should become the app&apos;s primary patient loop.
              </Text>
            </Card>
          </View>
        )}
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  fill: {
    flex: 1,
  },
  center: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
  },
  content: {
    gap: 16,
  },
  row: {
    flexDirection: "row",
    gap: 12,
  },
  heroValue: {
    fontSize: 38,
    fontWeight: "900",
    color: colors.text,
  },
  heroMeta: {
    fontSize: 15,
    color: colors.textMuted,
  },
  body: {
    fontSize: 15,
    lineHeight: 22,
    color: colors.textMuted,
  },
});
