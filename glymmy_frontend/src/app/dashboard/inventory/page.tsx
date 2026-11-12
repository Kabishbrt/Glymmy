"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api-client";
import type { HealthInventory } from "@/lib/api-types";
import {
  Pill,
  AlertTriangle,
  Heart,
  Phone,
  Droplets,
  Shield,
  Stethoscope,
  FileText,
  Trash2,
} from "lucide-react";

const severityColor: Record<string, string> = {
  mild: "bg-amber-900/50 text-amber-300 border-amber-800",
  moderate: "bg-orange-900/50 text-orange-300 border-orange-800",
  severe: "bg-red-900/50 text-red-300 border-red-800",
};

const statusColor: Record<string, string> = {
  active: "bg-red-900/50 text-red-300 border-red-800",
  managed: "bg-sky-900/50 text-sky-300 border-sky-800",
  resolved: "bg-emerald-900/50 text-emerald-300 border-emerald-800",
};

export default function InventoryPage() {
  const [inventory, setInventory] = useState<HealthInventory | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchInventory = () => {
    api.me.inventory()
      .then(setInventory)
      .catch(() => setInventory(null))
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchInventory(); }, []);

  async function removeItem(category: string, index: number) {
    await api.me.removeInventoryItem(category, index);
    fetchInventory();
  }

  if (loading) {
    return (
      <div className="space-y-6 max-w-5xl">
        <Skeleton className="h-8 w-64" />
        {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-32 w-full" />)}
      </div>
    );
  }

  if (!inventory) {
    return (
      <div className="space-y-6 max-w-5xl">
        <h1 className="text-2xl font-bold text-white">Health Card</h1>
        <p className="text-neutral-500">No health inventory data yet.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-5xl">
      <div>
        <h1 className="text-2xl font-bold text-white">Health Card</h1>
        <p className="text-neutral-500 mt-1">Your personal health record</p>
      </div>

      {/* General Info */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <InfoCard icon={<Droplets className="h-4 w-4 text-red-400" />} label="Blood Type" value={inventory.blood_type || "—"} />
        <InfoCard icon={<Stethoscope className="h-4 w-4 text-sky-400" />} label="Physician" value={inventory.primary_physician || "—"} />
        <InfoCard icon={<Shield className="h-4 w-4 text-emerald-400" />} label="Insurance" value={inventory.insurance_provider || "—"} />
        <InfoCard icon={<FileText className="h-4 w-4 text-violet-400" />} label="Insurance ID" value={inventory.insurance_id || "—"} />
      </div>

      {/* Medications */}
      <Card className="border-neutral-800 bg-neutral-900/50">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Pill className="h-5 w-5 text-sky-400" />
            Medications ({inventory.medications.length})
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {inventory.medications.length === 0 ? (
            <p className="text-sm text-neutral-500">No medications on record</p>
          ) : (
            inventory.medications.map((med, i) => (
              <div key={i} className="flex items-center justify-between rounded-lg border border-neutral-800 bg-neutral-800/30 p-3">
                <div>
                  <p className="font-medium text-white">{med.name} — {med.dosage}</p>
                  <p className="text-xs text-neutral-500">{med.frequency} · Prescribed by {med.prescriber || "—"}</p>
                  {med.notes && <p className="text-xs text-neutral-600 mt-1">{med.notes}</p>}
                </div>
                <Button variant="ghost" size="sm" className="text-neutral-600 hover:text-red-400" onClick={() => removeItem("medications", i)}>
                  <Trash2 className="h-3 w-3" />
                </Button>
              </div>
            ))
          )}
        </CardContent>
      </Card>

      {/* Allergies */}
      <Card className="border-neutral-800 bg-neutral-900/50">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-orange-400" />
            Allergies ({inventory.allergies.length})
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {inventory.allergies.length === 0 ? (
            <p className="text-sm text-neutral-500">No known allergies</p>
          ) : (
            inventory.allergies.map((a, i) => (
              <div key={i} className="flex items-center justify-between rounded-lg border border-neutral-800 bg-neutral-800/30 p-3">
                <div>
                  <div className="flex items-center gap-2">
                    <p className="font-medium text-white">{a.allergen}</p>
                    <span className={`text-xs px-2 py-0.5 rounded-full border ${severityColor[a.severity] || severityColor.mild}`}>{a.severity}</span>
                  </div>
                  <p className="text-xs text-neutral-500 mt-1">Reaction: {a.reaction}</p>
                </div>
                <Button variant="ghost" size="sm" className="text-neutral-600 hover:text-red-400" onClick={() => removeItem("allergies", i)}>
                  <Trash2 className="h-3 w-3" />
                </Button>
              </div>
            ))
          )}
        </CardContent>
      </Card>

      {/* Conditions */}
      <Card className="border-neutral-800 bg-neutral-900/50">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Heart className="h-5 w-5 text-rose-400" />
            Conditions ({inventory.conditions.length})
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {inventory.conditions.length === 0 ? (
            <p className="text-sm text-neutral-500">No conditions on record</p>
          ) : (
            inventory.conditions.map((c, i) => (
              <div key={i} className="flex items-center justify-between rounded-lg border border-neutral-800 bg-neutral-800/30 p-3">
                <div>
                  <div className="flex items-center gap-2">
                    <p className="font-medium text-white">{c.name}</p>
                    <span className={`text-xs px-2 py-0.5 rounded-full border ${statusColor[c.status] || statusColor.active}`}>{c.status}</span>
                  </div>
                  <p className="text-xs text-neutral-500 mt-1">
                    Diagnosed: {c.diagnosed_date || "—"}{c.notes ? ` · ${c.notes}` : ""}
                  </p>
                </div>
                <Button variant="ghost" size="sm" className="text-neutral-600 hover:text-red-400" onClick={() => removeItem("conditions", i)}>
                  <Trash2 className="h-3 w-3" />
                </Button>
              </div>
            ))
          )}
        </CardContent>
      </Card>

      {/* Emergency Contacts */}
      <Card className="border-neutral-800 bg-neutral-900/50">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Phone className="h-5 w-5 text-emerald-400" />
            Emergency Contacts ({inventory.emergency_contacts.length})
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {inventory.emergency_contacts.length === 0 ? (
            <p className="text-sm text-neutral-500">No emergency contacts</p>
          ) : (
            inventory.emergency_contacts.map((c, i) => (
              <div key={i} className="flex items-center justify-between rounded-lg border border-neutral-800 bg-neutral-800/30 p-3">
                <div>
                  <p className="font-medium text-white">{c.name}</p>
                  <p className="text-xs text-neutral-500">{c.relationship} · {c.phone}{c.email ? ` · ${c.email}` : ""}</p>
                </div>
                <Button variant="ghost" size="sm" className="text-neutral-600 hover:text-red-400" onClick={() => removeItem("emergency_contacts", i)}>
                  <Trash2 className="h-3 w-3" />
                </Button>
              </div>
            ))
          )}
        </CardContent>
      </Card>

      {/* Notes */}
      {inventory.notes && (
        <Card className="border-neutral-800 bg-neutral-900/50">
          <CardContent className="py-4">
            <p className="text-sm text-neutral-400">{inventory.notes}</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function InfoCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <Card className="border-neutral-800 bg-neutral-900/50">
      <CardContent className="py-4">
        <div className="flex items-center gap-2 mb-2">
          {icon}
          <span className="text-xs text-neutral-500">{label}</span>
        </div>
        <p className="text-sm font-medium text-white truncate">{value}</p>
      </CardContent>
    </Card>
  );
}
