'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { fetchWithAuth } from '@/lib/fetchWithAuth';

export default function UserLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await fetchWithAuth("https://ai-predictive-vehicle-maintenance-production.up.railway.app/auth/me");

        if (!res.ok) throw new Error("Unauthorized");

        setUser(await res.json());
      } catch {
        router.replace("/login");
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, []);

  if (loading) return null;
  if (!user) return null;

  return (
    <div className="min-h-screen bg-gray-900">
      {children}
    </div>
  );
}
