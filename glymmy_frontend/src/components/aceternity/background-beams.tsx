"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";

/**
 * Aceternity-style BackgroundBeams — animated SVG beams sweeping across
 * a container. Designed for hero sections and empty-state backgrounds.
 */
export function BackgroundBeams({ className }: { className?: string }) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  if (!mounted) return null;

  const paths = [
    "M-380 -189C-380 -189 -312 216 152 343C616 470 684 875 684 875",
    "M-373 -197C-373 -197 -305 208 159 335C623 462 691 867 691 867",
    "M-366 -205C-366 -205 -298 200 166 327C630 454 698 859 698 859",
    "M-359 -213C-359 -213 -291 192 173 319C637 446 705 851 705 851",
    "M-352 -221C-352 -221 -284 184 180 311C644 438 712 843 712 843",
  ];

  return (
    <div
      className={cn(
        "absolute inset-0 h-full w-full overflow-hidden bg-neutral-950",
        className
      )}
    >
      <svg
        className="pointer-events-none absolute z-0 h-full w-full"
        width="100%"
        height="100%"
        viewBox="0 0 696 316"
        fill="none"
      >
        {paths.map((d, idx) => (
          <motion.path
            key={`beam-${idx}`}
            d={d}
            stroke={`url(#beam-grad-${idx})`}
            strokeWidth="0.5"
            strokeOpacity="0.4"
          />
        ))}
        <defs>
          {paths.map((_, idx) => (
            <motion.linearGradient
              id={`beam-grad-${idx}`}
              key={`grad-${idx}`}
              initial={{ x1: "0%", x2: "0%", y1: "0%", y2: "0%" }}
              animate={{
                x1: ["0%", "100%"],
                x2: ["0%", "95%"],
                y1: ["0%", "100%"],
                y2: ["0%", "99%"],
              }}
              transition={{
                duration: Math.random() * 10 + 10,
                ease: "easeInOut",
                repeat: Infinity,
                delay: Math.random() * 10,
              }}
            >
              <stop stopColor="#18CCFC" stopOpacity="0" />
              <stop stopColor="#18CCFC" />
              <stop offset="32.5%" stopColor="#6344F5" />
              <stop offset="100%" stopColor="#AE48FF" stopOpacity="0" />
            </motion.linearGradient>
          ))}
        </defs>
      </svg>
    </div>
  );
}
