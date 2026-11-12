"use client";

import { useCallback, useRef, useState } from "react";
import { Upload, Loader2 } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api-client";
import type { ScanResponse, DocumentType } from "@/lib/api-types";

const DOC_TABS: { label: string; value: DocumentType | "auto" }[] = [
  { label: "Auto-detect", value: "auto" },
  { label: "Lab Report", value: "lab_report" },
  { label: "Prescription", value: "prescription" },
  { label: "Food Label", value: "food_label" },
];

export default function ScanPage() {
  const fileRef = useRef<HTMLInputElement>(null);
  const [tab, setTab] = useState<DocumentType | "auto">("auto");
  const [scanning, setScanning] = useState(false);
  const [result, setResult] = useState<ScanResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFile = useCallback(
    async (file: File) => {
      setScanning(true);
      setError(null);
      setResult(null);
      try {
        let res: ScanResponse;
        switch (tab) {
          case "lab_report":
            res = await api.scan.labReport(file);
            break;
          case "prescription":
            res = await api.scan.prescription(file);
            break;
          case "food_label":
            res = await api.scan.foodLabel(file);
            break;
          default:
            res = await api.scan.auto(file);
        }
        setResult(res);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Scan failed");
      } finally {
        setScanning(false);
      }
    },
    [tab],
  );

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      const file = e.dataTransfer.files?.[0];
      if (file) handleFile(file);
    },
    [handleFile],
  );

  const onSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) handleFile(file);
    },
    [handleFile],
  );

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Document Scanner</h1>
        <p className="text-sm text-neutral-400 mt-1">
          Upload any medical document. Glymmy extracts the data automatically.
        </p>
      </div>

      {/* Tab selector */}
      <div className="flex gap-2 flex-wrap">
        {DOC_TABS.map((t) => (
          <button
            key={t.value}
            onClick={() => setTab(t.value)}
            className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              tab === t.value
                ? "bg-sky-600 text-white"
                : "bg-neutral-800 text-neutral-400 hover:text-white hover:bg-neutral-700"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Upload zone */}
      <div
        role="button"
        tabIndex={0}
        onClick={() => fileRef.current?.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={onDrop}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") fileRef.current?.click();
        }}
        className="flex flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed border-neutral-700 bg-neutral-900/50 py-16 cursor-pointer hover:border-sky-600 hover:bg-neutral-900 transition-colors"
      >
        {scanning ? (
          <>
            <Loader2 className="h-10 w-10 text-sky-400 animate-spin" />
            <p className="text-sm text-neutral-300">Analyzing document...</p>
          </>
        ) : (
          <>
            <Upload className="h-10 w-10 text-neutral-500" />
            <p className="text-sm text-neutral-400">
              Drag &amp; drop or click to upload
            </p>
            <p className="text-xs text-neutral-600">
              Accepts images (JPG, PNG, HEIC, etc.)
            </p>
          </>
        )}
        <input
          ref={fileRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={onSelect}
        />
      </div>

      {/* Error */}
      {error && (
        <div className="rounded-lg border border-red-800 bg-red-950/40 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {/* Results */}
      {result && <ScanResults data={result} />}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Results                                                           */
/* ------------------------------------------------------------------ */

function ScanResults({ data }: { data: ScanResponse }) {
  return (
    <div className="space-y-4">
      {/* Confidence badge */}
      <div className="flex items-center gap-3">
        <Badge
          variant="outline"
          className="border-sky-800 text-sky-300 text-xs"
        >
          {data.document_type.replace(/_/g, " ")}
        </Badge>
        <Badge
          variant="outline"
          className="border-neutral-700 text-neutral-400 text-xs"
        >
          Confidence: {Math.round(data.confidence * 100)}%
        </Badge>
      </div>

      {data.document_type === "lab_report" && data.lab_report && (
        <LabReportView data={data} />
      )}
      {data.document_type === "prescription" && data.prescription && (
        <PrescriptionView data={data} />
      )}
      {data.document_type === "food_label" && data.food_label && (
        <FoodLabelView data={data} />
      )}
      {data.document_type === "general" && (
        <GeneralView rawText={data.raw_text} />
      )}
    </div>
  );
}

/* ---- Lab Report -------------------------------------------------- */

function flagColor(flag?: string | null) {
  if (!flag) return "text-neutral-400";
  const f = flag.toLowerCase();
  if (f === "normal" || f === "n") return "text-emerald-400";
  if (f === "critical" || f === "c") return "text-red-400 font-bold";
  if (f === "abnormal" || f === "a" || f === "high" || f === "low")
    return "text-red-400";
  return "text-neutral-400";
}

function LabReportView({ data }: { data: ScanResponse }) {
  const lr = data.lab_report!;
  return (
    <div className="space-y-4">
      {lr.summary && (
        <Card className="border-neutral-800 bg-neutral-900/50">
          <CardContent className="py-4">
            <p className="text-sm text-neutral-300">{lr.summary}</p>
          </CardContent>
        </Card>
      )}

      <div className="overflow-x-auto rounded-lg border border-neutral-800">
        <table className="w-full text-sm">
          <thead className="bg-neutral-900 text-neutral-400">
            <tr>
              <th className="text-left px-4 py-2 font-medium">Test</th>
              <th className="text-left px-4 py-2 font-medium">Value</th>
              <th className="text-left px-4 py-2 font-medium">Unit</th>
              <th className="text-left px-4 py-2 font-medium">
                Reference Range
              </th>
              <th className="text-left px-4 py-2 font-medium">Flag</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-800">
            {lr.tests.map((t, i) => (
              <tr key={i} className="bg-neutral-950/50">
                <td className="px-4 py-2 text-white">{t.key}</td>
                <td className="px-4 py-2 text-white tabular-nums">
                  {t.value}
                </td>
                <td className="px-4 py-2 text-neutral-400">{t.unit ?? "—"}</td>
                <td className="px-4 py-2 text-neutral-400">
                  {t.reference_range ?? "—"}
                </td>
                <td className={`px-4 py-2 ${flagColor(t.flag)}`}>
                  {t.flag ?? "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/* ---- Prescription ------------------------------------------------ */

function PrescriptionView({ data }: { data: ScanResponse }) {
  const rx = data.prescription!;
  return (
    <div className="space-y-4">
      {(rx.doctor_name || rx.date) && (
        <div className="flex gap-4 text-sm text-neutral-400">
          {rx.doctor_name && <span>Doctor: {rx.doctor_name}</span>}
          {rx.date && <span>Date: {rx.date}</span>}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {rx.medications.map((med, i) => (
          <Card key={i} className="border-neutral-800 bg-neutral-900/50">
            <CardContent className="py-4 space-y-1">
              <p className="text-base font-semibold text-white">{med.name}</p>
              <p className="text-sm text-neutral-300">
                {med.dosage} &middot; {med.frequency}
              </p>
              <p className="text-xs text-neutral-500">
                Duration: {med.duration}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

/* ---- Food Label -------------------------------------------------- */

function NutritionRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between py-1.5 border-b border-neutral-800 last:border-0">
      <span className="text-sm text-neutral-400">{label}</span>
      <span className="text-sm text-white tabular-nums">{value}</span>
    </div>
  );
}

function FoodLabelView({ data }: { data: ScanResponse }) {
  const fl = data.food_label!;
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="border-neutral-800 bg-neutral-900/50">
          <CardContent className="py-4">
            <h3 className="text-sm font-medium text-neutral-400 mb-3">
              Nutrition Facts
              {fl.serving_size && (
                <span className="text-neutral-500 ml-2">
                  ({fl.serving_size})
                </span>
              )}
            </h3>
            <NutritionRow
              label="Calories"
              value={fl.calories != null ? `${fl.calories} kcal` : "—"}
            />
            <NutritionRow
              label="Carbs"
              value={fl.carbs_g != null ? `${fl.carbs_g} g` : "—"}
            />
            <NutritionRow
              label="Sugar"
              value={fl.sugar_g != null ? `${fl.sugar_g} g` : "—"}
            />
            <NutritionRow
              label="Protein"
              value={fl.protein_g != null ? `${fl.protein_g} g` : "—"}
            />
            <NutritionRow
              label="Fat"
              value={fl.fat_g != null ? `${fl.fat_g} g` : "—"}
            />
            <NutritionRow
              label="Fiber"
              value={fl.fiber_g != null ? `${fl.fiber_g} g` : "—"}
            />
            <NutritionRow
              label="Sodium"
              value={fl.sodium_mg != null ? `${fl.sodium_mg} mg` : "—"}
            />
          </CardContent>
        </Card>

        {fl.ingredients && fl.ingredients.length > 0 && (
          <Card className="border-neutral-800 bg-neutral-900/50">
            <CardContent className="py-4">
              <h3 className="text-sm font-medium text-neutral-400 mb-3">
                Ingredients
              </h3>
              <p className="text-sm text-neutral-300 leading-relaxed">
                {fl.ingredients.join(", ")}
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

/* ---- General ----------------------------------------------------- */

function GeneralView({ rawText }: { rawText: string }) {
  return (
    <Card className="border-neutral-800 bg-neutral-900/50">
      <CardContent className="py-4">
        <h3 className="text-sm font-medium text-neutral-400 mb-3">
          Extracted Text
        </h3>
        <pre className="whitespace-pre-wrap text-sm text-neutral-300 font-mono leading-relaxed">
          {rawText}
        </pre>
      </CardContent>
    </Card>
  );
}
