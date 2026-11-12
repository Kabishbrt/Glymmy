"use client";

import { usePatient } from "./patient-context";
import { ChevronsUpDown, User } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { useState } from "react";

export function PatientSelector() {
  const { patients, selected, setSelected, loading } = usePatient();
  const [open, setOpen] = useState(false);

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="flex w-full items-center justify-between rounded-lg border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 px-3 py-2 text-sm hover:bg-neutral-50 dark:hover:bg-neutral-800 transition"
      >
        <div className="flex items-center gap-2 min-w-0">
          <User className="h-4 w-4 flex-shrink-0 text-neutral-500" />
          <span className="truncate">
            {loading
              ? "Loading..."
              : selected
              ? selected.name
              : "Select patient"}
          </span>
        </div>
        <ChevronsUpDown className="h-4 w-4 text-neutral-400" />
      </button>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Choose a patient</DialogTitle>
        </DialogHeader>
        <div className="space-y-2 max-h-[60vh] overflow-y-auto">
          {patients.map((p) => (
            <button
              key={p.id}
              onClick={() => {
                setSelected(p);
                setOpen(false);
              }}
              className="w-full flex flex-col items-start gap-1 rounded-lg border border-neutral-200 dark:border-neutral-800 p-3 text-left hover:bg-neutral-50 dark:hover:bg-neutral-900 transition"
            >
              <div className="flex items-center gap-2 w-full">
                <span className="font-medium">{p.name}</span>
                <Badge variant="secondary" className="text-xs">
                  {p.source}
                </Badge>
                {p.diagnosis && (
                  <span className="text-xs text-neutral-500 ml-auto">
                    {p.diagnosis}
                  </span>
                )}
              </div>
              <div className="text-xs text-neutral-500 flex gap-3">
                {p.num_readings && <span>{p.num_readings} readings</span>}
                {p.num_lab_events && <span>{p.num_lab_events} lab events</span>}
                {p.num_abnormal && (
                  <span className="text-danger">
                    {p.num_abnormal} abnormal
                  </span>
                )}
              </div>
            </button>
          ))}
        </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
