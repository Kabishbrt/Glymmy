"use client";

import {
  Activity,
  Apple,
  Bell,
  ClipboardList,
  FlaskConical,
  Heart,
  Home,
  MessageSquare,
  QrCode,
  ScanLine,
  Watch,
} from "lucide-react";
import { UserButton } from "@clerk/nextjs";
import {
  Sidebar,
  SidebarBody,
  SidebarLink,
} from "@/components/aceternity/sidebar";
import { UserProvider, useUser } from "@/components/dashboard/user-context";
import { isAuthEnabledClient } from "@/lib/auth-config";

const iconClass = "h-5 w-5 text-neutral-400";

const links = [
  { label: "Overview", href: "/dashboard", icon: <Home className={iconClass} /> },
  { label: "Glucose", href: "/dashboard/glucose", icon: <Activity className={iconClass} /> },
  { label: "Devices", href: "/dashboard/devices", icon: <Watch className={iconClass} /> },
  { label: "Health Card", href: "/dashboard/inventory", icon: <ClipboardList className={iconClass} /> },
  { label: "Food", href: "/dashboard/food", icon: <Apple className={iconClass} /> },
  { label: "Scan", href: "/dashboard/scan", icon: <ScanLine className={iconClass} /> },
  { label: "Labs", href: "/dashboard/labs", icon: <FlaskConical className={iconClass} /> },
  { label: "Chat", href: "/dashboard/chat", icon: <MessageSquare className={iconClass} /> },
  { label: "Notifications", href: "/dashboard/notifications", icon: <Bell className={iconClass} /> },
  { label: "Share", href: "/dashboard/share", icon: <QrCode className={iconClass} /> },
];

const authEnabled = isAuthEnabledClient();

function DashboardHeader() {
  const { user, loading } = useUser();
  const firstName = user?.name?.split(" ")[0] || "there";

  return (
    <div className="border-b border-neutral-800 bg-neutral-900/50 backdrop-blur-sm px-6 py-4 flex items-center justify-between">
      <div>
        <h2 className="text-lg font-semibold text-white">
          {loading ? "Loading..." : `Hi, ${firstName}`}
        </h2>
        {user?.diagnosis && (
          <p className="text-sm text-neutral-400">{user.diagnosis}</p>
        )}
      </div>
      <div className="flex items-center gap-4">
        {authEnabled ? (
          <UserButton />
        ) : (
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-full bg-gradient-to-br from-sky-400 to-indigo-600 flex items-center justify-center text-xs font-bold text-white">
              {user?.name?.[0] || "?"}
            </div>
            <span className="text-sm text-neutral-400">Demo</span>
          </div>
        )}
      </div>
    </div>
  );
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <UserProvider>
      <div className="flex min-h-screen w-full bg-neutral-950">
        <Sidebar>
          <SidebarBody className="justify-between gap-10">
            <div className="flex flex-1 flex-col overflow-y-auto overflow-x-hidden">
              <div className="flex items-center gap-2 px-1">
                <div className="h-7 w-7 flex-shrink-0 rounded-lg bg-gradient-to-br from-sky-400 to-indigo-600" />
                <span className="font-bold text-white">Glymmy</span>
              </div>
              <div className="mt-8 flex flex-col gap-2">
                {links.map((link) => (
                  <SidebarLink key={link.href} link={link} />
                ))}
              </div>
            </div>
            <div className="flex items-center gap-2 px-1">
              <Heart className="h-4 w-4 text-rose-500" />
              <span className="text-xs text-neutral-500">Harvard HSIL 2026</span>
            </div>
          </SidebarBody>
        </Sidebar>

        <main className="flex-1 overflow-y-auto">
          <DashboardHeader />
          <div className="p-6">{children}</div>
        </main>
      </div>
    </UserProvider>
  );
}
