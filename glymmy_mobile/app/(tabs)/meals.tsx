import { useState } from "react";
import { Pressable, StyleSheet, Text, TextInput, View } from "react-native";

import { Card } from "@/components/card";
import { Screen } from "@/components/screen";
import { api } from "@/lib/api/client";
import type { FoodAnalysisResponse } from "@/lib/api/types";
import { colors } from "@/lib/theme";

export default function MealsScreen() {
  const [description, setDescription] = useState(
    "Dal, white rice, grilled chicken, and cucumber salad",
  );
  const [result, setResult] = useState<FoodAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function analyze() {
    try {
      setLoading(true);
      setError(null);
      const res = await api.food.analyzeText(description);
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Meal analysis failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Screen
      title="Meals"
      subtitle="Food scanning should be one of the app's marquee flows because it creates immediate, personalized value."
    >
      <Card title="Quick meal check" subtitle="Camera capture can come next. Text keeps the loop testable right now.">
        <TextInput
          multiline
          style={styles.input}
          value={description}
          onChangeText={setDescription}
          placeholder="Describe your meal..."
          placeholderTextColor={colors.textMuted}
        />
        <Pressable style={styles.button} onPress={() => void analyze()}>
          <Text style={styles.buttonText}>{loading ? "Analyzing..." : "Analyze meal"}</Text>
        </Pressable>
        {error ? <Text style={styles.error}>{error}</Text> : null}
      </Card>

      {result ? (
        <>
          <Card title="Predicted response">
            <Text style={styles.spike}>
              +{result.glucose_prediction.predicted_spike_mg_dl} mg/dL
            </Text>
            <Text style={styles.body}>
              Risk: {result.glucose_prediction.risk}{"\n"}
              Peak in about {result.glucose_prediction.time_to_peak_min} minutes{"\n"}
              With a short walk: +{result.glucose_prediction.with_walk_spike_mg_dl} mg/dL
            </Text>
          </Card>

          <Card title="Nutrition summary">
            <Text style={styles.body}>
              Calories {Math.round(result.total.calories)} kcal
              {"\n"}Carbs {Math.round(result.total.carbs_g)} g
              {"\n"}Protein {Math.round(result.total.protein_g)} g
              {"\n"}Fat {Math.round(result.total.fat_g)} g
              {"\n"}Fiber {Math.round(result.total.fiber_g)} g
            </Text>
          </Card>
        </>
      ) : null}
    </Screen>
  );
}

const styles = StyleSheet.create({
  input: {
    minHeight: 120,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 16,
    padding: 14,
    fontSize: 15,
    lineHeight: 22,
    color: colors.text,
    backgroundColor: colors.bg,
    textAlignVertical: "top",
  },
  button: {
    backgroundColor: colors.primary,
    borderRadius: 16,
    paddingVertical: 14,
    alignItems: "center",
  },
  buttonText: {
    color: "#ffffff",
    fontSize: 15,
    fontWeight: "700",
  },
  spike: {
    fontSize: 34,
    fontWeight: "900",
    color: colors.text,
  },
  body: {
    fontSize: 15,
    lineHeight: 24,
    color: colors.textMuted,
  },
  error: {
    fontSize: 14,
    color: colors.danger,
  },
});
