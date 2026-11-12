import { useState } from "react";
import { Pressable, StyleSheet, Text, TextInput } from "react-native";

import { Card } from "@/components/card";
import { Screen } from "@/components/screen";
import { api } from "@/lib/api/client";
import type { ChatResponse } from "@/lib/api/types";
import { colors } from "@/lib/theme";

export default function CareScreen() {
  const [prompt, setPrompt] = useState("What should I pay attention to today?");
  const [result, setResult] = useState<ChatResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function ask() {
    try {
      setLoading(true);
      setError(null);
      const res = await api.chat.send(prompt);
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Chat unavailable.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Screen
      title="Care"
      subtitle="This tab combines coach, clinician-share, and account utilities. In V1 it can stay intentionally compact."
    >
      <Card title="Ask Glymmy" subtitle="Chat may require the local embedding model and Ollama services to be available.">
        <TextInput
          multiline
          style={styles.input}
          value={prompt}
          onChangeText={setPrompt}
          placeholder="Ask about glucose, labs, or food..."
          placeholderTextColor={colors.textMuted}
        />
        <Pressable style={styles.button} onPress={() => void ask()}>
          <Text style={styles.buttonText}>{loading ? "Thinking..." : "Ask"}</Text>
        </Pressable>
        {error ? <Text style={styles.error}>{error}</Text> : null}
        {result ? (
          <Text style={styles.body}>
            {result.response}
            {result.sources.length > 0 ? `\n\nSources: ${result.sources.map((s) => s.title).join(", ")}` : ""}
          </Text>
        ) : null}
      </Card>

      <Card title="Share with doctor">
        <Text style={styles.body}>
          The repo already has QR-based sharing on the backend, but the mobile screen is still missing.
          This should become a polished handoff flow with consent, summary, and a QR or secure link.
        </Text>
      </Card>
    </Screen>
  );
}

const styles = StyleSheet.create({
  input: {
    minHeight: 100,
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
    borderRadius: 14,
    paddingVertical: 12,
    alignItems: "center",
  },
  buttonText: {
    color: "#fff",
    fontWeight: "700",
    fontSize: 15,
  },
  body: {
    fontSize: 15,
    lineHeight: 22,
    color: colors.textMuted,
  },
  error: {
    color: colors.danger,
    fontSize: 14,
  },
});
