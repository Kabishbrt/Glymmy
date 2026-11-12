"use client";

import { useEffect, useState, useCallback } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api-client";
import type {
  Notification,
  NotificationResponse,
  Reminder,
  RemindersResponse,
} from "@/lib/api-types";
import { Bell, Calendar, CheckCircle2, Clock, AlertTriangle } from "lucide-react";

type Tab = "alerts" | "reminders";

function relativeTime(timestamp: string): string {
  const now = Date.now();
  const then = new Date(timestamp).getTime();
  const diffMs = now - then;
  const diffMin = Math.floor(diffMs / 60_000);
  if (diffMin < 1) return "just now";
  if (diffMin < 60) return `${diffMin} min ago`;
  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `${diffHr}h ago`;
  const diffDays = Math.floor(diffHr / 24);
  return `${diffDays}d ago`;
}

const severityStyles: Record<string, string> = {
  critical: "bg-red-600/20 text-red-400 border-red-600/30",
  high: "bg-orange-600/20 text-orange-400 border-orange-600/30",
  moderate: "bg-amber-600/20 text-amber-400 border-amber-600/30",
};

const priorityStyles: Record<string, string> = {
  high: "bg-red-600/20 text-red-400 border-red-600/30",
  medium: "bg-amber-600/20 text-amber-400 border-amber-600/30",
  low: "bg-neutral-600/20 text-neutral-400 border-neutral-600/30",
};

