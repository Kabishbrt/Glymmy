import { useEffect, useState } from "react";
import { ActivityIndicator, Pressable, StyleSheet, Text } from "react-native";

import { Card } from "@/components/card";
import { Screen } from "@/components/screen";
import { api } from "@/lib/api/client";
import type { LabInterpretation } from "@/lib/api/types";
import { colors } from "@/lib/theme";

const DEMO_PATIENT_ID = "mimic_10000032";

export default function LabsScreen() {
  const [interpretation, setInterpretation] = useState<LabInterpretation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void interpret();
  }, []);

  async function interpret() {
    try {
      setLoading(true);
      setError(null);
      const res = await api.labs.interpret(DEMO_PATIENT_ID);
      setInterpretation(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to interpret labs.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Screen
      title="Labs"
      subtitle="Labs are powerful in the product, but they should feel like care support rather than the app's primary heartbeat."
    >
      {loading ? (
        <ActivityIndicator size="large" color={colors.primary} />
      ) : error ? (
        <Card title="Lab interpretation unavailable" subtitle={error}>
          <Pressable style={styles.button} onPress={() => void interpret()}>
            <Text style={styles.buttonText}>Try again</Text>
          </Pressable>
        </Card>
      ) : interpretation ? (
        <>
          <Card title="AI interpretation" subtitle={interpretation.summary}>
            <Text style={styles.body}>
              Diabetes risk: {interpretation.risk_assessment.diabetes_risk}{"\n"}
              Cardiovascular risk: {interpretation.risk_assessment.cardiovascular_risk}{"\n"}
              Liver risk: {interpretation.risk_assessment.liver_risk}{"\n"}
              Kidney risk: {interpretation.risk_assessment.kidney_risk}
            </Text>
          </Card>

          {interpretation.abnormal_markers.slice(0, 3).map((marker) => (
            <Card
              key={marker.test}
              title={`${marker.test}: ${marker.value} ${marker.unit || ""}`.trim()}
              subtitle={`${marker.status} · ${marker.severity}`}
            >
              <Text style={styles.body}>{marker.explanation}</Text>
            </Card>
          ))}
        </>
      ) : null}
    </Screen>
  );
}

const styles = StyleSheet.create({
  body: {
    fontSize: 15,
    lineHeight: 22,
    color: colors.textMuted,
  },
  button: {
    marginTop: 4,
    backgroundColor: colors.primary,
    borderRadius: 14,
    paddingVertical: 12,
    alignItems: "center",
  },
  buttonText: {
    color: "#fff",
    fontWeight: "700",
  },
});
