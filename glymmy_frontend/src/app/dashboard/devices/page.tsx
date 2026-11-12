"use client";

import { useEffect, useState } from "react";
import { Activity, Footprints, Heart, Watch } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useUser } from "@/components/dashboard/user-context";
import { api } from "@/lib/api-client";
import type {
  Device,
  DeviceReadingsResponse,
  CGMReading,
  SmartwatchReading,
  HeartRateMonitorReading,
  ActivityTrackerReading,
} from "@/lib/api-types";

/* ── helpers ─────────────────────────────────────────────────────────── */

function DeviceIcon({ type }: { type: Device["type"] }) {
  switch (type) {
    case "smartwatch":
      return <Watch className="h-6 w-6 text-sky-400" />;
    case "heart_rate_monitor":
      return <Heart className="h-6 w-6 text-rose-400" />;
    case "cgm":
      return <Activity className="h-6 w-6 text-emerald-400" />;
    case "activity_tracker":
      return <Footprints className="h-6 w-6 text-violet-400" />;
  }
}

const vendorLabels: Record<Device["vendor"], string> = {
  dexcom: "Dexcom",
  libre: "Libre",
  apple_watch: "Apple Watch",
  garmin: "Garmin",
  fitbit: "Fitbit",
  oura: "Oura",
  whoop: "WHOOP",
};

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

/* ── readings summaries ──────────────────────────────────────────────── */

function CgmSummary({ reading }: { reading: CGMReading }) {
  return (
    <div className="flex items-baseline gap-3">
      <div>
        <p className="text-xs text-neutral-500">Glucose</p>
        <p className="text-lg font-semibold text-white tabular-nums">
          {Math.round(reading.glucose_mg_dl)}{" "}
          <span className="text-xs text-neutral-400">mg/dL</span>
        </p>
      </div>
      {reading.trend && (
        <div>
          <p className="text-xs text-neutral-500">Trend</p>
          <p className="text-sm text-neutral-300 capitalize">{reading.trend}</p>
        </div>
      )}
    </div>
  );
}

function SmartwatchSummary({ reading }: { reading: SmartwatchReading }) {
  return (
    <div className="flex flex-wrap gap-x-4 gap-y-1">
      {reading.heart_rate_bpm != null && (
        <div>
          <p className="text-xs text-neutral-500">HR</p>
          <p className="text-sm font-medium text-white tabular-nums">
            {reading.heart_rate_bpm} <span className="text-xs text-neutral-400">bpm</span>
          </p>
        </div>
      )}
      {reading.spo2_pct != null && (
        <div>
          <p className="text-xs text-neutral-500">SpO2</p>
          <p className="text-sm font-medium text-white tabular-nums">
            {reading.spo2_pct}<span className="text-xs text-neutral-400">%</span>
          </p>
        </div>
      )}
      {reading.steps != null && (
        <div>
          <p className="text-xs text-neutral-500">Steps</p>
          <p className="text-sm font-medium text-white tabular-nums">
            {reading.steps.toLocaleString()}
          </p>
        </div>
      )}
    </div>
  );
}

function HeartRateSummary({ reading }: { reading: HeartRateMonitorReading }) {
  return (
    <div className="flex gap-x-4">
      <div>
        <p className="text-xs text-neutral-500">HR</p>
        <p className="text-sm font-medium text-white tabular-nums">
          {reading.heart_rate_bpm} <span className="text-xs text-neutral-400">bpm</span>
        </p>
      </div>
      {reading.hrv_ms != null && (
        <div>
          <p className="text-xs text-neutral-500">HRV (RMSSD)</p>
          <p className="text-sm font-medium text-white tabular-nums">
            {reading.hrv_ms} <span className="text-xs text-neutral-400">ms</span>
          </p>
        </div>
      )}
    </div>
  );
}

