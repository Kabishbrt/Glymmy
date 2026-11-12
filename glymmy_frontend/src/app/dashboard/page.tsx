"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Activity,
  Apple,
  ArrowDown,
  ArrowRight,
  ArrowUp,
  Bell,
  FlaskConical,
  Heart,
  MessageSquare,
  Minus,
  ScanLine,
  Watch,
  Wind,
  Footprints,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useUser } from "@/components/dashboard/user-context";
import { api } from "@/lib/api-client";
import type {
  LatestCgmResponse,
  NotificationResponse,
  SmartwatchReading,
  Device,
} from "@/lib/api-types";

function TrendIcon({ trend }: { trend?: string | null }) {
  if (trend === "rising") return <ArrowUp className="h-5 w-5 text-orange-400" />;
  if (trend === "falling") return <ArrowDown className="h-5 w-5 text-sky-400" />;
  return <Minus className="h-4 w-4 text-neutral-500" />;
}

function glucoseColor(mg: number) {
  if (mg < 70 || mg > 250) return "from-red-900/30 to-red-950/20 border-red-800/50";
  if (mg > 180) return "from-amber-900/30 to-amber-950/20 border-amber-800/50";
  return "from-emerald-900/30 to-emerald-950/20 border-emerald-800/50";
}

function glucoseLabel(mg: number) {
  if (mg < 70) return { text: "Low", color: "text-red-400" };
  if (mg > 250) return { text: "Critical High", color: "text-red-400" };
  if (mg > 180) return { text: "High", color: "text-amber-400" };
  return { text: "In Range", color: "text-emerald-400" };
}

function DeviceIcon({ type }: { type: string }) {
  if (type === "smartwatch") return <Watch className="h-5 w-5 text-sky-400" />;
  if (type === "heart_rate_monitor") return <Heart className="h-5 w-5 text-rose-400" />;
  if (type === "cgm") return <Activity className="h-5 w-5 text-emerald-400" />;
  return <Activity className="h-5 w-5 text-violet-400" />;
}

