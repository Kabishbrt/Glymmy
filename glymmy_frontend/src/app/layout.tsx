import type { Metadata } from "next";
import { ClerkProvider } from "@clerk/nextjs";
import { isAuthEnabledServer } from "@/lib/auth-config";
import { AuthTokenProvider } from "@/components/auth-token-provider";
import "./globals.css";

export const metadata: Metadata = {
  title: "Glymmy — Your Glycemic Companion",
  description:
    "AI-powered unified health platform connecting CGM, wearables, food photos, and lab reports.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const authEnabled = isAuthEnabledServer();

  const content = (
    <html lang="en" className="dark h-full antialiased">
      <body className="min-h-full bg-background font-sans text-foreground">
        <AuthTokenProvider authEnabled={authEnabled}>
          {children}
        </AuthTokenProvider>
      </body>
    </html>
  );

  if (!authEnabled) {
    return content;
  }

  return <ClerkProvider>{content}</ClerkProvider>;
}