function ActivitySummary({ reading }: { reading: ActivityTrackerReading }) {
  return (
    <div className="flex flex-wrap gap-x-4 gap-y-1">
      <div>
        <p className="text-xs text-neutral-500">Steps</p>
        <p className="text-sm font-medium text-white tabular-nums">
          {reading.steps.toLocaleString()}
        </p>
      </div>
      <div>
        <p className="text-xs text-neutral-500">Calories</p>
        <p className="text-sm font-medium text-white tabular-nums">
          {reading.calories_burned.toLocaleString()}
        </p>
      </div>
      <div>
        <p className="text-xs text-neutral-500">Active</p>
        <p className="text-sm font-medium text-white tabular-nums">
          {reading.active_minutes} <span className="text-xs text-neutral-400">min</span>
        </p>
      </div>
    </div>
  );
}

function ReadingSummary({ device, reading }: { device: Device; reading: unknown }) {
  if (!reading) return <p className="text-xs text-neutral-600">No readings yet</p>;

  switch (device.type) {
    case "cgm":
      return <CgmSummary reading={reading as CGMReading} />;
    case "smartwatch":
      return <SmartwatchSummary reading={reading as SmartwatchReading} />;
    case "heart_rate_monitor":
      return <HeartRateSummary reading={reading as HeartRateMonitorReading} />;
    case "activity_tracker":
      return <ActivitySummary reading={reading as ActivityTrackerReading} />;
  }
}

/* ── main page ───────────────────────────────────────────────────────── */

export default function DevicesPage() {
  const { user, loading: userLoading } = useUser();
  const [readings, setReadings] = useState<Record<string, DeviceReadingsResponse>>({});
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    if (userLoading || !user?.devices?.length) {
      if (!userLoading) setLoaded(true);
      return;
    }

    Promise.allSettled(
      user.devices.map((d) =>
        api.me.deviceReadings(d.id, { limit: 1 }).then((res) => {
          setReadings((prev) => ({ ...prev, [d.id]: res }));
        }),
      ),
    ).finally(() => setLoaded(true));
  }, [userLoading, user]);

  const devices = user?.devices ?? [];

  return (
    <div className="space-y-6 max-w-5xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Connected Devices</h1>
        <p className="text-sm text-neutral-500 mt-1">
          {userLoading
            ? "Loading..."
            : `${devices.length} device${devices.length !== 1 ? "s" : ""} paired`}
        </p>
      </div>

      {/* Grid */}
      {userLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-48 rounded-xl" />
          ))}
        </div>
      ) : devices.length === 0 ? (
        <Card className="border-neutral-800 bg-neutral-900/50">
          <CardContent className="py-12 text-center">
            <Watch className="h-10 w-10 text-neutral-700 mx-auto mb-3" />
            <p className="text-neutral-400">No devices paired yet</p>
            <p className="text-xs text-neutral-600 mt-1">
              Connect a wearable to start tracking your health data.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {devices.map((device) => {
            const latestReading = readings[device.id]?.readings?.[0] ?? null;
            const readingLoaded = loaded || !!readings[device.id];

            return (
              <Card
                key={device.id}
                className="border-neutral-800 bg-neutral-900/50"
              >
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-lg bg-neutral-800 flex items-center justify-center">
                        <DeviceIcon type={device.type} />
                      </div>
                      <div className="min-w-0">
                        <CardTitle className="text-sm font-medium text-white truncate">
                          {device.model || vendorLabels[device.vendor]}
                        </CardTitle>
                        <p className="text-xs text-neutral-500 capitalize">
                          {device.type.replace(/_/g, " ")}
                        </p>
                      </div>
                    </div>
                    <div className="h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse mt-1" />
                  </div>
                </CardHeader>

                <CardContent className="space-y-3">
                  {/* Vendor badge */}
                  <Badge
                    variant="outline"
                    className="border-neutral-700 bg-neutral-800/60 text-neutral-300 text-xs"
                  >
                    {vendorLabels[device.vendor]}
                  </Badge>

                  {/* Latest reading */}
                  <div className="pt-1">
                    {!readingLoaded ? (
                      <Skeleton className="h-10 w-full" />
                    ) : (
                      <ReadingSummary device={device} reading={latestReading} />
                    )}
                  </div>

                  {/* Paired date */}
                  <p className="text-xs text-neutral-600">
                    Paired {formatDate(device.paired_at)}
                  </p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
