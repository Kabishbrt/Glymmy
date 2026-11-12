import { auth } from "@clerk/nextjs/server";
import { SignUp } from "@clerk/nextjs";
import { redirect } from "next/navigation";
import { Spotlight } from "@/components/aceternity/spotlight";
import { isAuthEnabledServer } from "@/lib/auth-config";

export default async function SignUpPage() {
  const authEnabled = isAuthEnabledServer();
  if (authEnabled) {
    const { userId } = await auth();
    if (userId) {
      redirect(
        process.env.NEXT_PUBLIC_CLERK_SIGN_UP_FALLBACK_REDIRECT_URL ||
          "/dashboard"
      );
    }
  }

  return (
    <div className="relative flex min-h-screen w-full items-center justify-center overflow-hidden bg-neutral-950">
      <Spotlight className="-top-40 left-0 md:-top-20 md:left-60" fill="white" />
      <div className="relative z-10 flex flex-col items-center gap-8">
        <div className="text-center">
          <h1 className="bg-gradient-to-b from-white to-neutral-400 bg-clip-text text-4xl font-bold text-transparent md:text-6xl">
            Join Glymmy
          </h1>
          <p className="mt-4 text-neutral-400">Your AI-powered health companion.</p>
        </div>
        {authEnabled ? (
          <SignUp
            appearance={{
              elements: {
                rootBox: "mx-auto",
                card: "bg-neutral-900 border border-neutral-800 shadow-2xl",
              },
            }}
          />
        ) : (
          <div className="w-full max-w-md rounded-3xl border border-neutral-800 bg-neutral-900/90 p-8 text-center text-neutral-300 shadow-2xl">
            Authentication is disabled in local demo mode. Open the dashboard directly to explore the app.
          </div>
        )}
      </div>
    </div>
  );
}
