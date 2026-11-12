import type { PropsWithChildren, ReactNode } from "react";
import type { ScrollViewProps } from "react-native";
import { SafeAreaView, ScrollView, StyleSheet, Text, View } from "react-native";

import { colors, spacing } from "@/lib/theme";

export function Screen({
  title,
  subtitle,
  children,
  right,
  scroll = true,
  scrollProps,
}: PropsWithChildren<{
  title: string;
  subtitle?: string;
  right?: ReactNode;
  scroll?: boolean;
  scrollProps?: ScrollViewProps;
}>) {
  const content = (
    <View style={styles.container}>
      <View style={styles.header}>
        <View style={styles.headerText}>
          <Text style={styles.title}>{title}</Text>
          {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
        </View>
        {right}
      </View>
      {children}
    </View>
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      {scroll ? <ScrollView {...scrollProps}>{content}</ScrollView> : content}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: colors.bg,
  },
  container: {
    paddingHorizontal: spacing.screen,
    paddingTop: 20,
    paddingBottom: 32,
    gap: 16,
  },
  header: {
    flexDirection: "row",
    alignItems: "flex-start",
    justifyContent: "space-between",
    gap: 12,
  },
  headerText: {
    flex: 1,
    gap: 6,
  },
  title: {
    fontSize: 30,
    fontWeight: "800",
    color: colors.text,
  },
  subtitle: {
    fontSize: 15,
    lineHeight: 22,
    color: colors.textMuted,
  },
});
