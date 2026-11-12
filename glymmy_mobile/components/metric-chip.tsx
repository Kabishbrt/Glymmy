import { StyleSheet, Text, View } from "react-native";

import { colors } from "@/lib/theme";

export function MetricChip({
  label,
  value,
  tone = "neutral",
}: {
  label: string;
  value: string;
  tone?: "neutral" | "primary" | "success" | "warning" | "danger";
}) {
  const toneStyle = tones[tone];

  return (
    <View style={[styles.chip, toneStyle.container]}>
      <Text style={[styles.label, toneStyle.text]}>{label}</Text>
      <Text style={[styles.value, toneStyle.text]}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  chip: {
    borderRadius: 16,
    paddingHorizontal: 14,
    paddingVertical: 12,
    gap: 4,
    minWidth: 110,
  },
  label: {
    fontSize: 12,
    fontWeight: "600",
  },
  value: {
    fontSize: 18,
    fontWeight: "800",
  },
});

const tones = {
  neutral: {
    container: { backgroundColor: colors.surfaceMuted },
    text: { color: colors.text },
  },
  primary: {
    container: { backgroundColor: colors.primarySoft },
    text: { color: colors.primary },
  },
  success: {
    container: { backgroundColor: colors.successSoft },
    text: { color: colors.success },
  },
  warning: {
    container: { backgroundColor: colors.warningSoft },
    text: { color: colors.warning },
  },
  danger: {
    container: { backgroundColor: colors.dangerSoft },
    text: { color: colors.danger },
  },
} as const;