function SeverityBadge({ severity }: { severity: string }) {
  const map: Record<string, string> = {
    critical: "bg-red-900/50 text-red-300 border-red-800",
    high: "bg-orange-900/50 text-orange-300 border-orange-800",
    moderate: "bg-amber-900/50 text-amber-300 border-amber-800",
  };
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full border ${map[severity] || map.moderate}`}>
      {severity}
    </span>
  );
}

const quickActions = [
  { title: "Glucose Trends", desc: "View your CGM data", href: "/dashboard/glucose", icon: Activity, color: "text-emerald-400" },
  { title: "Scan Food", desc: "Photo or text analysis", href: "/dashboard/food", icon: Apple, color: "text-orange-400" },
  { title: "Scan Document", desc: "Lab reports & prescriptions", href: "/dashboard/scan", icon: ScanLine, color: "text-sky-400" },
  { title: "Ask Glymmy", desc: "AI health chat", href: "/dashboard/chat", icon: MessageSquare, color: "text-violet-400" },
];

export default function DashboardOverview() {
  const { user, loading: userLoading } = useUser();
  const [cgm, setCgm] = useState<LatestCgmResponse | null>(null);
  const [notifications, setNotifications] = useState<NotificationResponse | null>(null);
  const [watchData, setWatchData] = useState<SmartwatchReading | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    if (userLoading) return;
    Promise.allSettled([
      api.me.latestCgm().then(setCgm),
      api.me.notifications().then(setNotifications),
      api.me.wearables({ device_type: "smartwatch", limit: 1 }).then((res) => {
        const dev = res.devices?.[0];
        if (dev?.readings?.length) setWatchData(dev.readings[0] as SmartwatchReading);
      }),
    ]).finally(() => setLoaded(true));
  }, [userLoading]);

  const glucose = cgm?.latest_reading?.glucose_mg_dl;
  const trend = cgm?.latest_reading?.trend;

  return (
    <div className="space-y-6 max-w-5xl">
      {/* Glucose Hero */}
      <Card className={`border bg-gradient-to-br ${glucose ? glucoseColor(glucose) : "from-neutral-900 to-neutral-950 border-neutral-800"}`}>
        <CardContent className="py-8 flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-neutral-400 mb-1">Current Glucose</p>
            {!loaded ? (
              <Skeleton className="h-16 w-40" />
            ) : glucose ? (
              <div className="flex items-end gap-3">
                <span className="text-6xl font-bold text-white tabular-nums">{Math.round(glucose)}</span>
                <span className="text-lg text-neutral-400 mb-2">mg/dL</span>
                <TrendIcon trend={trend} />
              </div>
            ) : (
              <p className="text-2xl text-neutral-500">No CGM data</p>
            )}
            {glucose && (
              <p className={`text-sm mt-1 ${glucoseLabel(glucose).color}`}>
                {glucoseLabel(glucose).text}
              </p>
            )}
          </div>
          <div className="text-right">
            {user && (
              <>
                <p className="text-sm text-neutral-500">A1C</p>
                <p className="text-2xl font-bold text-white">{user.a1c || "—"}%</p>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Heart Rate" value={watchData?.heart_rate_bpm ? `${watchData.heart_rate_bpm}` : "—"} unit="bpm" icon={<Heart className="h-4 w-4 text-rose-400" />} loaded={loaded} />
        <StatCard label="SpO2" value={watchData?.spo2_pct ? `${watchData.spo2_pct}` : "—"} unit="%" icon={<Wind className="h-4 w-4 text-sky-400" />} loaded={loaded} />
        <StatCard label="Steps" value={watchData?.steps ? `${watchData.steps.toLocaleString()}` : "—"} unit="" icon={<Footprints className="h-4 w-4 text-emerald-400" />} loaded={loaded} />
        <StatCard label="Devices" value={user?.devices?.length?.toString() || "0"} unit="paired" icon={<Watch className="h-4 w-4 text-violet-400" />} loaded={loaded} />
      </div>

      {/* Connected Devices */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-neutral-400">Connected Devices</h3>
          <Link href="/dashboard/devices" className="text-xs text-sky-400 hover:text-sky-300 flex items-center gap-1">
            View all <ArrowRight className="h-3 w-3" />
          </Link>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {userLoading ? (
            Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-20 rounded-xl" />)
          ) : user?.devices?.length ? (
            user.devices.map((d: Device) => (
              <Card key={d.id} className="border-neutral-800 bg-neutral-900/50">
                <CardContent className="py-3 flex items-center gap-3">
                  <div className="h-10 w-10 rounded-lg bg-neutral-800 flex items-center justify-center">
                    <DeviceIcon type={d.type} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-white truncate">{d.model || d.vendor}</p>
                    <p className="text-xs text-neutral-500 capitalize">{d.type.replace(/_/g, " ")}</p>
                  </div>
                  <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                </CardContent>
              </Card>
            ))
          ) : (
            <p className="text-sm text-neutral-500 col-span-3">No devices paired yet</p>
          )}
        </div>
      </div>

      {/* Recent Alerts */}
      {notifications && notifications.notifications.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-medium text-neutral-400">Recent Alerts</h3>
            <Link href="/dashboard/notifications" className="text-xs text-sky-400 hover:text-sky-300 flex items-center gap-1">
              View all <ArrowRight className="h-3 w-3" />
            </Link>
          </div>
          <div className="space-y-2">
            {notifications.notifications.slice(0, 3).map((n) => (
              <Card key={n.id} className="border-neutral-800 bg-neutral-900/50">
                <CardContent className="py-3 flex items-center gap-3">
                  <Bell className="h-4 w-4 text-amber-400 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-white truncate">{n.title}</p>
                    <p className="text-xs text-neutral-500 truncate">{n.message}</p>
                  </div>
                  <SeverityBadge severity={n.severity} />
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div>
        <h3 className="text-sm font-medium text-neutral-400 mb-3">Quick Actions</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {quickActions.map((a) => (
            <Link key={a.href} href={a.href}>
              <Card className="border-neutral-800 bg-neutral-900/50 hover:border-neutral-700 hover:bg-neutral-900 transition-colors cursor-pointer h-full">
                <CardContent className="py-4 flex flex-col items-center text-center gap-2">
                  <a.icon className={`h-6 w-6 ${a.color}`} />
                  <p className="text-sm font-medium text-white">{a.title}</p>
                  <p className="text-xs text-neutral-500">{a.desc}</p>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, unit, icon, loaded }: { label: string; value: string; unit: string; icon: React.ReactNode; loaded: boolean }) {
  return (
    <Card className="border-neutral-800 bg-neutral-900/50">
      <CardContent className="py-4">
        <div className="flex items-center gap-2 mb-2">
          {icon}
          <span className="text-xs text-neutral-500">{label}</span>
        </div>
        {!loaded ? (
          <Skeleton className="h-8 w-20" />
        ) : (
          <div className="flex items-baseline gap-1">
            <span className="text-2xl font-bold text-white tabular-nums">{value}</span>
            {unit && <span className="text-xs text-neutral-500">{unit}</span>}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
