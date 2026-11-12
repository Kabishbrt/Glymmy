"use client";

import { createContext, useContext, useEffect, useState } from "react";
import type { Patient } from "@/lib/api-types";
import { api } from "@/lib/api-client";

interface PatientContextValue {
  patients: Patient[];
  selected: Patient | null;
  setSelected: (p: Patient) => void;
  loading: boolean;
}

const Ctx = createContext<PatientContextValue | undefined>(undefined);

export function PatientProvider({ children }: { children: React.ReactNode }) {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [selected, setSelected] = useState<Patient | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let alive = true;
    api.patients
      .list()
      .then((res) => {
        if (!alive) return;
        setPatients(res.patients);
        if (res.patients.length > 0) {
          // Prefer a Dubosson T1D patient as default (rich data)
          const t1d = res.patients.find((p) => p.source === "dubosson");
          setSelected(t1d || res.patients[0]);
        }
      })
      .catch(() => {})
      .finally(() => alive && setLoading(false));
    return () => {
      alive = false;
    };
  }, []);

  return (
    <Ctx.Provider value={{ patients, selected, setSelected, loading }}>
      {children}
    </Ctx.Provider>
  );
}

export function usePatient() {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("usePatient must be used within PatientProvider");
  return ctx;
}
