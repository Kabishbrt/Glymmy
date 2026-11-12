import type { PropsWithChildren } from "react";
import { StyleSheet, Text, View } from "react-native";

import { colors } from "@/lib/theme";

export function Card({
  title,
  subtitle,
  children,
}: PropsWithChildren<{
  title?: string;
  subtitle?: string;
}>) {
  return (
    <View style={styles.card}>
      {title ? <Text style={styles.title}>{title}</Text> : null}
      {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: colors.border,
    padding: 16,
    gap: 10,
  },
  title: {
    fontSize: 17,
    fontWeight: "700",
    color: colors.text,
  },
  subtitle: {
    fontSize: 14,
    lineHeight: 20,
    color: colors.textMuted,
  },
});
