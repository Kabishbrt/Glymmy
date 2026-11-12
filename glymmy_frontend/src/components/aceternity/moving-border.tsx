"use client";

import { motion, useAnimationFrame, useMotionTemplate, useMotionValue, useTransform } from "framer-motion";
import { useRef } from "react";
import { cn } from "@/lib/utils";

/**
 * Aceternity-style MovingBorder — an animated gradient border that orbits
 * around a container. Great for CTA buttons and premium cards.
 */
export function MovingBorderButton({
  children,
  className,
  containerClassName,
  borderClassName,
  duration = 3000,
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  children: React.ReactNode;
  className?: string;
  containerClassName?: string;
  borderClassName?: string;
  duration?: number;
}) {
  return (
    <button
      className={cn(
        "relative h-12 w-48 overflow-hidden bg-transparent p-[1px] text-xl",
        containerClassName
      )}
      {...props}
    >
      <div className="absolute inset-0">
        <MovingBorder duration={duration} rx="12%" ry="12%">
          <div
            className={cn(
              "h-20 w-20 bg-[radial-gradient(var(--sky-500)_40%,transparent_60%)] opacity-[0.8]",
              borderClassName
            )}
          />
        </MovingBorder>
      </div>
      <div
        className={cn(
          "relative flex h-full w-full items-center justify-center border border-slate-800 bg-slate-950/[0.9] text-sm text-white antialiased backdrop-blur-xl rounded-lg",
          className
        )}
      >
        {children}
      </div>
    </button>
  );
}

export function MovingBorder({
  children,
  duration = 3000,
  rx = "30%",
  ry = "30%",
}: {
  children: React.ReactNode;
  duration?: number;
  rx?: string;
  ry?: string;
}) {
  const pathRef = useRef<SVGRectElement | null>(null);
  const progress = useMotionValue<number>(0);

  useAnimationFrame((time) => {
    const length = pathRef.current?.getTotalLength();
    if (length) {
      const pxPerMs = length / duration;
      progress.set((time * pxPerMs) % length);
    }
  });

  const x = useTransform(
    progress,
    (val) => pathRef.current?.getPointAtLength(val).x ?? 0
  );
  const y = useTransform(
    progress,
    (val) => pathRef.current?.getPointAtLength(val).y ?? 0
  );
  const transform = useMotionTemplate`translateX(${x}px) translateY(${y}px) translateX(-50%) translateY(-50%)`;

  return (
    <>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        preserveAspectRatio="none"
        className="absolute h-full w-full"
        width="100%"
        height="100%"
      >
        <rect
          fill="none"
          width="100%"
          height="100%"
          rx={rx}
          ry={ry}
          ref={pathRef}
        />
      </svg>
      <motion.div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          display: "inline-block",
          transform,
        }}
      >
        {children}
      </motion.div>
    </>
  );
}
