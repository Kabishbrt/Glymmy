"use client";

import { createContext, useContext, useCallback, useEffect, useState } from "react";
import type { UserProfile } from "@/lib/api-types";
import { api } from "@/lib/api-client";

interface UserContextValue {
  user: UserProfile | null;
  loading: boolean;
  error: string | null;
  refreshUser: () => void;
}

const UserContext = createContext<UserContextValue>({
  user: null,
  loading: true,
  error: null,
  refreshUser: () => {},
});

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchUser = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const profile = await api.me.profile();
      setUser(profile);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to load profile";
      setError(msg);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  return (
    <UserContext.Provider value={{ user, loading, error, refreshUser: fetchUser }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  return useContext(UserContext);
}
