"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { api } from "@/lib/api-client";
import type { SharedData } from "@/lib/api-types";
import { Activity, Heart, Pill, Stethoscope, Download } from "lucide-react";

export default function PublicSharePage() {
  const params = useParams();
  const token = params.token as string;
  const [data, setData] = useState<SharedData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isDownloading, setIsDownloading] = useState(false);

  useEffect(() => {
    api.share
      .getData(token)
      .then(setData)
      .catch(() => setError("This share link is invalid or has expired."))
      .finally(() => setLoading(false));
  }, [token]);

  const handleDownload = async () => {
    if (!data) return;
    setIsDownloading(true);
    try {
      const { toPng } = await import("html-to-image");
      const { jsPDF } = await import("jspdf");
      
      const element = document.getElementById("pdf-content");
      if (!element) return;
      
      const dataUrl = await toPng(element, { 
        quality: 0.95, 
        backgroundColor: '#0a0a0a',
        pixelRatio: 2,
        filter: (node) => {
          if (node?.id === 'download-btn') return false;
          return true;
        }
      });
      
      // Extract image properties to create a perfectly fitting canvas
      const tempPdf = new jsPDF();
      const imgProps = tempPdf.getImageProperties(dataUrl);

      const pdf = new jsPDF({
        orientation: "portrait",
        unit: "px",
        format: [imgProps.width, imgProps.height]
      });

      pdf.setFillColor("#0a0a0a");
      pdf.rect(0, 0, imgProps.width, imgProps.height + 10, "F");

      pdf.addImage(dataUrl, 'PNG', 0, 0, imgProps.width, imgProps.height);
      
      pdf.save(`${data.user_name.replace(/ /g, "_")}_Glymmy_Report.pdf`);
    } catch (err) {
      console.error("PDF generation failed:", err);
    } finally {
      setIsDownloading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-neutral-950 p-8">
        <div className="max-w-2xl mx-auto space-y-6">
          <Skeleton className="h-10 w-64" />
          {Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-32 w-full" />)}
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-neutral-950 flex items-center justify-center">
        <Card className="border-neutral-800 bg-neutral-900/50 max-w-md">
          <CardContent className="py-12 text-center">
            <p className="text-lg text-neutral-400">{error || "No data found"}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-950 flex justify-center py-4 md:py-8">
      <div id="pdf-content" className="w-full max-w-5xl bg-neutral-950 px-4 md:px-8 pb-4 space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-neutral-800 pb-6 print:border-b-gray-400">
          <div className="flex items-center gap-4">
            <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-sky-400 to-indigo-600 shadow-lg shadow-sky-900/20" />
            <div>
              <h1 className="text-3xl font-bold text-white tracking-tight">{data.user_name}</h1>
              <p className="text-sm text-neutral-500 mt-1">Medical Report generated on {new Date(data.shared_at).toLocaleString()}</p>
            </div>
          </div>
          <Button 
            id="download-btn"
            variant="outline" 
            onClick={handleDownload} 
            disabled={isDownloading}
            className="gap-2 border-neutral-700 hover:bg-neutral-800 hover:text-white bg-neutral-900 text-neutral-300 self-start md:self-auto shadow-sm transition-all"
          >
            <Download className="h-4 w-4" />
            {isDownloading ? "Generating PDF..." : "Download PDF"}
          </Button>
        </div>

        {/* Profile */}
        {data.profile && (
          <Card className="border-neutral-800 bg-neutral-900/40 backdrop-blur shadow-xl print:break-inside-avoid">
            <CardHeader className="pb-4">
              <CardTitle className="text-white flex items-center gap-2 text-xl font-semibold">
                <Stethoscope className="h-5 w-5 text-sky-400" />
                Patient Profile
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableBody>
                  {"age" in data.profile && <TableRow className="border-neutral-800 hover:bg-transparent"><TableCell className="font-medium w-1/3 text-neutral-500 text-sm uppercase tracking-wider">Age</TableCell><TableCell className="text-white md:text-lg">{String(data.profile.age)}</TableCell></TableRow>}
                  {"diagnosis" in data.profile && <TableRow className="border-neutral-800 hover:bg-transparent"><TableCell className="font-medium text-neutral-500 text-sm uppercase tracking-wider">Diagnosis</TableCell><TableCell className="text-white font-medium">{String(data.profile.diagnosis)}</TableCell></TableRow>}
                  {"a1c" in data.profile && <TableRow className="border-neutral-800 hover:bg-transparent"><TableCell className="font-medium text-neutral-500 text-sm uppercase tracking-wider">A1C Level</TableCell><TableCell className="text-white md:text-lg">{String(data.profile.a1c)}%</TableCell></TableRow>}
                  {"blood_type" in data.profile && <TableRow className="border-neutral-800 hover:bg-transparent"><TableCell className="font-medium text-neutral-500 text-sm uppercase tracking-wider">Blood Type</TableCell><TableCell className="text-white font-medium">{String(data.profile.blood_type)}</TableCell></TableRow>}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}

        {/* Glucose */}
        {data.glucose_summary && (
          <Card className="border-neutral-800 bg-neutral-900/40 backdrop-blur shadow-xl print:break-inside-avoid">
            <CardHeader className="pb-4">
              <CardTitle className="text-white flex items-center gap-2 text-xl font-semibold">
                <Activity className="h-5 w-5 text-emerald-400" />
                Glucose Summary (24h)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader className="bg-neutral-950/50">
                  <TableRow className="border-neutral-800 border-b hover:bg-transparent">
                    <TableHead className="text-neutral-500 text-sm uppercase tracking-wider">Metric</TableHead>
                    <TableHead className="text-right text-neutral-500 text-sm uppercase tracking-wider">Value</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {"current" in data.glucose_summary && <TableRow className="border-neutral-800 hover:bg-transparent"><TableCell className="font-medium text-white">Current Reading</TableCell><TableCell className="text-right text-white font-medium text-lg">{Math.round(Number(data.glucose_summary.current))} mg/dL</TableCell></TableRow>}
                  {"mean" in data.glucose_summary && <TableRow className="border-neutral-800 hover:bg-transparent"><TableCell className="font-medium text-white">Average</TableCell><TableCell className="text-right text-neutral-300">{Math.round(Number(data.glucose_summary.mean))} mg/dL</TableCell></TableRow>}
                  {"min" in data.glucose_summary && <TableRow className="border-neutral-800 hover:bg-transparent"><TableCell className="font- medium text-white">Minimum</TableCell><TableCell className="text-right text-neutral-300">{Math.round(Number(data.glucose_summary.min))} mg/dL</TableCell></TableRow>}
                  {"max" in data.glucose_summary && <TableRow className="border-neutral-800 hover:bg-transparent"><TableCell className="font-medium text-white">Maximum</TableCell><TableCell className="text-right text-neutral-300">{Math.round(Number(data.glucose_summary.max))} mg/dL</TableCell></TableRow>}
                  {"readings_count" in data.glucose_summary && <TableRow className="border-neutral-800 hover:bg-transparent"><TableCell className="font-medium text-white">Total Readings</TableCell><TableCell className="text-right text-neutral-500">{String(data.glucose_summary.readings_count)}</TableCell></TableRow>}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}

        {/* Vitals */}
        {data.vitals && (
          <Card className="border-neutral-800 bg-neutral-900/40 backdrop-blur shadow-xl print:break-inside-avoid">
            <CardHeader className="pb-4">
              <CardTitle className="text-white flex items-center gap-2 text-xl font-semibold">
                <Heart className="h-5 w-5 text-rose-400" />
                Vitals
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                 <TableBody>
                  {"heart_rate_bpm" in data.vitals && <TableRow className="border-neutral-800 hover:bg-transparent"><TableCell className="font-medium w-1/3 text-neutral-500 text-sm uppercase tracking-wider">Heart Rate</TableCell><TableCell className="text-white md:text-lg">{String(data.vitals.heart_rate_bpm)} <span className="text-sm text-neutral-500 ml-1">bpm</span></TableCell></TableRow>}
                  {"spo2_pct" in data.vitals && <TableRow className="border-neutral-800 hover:bg-transparent"><TableCell className="font-medium text-neutral-500 text-sm uppercase tracking-wider">Blood Oxygen (SpO2)</TableCell><TableCell className="text-white md:text-lg">{String(data.vitals.spo2_pct)}<span className="text-sm text-neutral-500 ml-1">%</span></TableCell></TableRow>}
                  {"steps" in data.vitals && <TableRow className="border-neutral-800 hover:bg-transparent"><TableCell className="font-medium text-neutral-500 text-sm uppercase tracking-wider">Daily Steps</TableCell><TableCell className="text-white font-medium">{String(data.vitals.steps)}</TableCell></TableRow>}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}

        <div className="grid md:grid-cols-2 gap-8 print:block">
          {/* Medications */}
          {data.medications && data.medications.length > 0 && (
            <div className="print:mb-8 print:break-inside-avoid">
              <h2 className="text-white text-xl font-bold flex items-center gap-2 mb-4">
                <Pill className="h-5 w-5 text-sky-400" />
                Medications
              </h2>
              <div className="rounded-xl border border-neutral-800 bg-neutral-900/60 shadow-lg overflow-hidden">
                <Table>
                  <TableHeader className="bg-neutral-950/80">
                    <TableRow className="border-neutral-800 hover:bg-transparent">
                      <TableHead className="text-neutral-500 text-xs uppercase tracking-widest">Name & Dosage</TableHead>
                      <TableHead className="text-neutral-500 text-xs uppercase tracking-widest">Frequency</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {data.medications.map((m, i) => (
                      <TableRow key={i} className="border-neutral-800 hover:bg-transparent">
                        <TableCell className="text-white font-medium">{m.name} {m.dosage ? <span className="text-sky-300 ml-1">({m.dosage})</span> : ""}</TableCell>
                        <TableCell className="text-neutral-400">{m.frequency}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </div>
          )}

          {/* Conditions */}
          {data.conditions && data.conditions.length > 0 && (
            <div className="print:mb-8 print:break-inside-avoid">
              <h2 className="text-white text-xl font-bold flex items-center gap-2 mb-4">
                <Heart className="h-5 w-5 text-rose-400" />
                Conditions
              </h2>
              <div className="rounded-xl border border-neutral-800 bg-neutral-900/60 shadow-lg overflow-hidden">
                <Table>
                  <TableHeader className="bg-neutral-950/80">
                    <TableRow className="border-neutral-800 hover:bg-transparent">
                      <TableHead className="text-neutral-500 text-xs uppercase tracking-widest">Condition</TableHead>
                      <TableHead className="text-neutral-500 text-xs uppercase tracking-widest">Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {data.conditions.map((c, i) => (
                      <TableRow key={i} className="border-neutral-800 hover:bg-transparent">
                        <TableCell className="text-white font-medium">{c.name}</TableCell>
                        <TableCell>
                          <Badge variant="outline" className="border-neutral-700 bg-neutral-800/80 text-neutral-300 hover:bg-neutral-800">{c.status}</Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <p className="border-t border-neutral-800 mt-8 pt-6 text-xs text-neutral-600 text-center tracking-wide">
          Powered by Glymmy — Your Medical Copilot · Valid on {new Date(data.shared_at).toLocaleDateString()}
        </p>
      </div>
    </div>
  );
}
