"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api-client";
import type { ShareConfig, ShareResponse } from "@/lib/api-types";
import { QrCode, Copy, Check, Mail, Link2 } from "lucide-react";

const toggles: Array<{ key: keyof ShareConfig; label: string; desc: string }> = [
  { key: "include_profile", label: "Profile", desc: "Name, age, diagnosis, A1C" },
  { key: "include_glucose", label: "Glucose Data", desc: "Latest CGM reading, 24h summary" },
  { key: "include_vitals", label: "Vitals", desc: "Heart rate, SpO2, steps" },
  { key: "include_medications", label: "Medications", desc: "Current medication list" },
  { key: "include_conditions", label: "Conditions", desc: "Active health conditions" },
];

export default function SharePage() {
  const [config, setConfig] = useState<ShareConfig>({
    include_profile: true,
    include_glucose: true,
    include_vitals: true,
    include_medications: true,
    include_conditions: true,
  });
  const [result, setResult] = useState<ShareResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  async function generateShare() {
    setLoading(true);
    try {
      const res = await api.me.createShare(config);
      setResult(res);
    } catch (err) {
      console.error("Share failed:", err);
    } finally {
      setLoading(false);
    }
  }

  function copyLink() {
    if (!result) return;
    navigator.clipboard.writeText(result.share_url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  function emailLink() {
    if (!result) return;
    const subject = encodeURIComponent("My Glymmy Health Summary");
    const body = encodeURIComponent(`Here's my health data from Glymmy:\n\n${result.share_url}`);
    window.open(`mailto:?subject=${subject}&body=${body}`);
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold text-white">Share Health Data</h1>
        <p className="text-neutral-500 mt-1">
          Generate a QR code or shareable link. Choose what data to include.
        </p>
      </div>

      {/* Data selection */}
      <Card className="border-neutral-800 bg-neutral-900/50">
        <CardHeader>
          <CardTitle className="text-white">What to share</CardTitle>
          <CardDescription className="text-neutral-500">Toggle the data sections you want to include</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {toggles.map((t) => (
            <label key={t.key} className="flex items-center justify-between rounded-lg border border-neutral-800 bg-neutral-800/30 p-3 cursor-pointer hover:bg-neutral-800/50 transition">
              <div>
                <p className="text-sm font-medium text-white">{t.label}</p>
                <p className="text-xs text-neutral-500">{t.desc}</p>
              </div>
              <input
                type="checkbox"
                checked={config[t.key] ?? true}
                onChange={(e) => setConfig({ ...config, [t.key]: e.target.checked })}
                className="h-4 w-4 rounded border-neutral-600 bg-neutral-800 text-sky-500 focus:ring-sky-500"
              />
            </label>
          ))}

          <Button onClick={generateShare} disabled={loading} className="w-full mt-4 bg-sky-600 hover:bg-sky-500">
            {loading ? "Generating..." : (
              <>
                <QrCode className="h-4 w-4 mr-2" />
                Generate Share Link
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Result */}
      {result && (
        <Card className="border-sky-900/50 bg-sky-950/20">
          <CardContent className="py-6 space-y-6">
            {/* QR Code */}
            <div className="flex justify-center">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={result.qr_data_url}
                alt="Share QR Code"
                className="h-48 w-48 rounded-lg bg-white p-2"
              />
            </div>

            {/* URL */}
            <div className="flex items-center gap-2 rounded-lg border border-neutral-700 bg-neutral-800/50 p-3">
              <Link2 className="h-4 w-4 text-neutral-500 flex-shrink-0" />
              <code className="flex-1 text-xs text-neutral-300 truncate">{result.share_url}</code>
              <Button variant="ghost" size="sm" onClick={copyLink} className="text-neutral-400 hover:text-white">
                {copied ? <Check className="h-4 w-4 text-emerald-400" /> : <Copy className="h-4 w-4" />}
              </Button>
            </div>

            {/* Actions */}
            <div className="flex gap-3">
              <Button variant="outline" onClick={copyLink} className="flex-1 border-neutral-700 text-neutral-300 hover:bg-neutral-800">
                <Copy className="h-4 w-4 mr-2" />
                {copied ? "Copied!" : "Copy Link"}
              </Button>
              <Button variant="outline" onClick={emailLink} className="flex-1 border-neutral-700 text-neutral-300 hover:bg-neutral-800">
                <Mail className="h-4 w-4 mr-2" />
                Email Link
              </Button>
            </div>

            <p className="text-xs text-neutral-600 text-center">
              Anyone with this link can view the selected health data
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
