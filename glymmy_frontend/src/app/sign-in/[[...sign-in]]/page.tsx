import { auth } from "@clerk/nextjs/server";
import { SignIn } from "@clerk/nextjs";
import { redirect } from "next/navigation";
import { Spotlight } from "@/components/aceternity/spotlight";
import { isAuthEnabledServer } from "@/lib/auth-config";

export default async function SignInPage() {
  const authEnabled = isAuthEnabledServer();

  if (authEnabled) {
    const { userId } = await auth();
    if (userId) {
      redirect("/dashboard");
    }
  } else {
    // Demo mode — skip sign-in, go straight to dashboard
    redirect("/dashboard");
  }

  return (
    <div className="relative flex min-h-screen w-full items-center justify-center overflow-hidden bg-neutral-950">
      <Spotlight className="-top-40 left-0 md:-top-20 md:left-60" fill="white" />
      <div className="relative z-10 flex flex-col items-center gap-8">
        <div className="text-center">
          <h1 className="bg-gradient-to-b from-white to-neutral-400 bg-clip-text text-4xl font-bold text-transparent md:text-6xl">
            Welcome to Glymmy
          </h1>
          <p className="mt-4 text-neutral-400">Your glycemic companion. Sign in to continue.</p>
        </div>
        <SignIn
          appearance={{
            elements: {
              rootBox: "mx-auto",
              card: "bg-neutral-900 border border-neutral-800 shadow-2xl",
            },
          }}
        />
      </div>
    </div>
  );
}
