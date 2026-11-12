"use client";

import { useEffect, useMemo, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceArea,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useUser } from "@/components/dashboard/user-context";
import { api } from "@/lib/api-client";
import type {
  CGMReading,
  UserWearablesResponse,
  SpikePredictionResponse,
} from "@/lib/api-types";
import { Activity, TrendingUp, ArrowDown, ArrowUp } from "lucide-react";

interface GlucosePrediction {
  predicted_spike_mg_dl: number;
  time_to_peak_min: number;
  with_walk_spike_mg_dl: number;
}

interface ChartPoint {
  time: string;
  glucose?: number;
  predicted?: number;
  predictedWalk?: number;
}

export default function GlucosePage() {
  const { user } = useUser();
  const [readings, setReadings] = useState<CGMReading[]>([]);
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState<SpikePredictionResponse | null>(null);
  const [predicting, setPredicting] = useState(false);
  const [meal, setMeal] = useState({ carbs_g: 60, protein_g: 15, fat_g: 10, fiber_g: 5 });

  // Load CGM data from wearables endpoint
  useEffect(() => {
    if (!user) return;
    setLoading(true);
    api.me
      .wearables({ device_type: "cgm", limit: 2016 })
      .then((res: UserWearablesResponse) => {
        const allReadings: CGMReading[] = [];
        for (const device of res.devices) {
          for (const r of device.readings) {
            if ("glucose_mg_dl" in r) {
              allReadings.push(r as CGMReading);
            }
          }
        }
        allReadings.sort(
          (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime(),
        );
        setReadings(allReadings);
      })
      .catch(() => setReadings([]))
      .finally(() => setLoading(false));
  }, [user]);

  // Check sessionStorage for prediction overlay
  const storedPrediction = useMemo<GlucosePrediction | null>(() => {
    if (typeof window === "undefined") return null;
    try {
      const raw = sessionStorage.getItem("glucosePrediction");
      if (!raw) return null;
      return JSON.parse(raw) as GlucosePrediction;
    } catch {
      return null;
    }
  }, []);

  // Compute stats client-side
  const stats = useMemo(() => {
    if (readings.length === 0) return null;
    const values = readings.map((r) => r.glucose_mg_dl);
    const sum = values.reduce((a, b) => a + b, 0);
    const mean = Math.round(sum / values.length);
    const min = Math.round(Math.min(...values));
    const max = Math.round(Math.max(...values));
    const inRange = values.filter((v) => v >= 70 && v <= 180).length;
    const tir = Math.round((inRange / values.length) * 100);
    return { mean, min, max, tir };
  }, [readings]);

  // Build chart data + optional prediction overlay
  const chartData = useMemo<ChartPoint[]>(() => {
    const points: ChartPoint[] = readings.map((r) => ({
      time: new Date(r.timestamp).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
      glucose: Math.round(r.glucose_mg_dl),
    }));

    if (storedPrediction && readings.length > 0) {
      const lastReading = readings[readings.length - 1];
      const baseline = lastReading.glucose_mg_dl;
      const lastTime = new Date(lastReading.timestamp).getTime();
      const { predicted_spike_mg_dl, time_to_peak_min, with_walk_spike_mg_dl } =
        storedPrediction;

      // Generate ~12 synthetic future points
      const totalMin = time_to_peak_min * 2;
      const stepMin = Math.max(5, Math.round(totalMin / 12));
      for (let i = 1; i <= 12; i++) {
        const minutesAhead = i * stepMin;
        const t = new Date(lastTime + minutesAhead * 60_000);
        const timeLabel = t.toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        });

        // Gaussian-ish curve peaking at time_to_peak_min
        const progress = minutesAhead / time_to_peak_min;
        const curve = Math.exp(-0.5 * Math.pow(progress - 1, 2));
        const predicted = Math.round(baseline + predicted_spike_mg_dl * curve);
        const predictedWalk = Math.round(baseline + with_walk_spike_mg_dl * curve);

        points.push({
          time: timeLabel,
          predicted,
          predictedWalk,
        });
      }
    }

    return points;
  }, [readings, storedPrediction]);

  async function handlePredict() {
    if (!user) return;
    setPredicting(true);
    try {
      const res = await api.glucose.predict({
        patient_id: user.id,
        meal,
      });
      setPrediction(res);
      // Store for chart overlay
      if (res) {
        sessionStorage.setItem(
          "glucosePrediction",
          JSON.stringify({
            predicted_spike_mg_dl: res.predicted_spike_mg_dl,
            time_to_peak_min: res.time_to_peak_min,
            with_walk_spike_mg_dl: res.with_walk_spike_mg_dl,
          }),
        );
      }
    } finally {
      setPredicting(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white">
          Glucose Dashboard
        </h1>
        <p className="text-neutral-500 mt-1">
          Continuous glucose monitoring + AI meal spike prediction
        </p>
      </div>

      {/* Stats cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <StatCard
          label="Mean"
          value={stats?.mean}
          unit="mg/dL"
          icon={<Activity className="h-4 w-4 text-neutral-400" />}
          loading={loading}
        />
        <StatCard
          label="Time in Range"
          value={stats?.tir}
          unit="%"
          icon={<TrendingUp className="h-4 w-4 text-emerald-400" />}
          accent="success"
          loading={loading}
        />
        <StatCard
          label="Min"
          value={stats?.min}
          unit="mg/dL"
          icon={<ArrowDown className="h-4 w-4 text-blue-400" />}
          loading={loading}
        />
        <StatCard
          label="Max"
          value={stats?.max}
          unit="mg/dL"
          icon={<ArrowUp className="h-4 w-4 text-red-400" />}
          loading={loading}
        />
      </div>

      {/* Chart */}
      <Card className="border-neutral-800 bg-neutral-900/50">
        <CardHeader>
          <CardTitle className="text-white">Glucose Over Time</CardTitle>
          <p className="text-sm text-neutral-500">
            Target range: 70-180 mg/dL (shaded green)
            {storedPrediction && (
              <span className="ml-2 text-orange-400">
                + predicted spike overlay
              </span>
            )}
          </p>
        </CardHeader>
        <CardContent>
          {loading ? (
            <Skeleton className="h-80 w-full bg-neutral-800" />
          ) : chartData.length === 0 ? (
            <div className="h-80 flex items-center justify-center text-neutral-500">
              No CGM data available
            </div>
          ) : (
            <div style={{ width: "100%", height: 320 }}>
              <ResponsiveContainer width="100%" height={320}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis
                    dataKey="time"
                    tick={{ fontSize: 11, fill: "#9ca3af" }}
                    axisLine={{ stroke: "#374151" }}
                    tickLine={{ stroke: "#374151" }}
                  />
                  <YAxis
                    domain={[40, 300]}
                    tick={{ fontSize: 11, fill: "#9ca3af" }}
                    axisLine={{ stroke: "#374151" }}
                    tickLine={{ stroke: "#374151" }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#1f2937",
                      border: "1px solid #374151",
                      borderRadius: "8px",
                      color: "#f3f4f6",
                    }}
                    labelStyle={{ color: "#9ca3af" }}
                  />
                  <ReferenceArea
                    y1={70}
                    y2={180}
                    fill="#22c55e"
                    fillOpacity={0.08}
                  />
                  <Line
                    type="monotone"
                    dataKey="glucose"
                    stroke="#3b82f6"
                    strokeWidth={2}
                    dot={false}
                    name="Glucose"
                    connectNulls={false}
                  />
                  {storedPrediction && (
                    <Line
                      type="monotone"
                      dataKey="predicted"
                      stroke="#f97316"
                      strokeWidth={2}
                      strokeDasharray="6 3"
                      dot={false}
                      name="Predicted"
                      connectNulls={false}
                    />
                  )}
                  {storedPrediction && (
                    <Line
                      type="monotone"
                      dataKey="predictedWalk"
                      stroke="#a3e635"
                      strokeWidth={2}
                      strokeDasharray="4 4"
                      dot={false}
                      name="With Walk"
                      connectNulls={false}
                    />
                  )}
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Meal Spike Predictor */}
      <Card className="border-neutral-800 bg-neutral-900/50">
        <CardHeader>
          <CardTitle className="text-white">Predict Meal Spike</CardTitle>
          <p className="text-sm text-neutral-500">
            Enter meal macros to predict your glucose response
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-3 sm:grid-cols-4">
            <FormField
              label="Carbs (g)"
              value={meal.carbs_g}
              onChange={(v) => setMeal({ ...meal, carbs_g: v })}
            />
            <FormField
              label="Protein (g)"
              value={meal.protein_g}
              onChange={(v) => setMeal({ ...meal, protein_g: v })}
            />
            <FormField
              label="Fat (g)"
              value={meal.fat_g}
              onChange={(v) => setMeal({ ...meal, fat_g: v })}
            />
            <FormField
              label="Fiber (g)"
              value={meal.fiber_g}
              onChange={(v) => setMeal({ ...meal, fiber_g: v })}
            />
          </div>
          <Button
            onClick={handlePredict}
            disabled={predicting || !user}
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
            {predicting ? "Predicting..." : "Predict Spike"}
          </Button>

          {prediction && (
            <div className="mt-4 rounded-lg border border-neutral-800 bg-neutral-900 p-4">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-sm text-neutral-400">Predicted spike:</span>
                <span className="text-2xl font-bold text-white">
                  +{prediction.predicted_spike_mg_dl} mg/dL
                </span>
                <Badge
                  variant={
                    prediction.risk === "high"
                      ? "destructive"
                      : prediction.risk === "moderate"
                        ? "secondary"
                        : "default"
                  }
                >
                  {prediction.risk} risk
                </Badge>
              </div>
              <div className="mt-2 text-sm text-neutral-400">
                Net carbs: {prediction.net_carbs_g}g &middot; Peak in ~
                {prediction.time_to_peak_min} min &middot; With 15-min walk: +
                {prediction.with_walk_spike_mg_dl} mg/dL
              </div>
              {prediction.explanation && (
                <div className="mt-2 text-xs text-neutral-500">
                  {prediction.explanation}
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

/* ─── Stat card ──────────────────────────────────────────────────────────── */

function StatCard({
  label,
  value,
  unit,
  icon,
  accent,
  loading,
}: {
  label: string;
  value: string | number | null | undefined;
  unit: string;
  icon?: React.ReactNode;
  accent?: "success";
  loading?: boolean;
}) {
  return (
    <Card className="border-neutral-800 bg-neutral-900/50">
      <CardContent className="pt-6">
        <div className="flex items-center gap-2 text-xs text-neutral-500 uppercase tracking-wide">
          {icon}
          {label}
        </div>
        {loading ? (
          <Skeleton className="h-8 w-24 mt-1 bg-neutral-800" />
        ) : (
          <div
            className={`text-2xl font-bold mt-1 ${
              accent === "success" ? "text-emerald-400" : "text-white"
            }`}
          >
            {value ?? "\u2014"}{" "}
            <span className="text-sm font-normal text-neutral-500">{unit}</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

/* ─── Form field ─────────────────────────────────────────────────────────── */

function FormField({
  label,
  value,
  onChange,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
}) {
  return (
    <div>
      <label className="text-xs text-neutral-400">{label}</label>
      <Input
        type="number"
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
        className="mt-1 border-neutral-700 bg-neutral-800 text-white placeholder:text-neutral-500"
      />
    </div>
  );
}
