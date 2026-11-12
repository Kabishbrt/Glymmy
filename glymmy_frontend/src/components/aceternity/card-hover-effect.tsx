"use client";

import { AnimatePresence, motion } from "framer-motion";
import Link from "next/link";
import { useState } from "react";
import { cn } from "@/lib/utils";

/**
 * Aceternity-style CardHoverEffect — a grid of cards where a blurred
 * gradient "spotlight" follows the cursor between cards. Classic on
 * Aceternity landing pages.
 */
export function HoverEffect({
  items,
  className,
}: {
  items: { title: string; description: string; link?: string; icon?: React.ReactNode }[];
  className?: string;
}) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  return (
    <div
      className={cn(
        "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 py-10 gap-4",
        className
      )}
    >
      {items.map((item, idx) => (
        <Link
          href={item.link || "#"}
          key={idx}
          className="relative group block p-2 h-full w-full"
          onMouseEnter={() => setHoveredIndex(idx)}
          onMouseLeave={() => setHoveredIndex(null)}
        >
          <AnimatePresence>
            {hoveredIndex === idx && (
              <motion.span
                className="absolute inset-0 h-full w-full bg-neutral-200/80 dark:bg-slate-800/[0.8] block rounded-3xl"
                layoutId="hover-bg"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1, transition: { duration: 0.15 } }}
                exit={{ opacity: 0, transition: { duration: 0.15, delay: 0.2 } }}
              />
            )}
          </AnimatePresence>
          <Card>
            {item.icon && <div className="mb-3 text-primary">{item.icon}</div>}
            <CardTitle>{item.title}</CardTitle>
            <CardDescription>{item.description}</CardDescription>
          </Card>
        </Link>
      ))}
    </div>
  );
}

const Card = ({ children }: { children: React.ReactNode }) => (
  <div className="rounded-2xl h-full w-full p-4 overflow-hidden bg-white dark:bg-black border border-neutral-200 dark:border-white/[0.2] group-hover:border-slate-700 relative z-20">
    <div className="relative z-50">
      <div className="p-4">{children}</div>
    </div>
  </div>
);

const CardTitle = ({ children }: { children: React.ReactNode }) => (
  <h4 className="text-slate-900 dark:text-zinc-100 font-bold tracking-wide mt-2">{children}</h4>
);

const CardDescription = ({ children }: { children: React.ReactNode }) => (
  <p className="mt-4 text-slate-600 dark:text-zinc-400 tracking-wide leading-relaxed text-sm">
    {children}
  </p>
);
