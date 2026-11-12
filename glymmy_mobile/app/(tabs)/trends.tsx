import { useEffect, useMemo, useState } from "react";
import { ActivityIndicator, StyleSheet, Text, View } from "react-native";

import { Card } from "@/components/card";
import { MetricChip } from "@/components/metric-chip";
import { Screen } from "@/components/screen";
import { api } from "@/lib/api/client";
import type { DeviceReadingsResponse } from "@/lib/api/types";
import { colors } from "@/lib/theme";

export default function TrendsScreen() {
  const [devices, setDevices] = useState<DeviceReadingsResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    api.me
      .wearables(288)
      .then((res) => {
        if (mounted) setDevices(res.devices);
      })
      .catch((err) => {
        if (mounted) setError(err instanceof Error ? err.message : "Unable to load trends.");
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  const cgm = devices.find((device) => device.device.type === "cgm");
  const glucoseValues = useMemo(
    () =>
      (cgm?.readings || [])
        .map((reading) => reading.glucose_mg_dl)
        .filter((value): value is number => typeof value === "number"),
    [cgm],
  );

  const mean =
    glucoseValues.length > 0
      ? Math.round(glucoseValues.reduce((sum, value) => sum + value, 0) / glucoseValues.length)
      : null;
  const inRange =
    glucoseValues.length > 0
      ? Math.round(
          (glucoseValues.filter((value) => value >= 70 && value <= 180).length /
            glucoseValues.length) *
            100,
        )
      : null;

  return (
    <Screen
      title="Trends"
      subtitle="This screen should grow into a daily and weekly reflection view, not just a web chart squeezed onto a phone."
    >
      {loading ? (
        <View style={styles.center}>
          <ActivityIndicator size="large" color={colors.primary} />
        </View>
      ) : error ? (
        <Card title="Trend data unavailable" subtitle={error} />
      ) : (
        <>
          <View style={styles.row}>
            <MetricChip label="Mean" value={mean ? `${mean} mg/dL` : "—"} tone="primary" />
            <MetricChip label="In range" value={inRange ? `${inRange}%` : "—"} tone="success" />
          </View>

          <Card title="Current shape">
            <Text style={styles.body}>
              The backend already returns wearable and CGM series for the signed-in user. For V1,
              a simplified sparkline or compact chart is enough. The key is helping the user answer:
              did this day go well, and why?
            </Text>
          </Card>

          <Card title="Available devices">
            {devices.length === 0 ? (
              <Text style={styles.body}>No synced devices yet.</Text>
            ) : (
              devices.map((device) => (
                <View key={device.device.id} style={styles.deviceRow}>
                  <Text style={styles.deviceTitle}>
                    {device.device.vendor} {device.device.model || device.device.type}
                  </Text>
                  <Text style={styles.deviceMeta}>{device.count} readings loaded</Text>
                </View>
              ))
            )}
          </Card>
        </>
      )}
    </Screen>
  );
}

const styles = StyleSheet.create({
  center: {
    minHeight: 220,
    alignItems: "center",
    justifyContent: "center",
  },
  row: {
    flexDirection: "row",
    gap: 12,
  },
  body: {
    fontSize: 15,
    lineHeight: 22,
    color: colors.textMuted,
  },
  deviceRow: {
    paddingVertical: 8,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  deviceTitle: {
    fontSize: 15,
    fontWeight: "700",
    color: colors.text,
  },
  deviceMeta: {
    marginTop: 4,
    fontSize: 14,
    color: colors.textMuted,
  },
});
