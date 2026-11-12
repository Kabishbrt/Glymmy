"use client";

import { useState } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { api } from "@/lib/api-client";
import type { FoodAnalysisResponse, SpikePredictionResponse } from "@/lib/api-types";
import { Upload, Loader2, TrendingUp } from "lucide-react";

function generatePredictionCurve(prediction: SpikePredictionResponse, baseline = 120) {
  const peak = baseline + prediction.predicted_spike_mg_dl;
  const peakMin = prediction.time_to_peak_min;
  const points = [];
  for (let t = 0; t <= 180; t += 15) {
    let glucose: number;
    if (t <= peakMin) {
      const progress = t / peakMin;
      glucose = baseline + (peak - baseline) * Math.sin((progress * Math.PI) / 2);
    } else {
      const decay = (t - peakMin) / (180 - peakMin);
      glucose = peak - (peak - baseline) * Math.pow(decay, 0.8);
    }
    points.push({ time: `+${t}m`, glucose: Math.round(glucose) });
  }
  return points;
}

export default function FoodPage() {
  const [result, setResult] = useState<FoodAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [taskStatus, setTaskStatus] = useState<string | null>(null);
  const [description, setDescription] = useState("");

  // Poll a task until complete
  async function pollTask(taskId: string) {
    setTaskStatus("processing");
    const poll = setInterval(async () => {
      try {
        const task = await api.tasks.getStatus(taskId);
        if (task.status === "completed" && task.result) {
          clearInterval(poll);
          setTaskStatus(null);
          const res = task.result as FoodAnalysisResponse;
          setResult(res);
          setLoading(false);
          if (res.glucose_prediction) {
            sessionStorage.setItem("glucosePrediction", JSON.stringify(res.glucose_prediction));
          }
        } else if (task.status === "failed") {
          clearInterval(poll);
          setTaskStatus(null);
          setLoading(false);
        }
      } catch {
        clearInterval(poll);
        setTaskStatus(null);
        setLoading(false);
      }
    }, 2000);
  }

  async function onFileSelected(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setLoading(true);
    setResult(null);
    try {
      const { task_id } = await api.tasks.submitFoodPredict(file);
      await pollTask(task_id);
    } catch {
      // Fallback to synchronous
      try {
        const res = await api.food.scan(file);
        setResult(res);
        if (res.glucose_prediction) {
          sessionStorage.setItem("glucosePrediction", JSON.stringify(res.glucose_prediction));
        }
      } finally {
        setLoading(false);
      }
    }
  }

  async function onTextAnalyze() {
    if (!description.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const { task_id } = await api.tasks.submitFoodPredict(undefined, description);
      await pollTask(task_id);
    } catch {
      // Fallback to synchronous
      try {
        const res = await api.food.analyzeText(description);
        setResult(res);
        if (res.glucose_prediction) {
          sessionStorage.setItem("glucosePrediction", JSON.stringify(res.glucose_prediction));
        }
      } finally {
        setLoading(false);
      }
    }
  }

  const predictionCurve = result?.glucose_prediction
    ? generatePredictionCurve(result.glucose_prediction)
    : null;

  return (
    <div className="space-y-6 max-w-5xl">
      <div>
        <h1 className="text-2xl font-bold text-white">Food Scanner</h1>
        <p className="text-neutral-500 mt-1">
          Upload a photo or describe your meal — Glymmy estimates nutrition and predicts your glucose spike.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card className="border-neutral-800 bg-neutral-900/50">
          <CardHeader>
            <CardTitle className="text-white">Upload Photo</CardTitle>
            <CardDescription className="text-neutral-500">JPEG or PNG of your meal</CardDescription>
          </CardHeader>
          <CardContent>
            <label className="flex cursor-pointer flex-col items-center justify-center gap-3 rounded-lg border-2 border-dashed border-neutral-700 py-12 hover:bg-neutral-800/50 transition">
              {loading ? (
                <Loader2 className="h-8 w-8 animate-spin text-sky-400" />
              ) : (
                <Upload className="h-8 w-8 text-neutral-500" />
              )}
              <span className="text-sm text-neutral-400">Click to upload</span>
              <input type="file" accept="image/*" className="hidden" onChange={onFileSelected} disabled={loading} />
            </label>
          </CardContent>
        </Card>

        <Card className="border-neutral-800 bg-neutral-900/50">
          <CardHeader>
            <CardTitle className="text-white">Or Describe It</CardTitle>
            <CardDescription className="text-neutral-500">Plain-English works too</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Textarea
              rows={4}
              placeholder="e.g. Dal, white rice, 2 roti, and a small bowl of vegetable curry"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="bg-neutral-800 border-neutral-700 text-white placeholder:text-neutral-500"
            />
            <Button onClick={onTextAnalyze} disabled={loading || !description.trim()} className="w-full">
              {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              Analyze
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Task processing status */}
      {loading && taskStatus && (
        <Card className="border-neutral-800 bg-neutral-900/50">
          <CardContent className="py-8 flex flex-col items-center gap-3">
            <Loader2 className="h-8 w-8 animate-spin text-sky-400" />
            <p className="text-sm text-neutral-400">
              {taskStatus === "processing" ? "Gemma 4 is analyzing your meal..." : "Queuing analysis..."}
            </p>
            <p className="text-xs text-neutral-600">This may take 10-30 seconds</p>
          </CardContent>
        </Card>
      )}

      {result && (
        <>
          {/* Prediction Chart */}
          {predictionCurve && (
            <Card className="border-neutral-800 bg-neutral-900/50">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-orange-400" />
                  Predicted Glucose Response
                </CardTitle>
                <CardDescription className="text-neutral-500">
                  Estimated glucose curve over the next 3 hours
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={200}>
                  <AreaChart data={predictionCurve}>
                    <defs>
                      <linearGradient id="glucoseGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#f97316" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#f97316" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="time" tick={{ fill: "#9ca3af", fontSize: 12 }} />
                    <YAxis tick={{ fill: "#9ca3af", fontSize: 12 }} domain={["dataMin - 10", "dataMax + 10"]} />
                    <Tooltip
                      contentStyle={{ backgroundColor: "#1f2937", border: "1px solid #374151", borderRadius: "8px" }}
                      labelStyle={{ color: "#9ca3af" }}
                      itemStyle={{ color: "#f97316" }}
                    />
                    <Area type="monotone" dataKey="glucose" stroke="#f97316" strokeWidth={2} fill="url(#glucoseGradient)" />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          )}

          {/* Spike Summary */}
          <Card className="border-neutral-800 bg-gradient-to-br from-orange-950/30 to-neutral-950 border-orange-900/30">
            <CardContent className="py-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-neutral-400">Predicted spike</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-3xl font-bold text-white">+{result.glucose_prediction.predicted_spike_mg_dl} mg/dL</span>
                    <Badge variant={result.glucose_prediction.risk === "high" ? "destructive" : "secondary"}>
                      {result.glucose_prediction.risk}
                    </Badge>
                  </div>
                  <p className="text-sm text-neutral-500 mt-1">
                    With 15-min walk: +{result.glucose_prediction.with_walk_spike_mg_dl} mg/dL
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-neutral-500">Net carbs</p>
                  <p className="text-xl font-bold text-white">{result.glucose_prediction.net_carbs_g}g</p>
                  <p className="text-xs text-neutral-500">peak at {result.glucose_prediction.time_to_peak_min}min</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Items + Macros */}
          <Card className="border-neutral-800 bg-neutral-900/50">
            <CardHeader>
              <CardTitle className="text-white">Nutrition Breakdown</CardTitle>
              <CardDescription className="text-neutral-500">Source: {result.source}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                {result.items.map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between rounded-lg border border-neutral-800 bg-neutral-800/30 p-3">
                    <div>
                      <div className="font-medium text-white">{item.name}</div>
                      <div className="text-xs text-neutral-500">{item.portion}</div>
                    </div>
                    <div className="text-right text-sm">
                      <div className="font-semibold text-white">{item.calories} kcal</div>
                      <div className="text-xs text-neutral-500">
                        C: {item.carbs_g}g · P: {item.protein_g}g · F: {item.fat_g}g
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="grid grid-cols-5 gap-3 border-t border-neutral-800 pt-4">
                <Macro label="Calories" value={result.total.calories} unit="kcal" />
                <Macro label="Carbs" value={result.total.carbs_g} unit="g" />
                <Macro label="Protein" value={result.total.protein_g} unit="g" />
                <Macro label="Fat" value={result.total.fat_g} unit="g" />
                <Macro label="Fiber" value={result.total.fiber_g} unit="g" />
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}

function Macro({ label, value, unit }: { label: string; value: number; unit: string }) {
  return (
    <div className="text-center">
      <div className="text-xs text-neutral-500 uppercase">{label}</div>
      <div className="text-lg font-bold text-white">{Math.round(value)}</div>
      <div className="text-xs text-neutral-500">{unit}</div>
    </div>
  );
}
