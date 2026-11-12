"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api-client";
import type { LabEventsResponse, LabInterpretation } from "@/lib/api-types";
import { AlertCircle, Loader2, ScanLine, FileText } from "lucide-react";

export default function LabsPage() {
  const [events, setEvents] = useState<LabEventsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [interpretation, setInterpretation] = useState<LabInterpretation | null>(null);
  const [interpreting, setInterpreting] = useState(false);

  // Load demo MIMIC data for demonstration
  useEffect(() => {
    setLoading(true);
    api.labs
      .list("mimic_10006")
      .then(setEvents)
      .catch(() => setEvents(null))
      .finally(() => setLoading(false));
  }, []);

  async function handleInterpret() {
    setInterpreting(true);
    try {
      const res = await api.labs.interpret("mimic_10006");
      setInterpretation(res);
    } finally {
      setInterpreting(false);
    }
  }

  return (
    <div className="space-y-6 max-w-5xl">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Lab Results</h1>
          <p className="text-neutral-500 mt-1">
            Clinical lab data with AI-powered interpretation
          </p>
        </div>
        <div className="flex gap-2">
          <Link href="/dashboard/scan">
            <Button variant="outline" className="border-neutral-700 text-neutral-300 hover:bg-neutral-800">
              <ScanLine className="h-4 w-4 mr-2" />
              Scan Lab Report
            </Button>
          </Link>
          <Button onClick={handleInterpret} disabled={interpreting || !events} className="bg-sky-600 hover:bg-sky-500">
            {interpreting ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Interpreting...
              </>
            ) : (
              <>
                <FileText className="h-4 w-4 mr-2" />
                Interpret with AI
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Scan CTA */}
      {!events && !loading && (
        <Card className="border-dashed border-neutral-700 bg-neutral-900/30">
          <CardContent className="py-12 text-center">
            <ScanLine className="h-12 w-12 text-neutral-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-white mb-2">No Lab Reports Yet</h3>
            <p className="text-neutral-500 mb-4">Upload a lab report to get AI-powered interpretation</p>
            <Link href="/dashboard/scan">
              <Button className="bg-sky-600 hover:bg-sky-500">
                <ScanLine className="h-4 w-4 mr-2" />
                Scan Lab Report
              </Button>
            </Link>
          </CardContent>
        </Card>
      )}

      {interpretation && (
        <Card className="border-sky-900/50 bg-sky-950/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-white">
              <AlertCircle className="h-5 w-5 text-sky-400" />
              AI Interpretation
            </CardTitle>
            <CardDescription className="text-neutral-400">{interpretation.summary}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-3 sm:grid-cols-4">
              <RiskPill label="Diabetes" level={interpretation.risk_assessment.diabetes_risk} />
              <RiskPill label="Cardiovascular" level={interpretation.risk_assessment.cardiovascular_risk} />
              <RiskPill label="Liver" level={interpretation.risk_assessment.liver_risk} />
              <RiskPill label="Kidney" level={interpretation.risk_assessment.kidney_risk} />
            </div>

            {interpretation.abnormal_markers.map((m, idx) => (
              <Alert key={idx} className="bg-red-950/20 border-red-900/50">
                <AlertTitle className="flex items-center gap-2 text-red-300">
                  {m.test}: {m.value} {m.unit}{" "}
                  <Badge variant="outline" className="border-red-800 text-red-300">{m.status}</Badge>
                  <Badge variant="outline" className="border-orange-800 text-orange-300">{m.severity}</Badge>
                </AlertTitle>
                <AlertDescription className="text-neutral-400">
                  <p className="mt-1">{m.explanation}</p>
                  <ul className="mt-2 list-disc pl-5 text-xs">
                    {m.actions.map((a, i) => <li key={i}>{a}</li>)}
                  </ul>
                </AlertDescription>
              </Alert>
            ))}

            <div>
              <h4 className="font-semibold text-sm mb-2 text-white">Recommendations</h4>
              <ul className="list-disc pl-5 space-y-1 text-sm text-neutral-400">
                {interpretation.recommendations.map((r, i) => <li key={i}>{r}</li>)}
              </ul>
            </div>
          </CardContent>
        </Card>
      )}

      {(events || loading) && (
        <Card className="border-neutral-800 bg-neutral-900/50">
          <CardHeader>
            <CardTitle className="text-white">Recent Lab Events</CardTitle>
            <CardDescription className="text-neutral-500">
              {events ? `${events.total} events` : "Loading..."}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-2">
                {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-10 w-full" />)}
              </div>
            ) : events ? (
              <Table>
                <TableHeader>
                  <TableRow className="border-neutral-800">
                    <TableHead className="text-neutral-400">Test</TableHead>
                    <TableHead className="text-neutral-400">Value</TableHead>
                    <TableHead className="text-neutral-400">Normal Range</TableHead>
                    <TableHead className="text-neutral-400">Flag</TableHead>
                    <TableHead className="text-neutral-400">Date</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {events.events.slice(0, 20).map((e, idx) => (
                    <TableRow key={idx} className={`border-neutral-800 ${e.flag === "abnormal" ? "bg-red-950/10" : ""}`}>
                      <TableCell className="font-medium text-white">{e.test}</TableCell>
                      <TableCell className="text-white">{e.value ?? e.raw_value} {e.unit}</TableCell>
                      <TableCell className="text-neutral-500 text-sm">
                        {e.ref_low != null && e.ref_high != null ? `${e.ref_low}–${e.ref_high}` : "—"}
                      </TableCell>
                      <TableCell>
                        {e.flag === "abnormal" ? (
                          <Badge className="bg-red-900/50 text-red-300 border-red-800">Abnormal</Badge>
                        ) : (
                          <Badge className="bg-neutral-800 text-neutral-300 border-neutral-700">Normal</Badge>
                        )}
                      </TableCell>
                      <TableCell className="text-xs text-neutral-500">
                        {e.charttime ? new Date(e.charttime).toLocaleDateString() : "—"}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : null}
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function RiskPill({ label, level }: { label: string; level: string }) {
  const color =
    level === "high"
      ? "bg-red-950/30 text-red-300 border-red-900/50"
      : level === "moderate"
      ? "bg-amber-950/30 text-amber-300 border-amber-900/50"
      : "bg-emerald-950/30 text-emerald-300 border-emerald-900/50";
  return (
    <div className={`rounded-lg border p-3 text-center ${color}`}>
      <div className="text-xs uppercase tracking-wide">{label}</div>
      <div className="text-sm font-bold mt-1">{level}</div>
    </div>
  );
}