export default function NotificationsPage() {
  const [tab, setTab] = useState<Tab>("alerts");

  // Alerts state
  const [alerts, setAlerts] = useState<NotificationResponse | null>(null);
  const [alertsLoading, setAlertsLoading] = useState(false);
  const [alertActioning, setAlertActioning] = useState<string | null>(null);

  // Reminders state
  const [reminders, setReminders] = useState<RemindersResponse | null>(null);
  const [remindersLoading, setRemindersLoading] = useState(false);
  const [reminderActioning, setReminderActioning] = useState<string | null>(null);

  const fetchAlerts = useCallback(() => {
    setAlertsLoading(true);
    api.me
      .notifications()
      .then(setAlerts)
      .catch(() => setAlerts(null))
      .finally(() => setAlertsLoading(false));
  }, []);

  const fetchReminders = useCallback(() => {
    setRemindersLoading(true);
    api.me
      .reminders()
      .then(setReminders)
      .catch(() => setReminders(null))
      .finally(() => setRemindersLoading(false));
  }, []);

  useEffect(() => {
    if (tab === "alerts") fetchAlerts();
    else fetchReminders();
  }, [tab, fetchAlerts, fetchReminders]);

  async function handleAlertAction(id: string, action: "acknowledge" | "snooze") {
    setAlertActioning(id);
    try {
      await api.me.acknowledgeNotification(
        id,
        action === "snooze" ? { action: "snooze", snooze_minutes: 30 } : { action: "acknowledge" },
      );
      fetchAlerts();
    } finally {
      setAlertActioning(null);
    }
  }

  async function handleReminderAction(id: string, action: "dismiss" | "snooze") {
    setReminderActioning(id);
    try {
      await api.me.dismissReminder(
        id,
        action === "snooze" ? { action: "snooze", snooze_days: 7 } : { action: "dismiss" },
      );
      fetchReminders();
    } finally {
      setReminderActioning(null);
    }
  }

  const activeNotifications = alerts?.notifications.filter((n) => !n.acknowledged) ?? [];
  const activeReminders = reminders?.reminders.filter((r) => !r.dismissed) ?? [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Notifications</h1>
        <p className="text-neutral-500 mt-1">
          AI glucose alerts and health check reminders
        </p>
      </div>

      {/* Tab toggle */}
      <div className="flex gap-1 rounded-lg bg-neutral-900 p-1 w-fit">
        <button
          onClick={() => setTab("alerts")}
          className={`flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors ${
            tab === "alerts"
              ? "bg-neutral-800 text-white"
              : "text-neutral-500 hover:text-neutral-300"
          }`}
        >
          <Bell className="h-4 w-4" />
          Alerts
        </button>
        <button
          onClick={() => setTab("reminders")}
          className={`flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors ${
            tab === "reminders"
              ? "bg-neutral-800 text-white"
              : "text-neutral-500 hover:text-neutral-300"
          }`}
        >
          <Calendar className="h-4 w-4" />
          Reminders
        </button>
      </div>

      {/* Alerts tab */}
      {tab === "alerts" && (
        <div className="space-y-3">
          {alertsLoading ? (
            Array.from({ length: 3 }).map((_, i) => (
              <Card key={i} className="border-neutral-800 bg-neutral-900/50">
                <CardContent className="pt-5 space-y-3">
                  <Skeleton className="h-5 w-24" />
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-4 w-1/2" />
                </CardContent>
              </Card>
            ))
          ) : activeNotifications.length === 0 ? (
            <Card className="border-neutral-800 bg-neutral-900/50">
              <CardContent className="pt-6 pb-6 flex flex-col items-center gap-3 text-center">
                <CheckCircle2 className="h-10 w-10 text-green-500" />
                <p className="text-neutral-400">
                  No active alerts — your glucose is looking good!
                </p>
              </CardContent>
            </Card>
          ) : (
            activeNotifications.map((n: Notification) => (
              <Card key={n.id} className="border-neutral-800 bg-neutral-900/50">
                <CardContent className="pt-5 pb-4 space-y-3">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-2 flex-wrap">
                      <Badge
                        variant="outline"
                        className={severityStyles[n.severity] ?? ""}
                      >
                        {n.severity}
                      </Badge>
                      <span className="text-base font-semibold text-white">
                        {n.title}
                      </span>
                    </div>
                    <span className="text-xs text-neutral-500 whitespace-nowrap flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {relativeTime(n.timestamp)}
                    </span>
                  </div>

                  <p className="text-sm text-neutral-400">{n.message}</p>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4 text-neutral-500" />
                      <span className="text-sm font-medium text-white">
                        {n.glucose_mg_dl} mg/dL
                      </span>
                    </div>

                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="ghost"
                        className="text-neutral-400 hover:text-white"
                        disabled={alertActioning === n.id}
                        onClick={() => handleAlertAction(n.id, "snooze")}
                      >
                        <Clock className="h-3.5 w-3.5 mr-1" />
                        Snooze 30m
                      </Button>
                      <Button
                        size="sm"
                        variant="secondary"
                        disabled={alertActioning === n.id}
                        onClick={() => handleAlertAction(n.id, "acknowledge")}
                      >
                        Dismiss
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      )}

      {/* Reminders tab */}
      {tab === "reminders" && (
        <div className="space-y-3">
          {remindersLoading ? (
            Array.from({ length: 3 }).map((_, i) => (
              <Card key={i} className="border-neutral-800 bg-neutral-900/50">
                <CardContent className="pt-5 space-y-3">
                  <Skeleton className="h-5 w-24" />
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-4 w-1/2" />
                </CardContent>
              </Card>
            ))
          ) : activeReminders.length === 0 ? (
            <Card className="border-neutral-800 bg-neutral-900/50">
              <CardContent className="pt-6 pb-6 flex flex-col items-center gap-3 text-center">
                <CheckCircle2 className="h-10 w-10 text-green-500" />
                <p className="text-neutral-400">
                  All caught up! No pending reminders.
                </p>
              </CardContent>
            </Card>
          ) : (
            activeReminders.map((r: Reminder) => (
              <Card key={r.id} className="border-neutral-800 bg-neutral-900/50">
                <CardContent className="pt-5 pb-4 space-y-3">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-2 flex-wrap">
                      <Badge
                        variant="outline"
                        className={priorityStyles[r.priority] ?? ""}
                      >
                        {r.priority}
                      </Badge>
                      <span className="text-base font-semibold text-white">
                        {r.title}
                      </span>
                    </div>
                  </div>

                  <p className="text-sm text-neutral-400">{r.message}</p>

                  <div className="flex items-center justify-between">
                    <span className="text-xs text-neutral-500 flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      {r.due_context}
                    </span>

                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="ghost"
                        className="text-neutral-400 hover:text-white"
                        disabled={reminderActioning === r.id}
                        onClick={() => handleReminderAction(r.id, "snooze")}
                      >
                        <Clock className="h-3.5 w-3.5 mr-1" />
                        Snooze 7d
                      </Button>
                      <Button
                        size="sm"
                        variant="secondary"
                        disabled={reminderActioning === r.id}
                        onClick={() => handleReminderAction(r.id, "dismiss")}
                      >
                        Dismiss
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      )}
    </div>
  );
}
