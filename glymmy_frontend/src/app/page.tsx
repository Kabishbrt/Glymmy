import Link from "next/link";
import {
  Activity,
  Apple,
  FlaskConical,
  MessageSquare,
  QrCode,
  ShieldCheck,
} from "lucide-react";
import { Spotlight } from "@/components/aceternity/spotlight";
import { HoverEffect } from "@/components/aceternity/card-hover-effect";
import { MovingBorderButton } from "@/components/aceternity/moving-border";

const features = [
  {
    title: "Glucose Spike Prediction",
    description:
      "Photograph your meal. Glymmy predicts your glucose spike 30–60 min ahead using your personal trends.",
    icon: <Activity className="h-6 w-6" />,
    link: "/dashboard/glucose",
  },
  {
    title: "Food Scanning",
    description:
      "Multimodal AI identifies every food item and estimates carbs, protein, fat, and fiber.",
    icon: <Apple className="h-6 w-6" />,
    link: "/dashboard/food",
  },
  {
    title: "Lab Report Interpreter",
    description:
      "Upload a blood report. Glymmy flags abnormal values and explains them in plain language.",
    icon: <FlaskConical className="h-6 w-6" />,
    link: "/dashboard/labs",
  },
  {
    title: "AI Health Chat",
    description:
      "Ask anything about your data. RAG-powered context with your full patient history.",
    icon: <MessageSquare className="h-6 w-6" />,
    link: "/dashboard/chat",
  },
  {
    title: "One-QR Sharing",
    description:
      "Share your full health profile with any doctor via a single QR code — FHIR-compliant.",
    icon: <QrCode className="h-6 w-6" />,
    link: "/dashboard",
  },
  {
    title: "Privacy First",
    description:
      "Runs on Gemma 4 locally by default. Your health data never leaves your machine.",
    icon: <ShieldCheck className="h-6 w-6" />,
    link: "/dashboard",
  },
];

export default function LandingPage() {
  return (
    <main className="relative flex min-h-screen w-full flex-col overflow-hidden bg-neutral-950 text-white">
      <Spotlight className="-top-40 left-0 md:-top-20 md:left-60" fill="white" />

      {/* Nav */}
      <nav className="relative z-10 flex items-center justify-between px-6 py-6 md:px-16">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-sky-400 to-indigo-600" />
          <span className="text-xl font-bold tracking-tight">Glymmy</span>
        </div>
        <div className="flex items-center gap-4">
          <Link
            href="/dashboard"
            className="text-sm text-neutral-300 hover:text-white transition"
          >
            Sign in
          </Link>
          <Link
            href="/dashboard"
            className="rounded-full bg-white px-4 py-2 text-sm font-medium text-neutral-900 hover:bg-neutral-200 transition"
          >
            Get started
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative z-10 flex flex-col items-center justify-center px-6 py-20 text-center md:py-32">
        <h1 className="max-w-4xl bg-gradient-to-b from-white to-neutral-400 bg-clip-text text-5xl font-bold leading-tight tracking-tight text-transparent md:text-7xl">
          Your glycemic companion.
        </h1>
        <p className="mt-6 max-w-2xl text-lg text-neutral-400 md:text-xl">
          Glymmy unifies your CGM, wearables, food photos, and lab reports into
          one AI-powered platform — predicting spikes, explaining labs, and
          giving personalized health insights.
        </p>
        <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row">
          <Link href="/dashboard">
            <MovingBorderButton
              containerClassName="w-56 h-14"
              borderClassName="bg-[radial-gradient(#0ea5e9_40%,transparent_60%)]"
            >
              <span className="text-base font-medium">Start for free</span>
            </MovingBorderButton>
          </Link>
          <Link
            href="/dashboard"
            className="rounded-full border border-neutral-700 px-6 py-3 text-sm text-neutral-300 hover:border-neutral-500 hover:text-white transition"
          >
            See a demo →
          </Link>
        </div>

        <div className="mt-12 flex items-center gap-8 text-xs text-neutral-500">
          <span>Powered by Gemma 4</span>
          <span>•</span>
          <span>Real MIMIC-IV + GlucoBench data</span>
          <span>•</span>
          <span>Apache 2.0 stack</span>
        </div>
      </section>

      {/* Features grid */}
      <section className="relative z-10 mx-auto w-full max-w-6xl px-6 py-20">
        <div className="text-center">
          <h2 className="text-3xl font-bold tracking-tight md:text-4xl">
            Everything your health data deserves.
          </h2>
          <p className="mt-3 text-neutral-400">
            Six features. One unified platform. Zero data silos.
          </p>
        </div>
        <HoverEffect items={features} className="mt-10" />
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-neutral-800 px-6 py-8 text-center text-xs text-neutral-500">
        Built for the Harvard HSIL Hackathon 2026 · Team Glymmy
      </footer>
    </main>
  );
}
