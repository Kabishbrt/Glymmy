// Next.js 16 uses `proxy.ts` (renamed from middleware.ts).
// When Clerk is configured, clerkMiddleware protects /dashboard routes.
// When Clerk is not configured, all requests pass through.
import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";

const CLERK_KEY = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;
const AUTH_ENABLED =
  process.env.NEXT_PUBLIC_ENABLE_AUTH !== "false" && Boolean(CLERK_KEY);

const isProtectedRoute = createRouteMatcher(["/dashboard(.*)"]);

export default clerkMiddleware(async (auth, req) => {
  if (!AUTH_ENABLED) {
    return NextResponse.next();
  }
  if (isProtectedRoute(req)) {
    await auth.protect();
  }
});

export const config = {
  matcher: [
    // Skip Next.js internals and all static files
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    // Always run for API routes
    "/(api|trpc)(.*)",
  ],
};
