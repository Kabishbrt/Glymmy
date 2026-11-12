"use client";

import { useEffect } from "react";
import { useAuth } from "@clerk/nextjs";
import { setTokenProvider } from "@/lib/api-client";

/**
 * Inner component — only rendered when ClerkProvider is present.
 * Hooks are called unconditionally here (Rules of Hooks compliant).
 */
function ClerkTokenBridge({ children }: { children: React.ReactNode }) {
  const { getToken } = useAuth();

  useEffect(() => {
    setTokenProvider(() => getToken());
  }, [getToken]);

  return <>{children}</>;
}

/**
 * Invisible wrapper that wires the Clerk session token into the API client.
 * Mount inside ClerkProvider in the root layout.
 * When auth is disabled, renders children directly with no Clerk dependency.
 */
export function AuthTokenProvider({
  children,
  authEnabled,
}: {
  children: React.ReactNode;
  authEnabled: boolean;
}) {
  if (!authEnabled) {
    return <>{children}</>;
  }
  return <ClerkTokenBridge>{children}</ClerkTokenBridge>;
}
