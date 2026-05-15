'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar, { MenuItem } from '@/components/dashboard/Sidebar';
import { fetchWithAuth } from '@/lib/fetchWithAuth';

const API_BASE = 'https://ai-predictive-vehicle-maintenance-production.up.railway.app';
const menuItems: MenuItem[] = [
  {
    title: 'Dashboard',
    href: '/dashboard/user',
    icon: 'LayoutDashboard',
  },
  {
    title: 'My Vehicles',
    href: '/dashboard/user/vehicles',
    icon: 'Car',
    subItems: [
      { title: 'Add Vehicle', href: '/dashboard/user/vehicles/add' },
    ],
  },
  {
    title: 'Schedule',
    href: '/dashboard/user/schedule',
    icon: 'Calendar',
  },
  {
    title: 'Appointments',
    href: '/dashboard/user/appointments',
    icon: 'Bell',
  },
  {
    title: 'AI Analysis',
    href: '/dashboard/user/analysis',
    icon: 'TrendingUp',
  },
  {
    title: 'AI Assistant',
    href: '/dashboard/user/agent-chat',
    icon: 'Bot',
    badge: 'AI',
  },
  {
    title: 'Reports',
    href: '/dashboard/user/reports',
    icon: 'FileText',
  },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [collapsed, setCollapsed] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const loadUser = async () => {
      try {
        const res = await fetchWithAuth(`${API_BASE}/auth/me`);

        if (!res.ok) throw new Error();

        setUser(await res.json());
      } catch {
        router.replace('/login'); // 🔴 replace, not push
      } finally {
        setLoading(false); // 🔴 ALWAYS clear loading
      }
    };

    loadUser();
  }, [router]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen text-gray-600">
        Loading session...
      </div>
    );
  }

  if (!user) {
    return null; // redirect already triggered
  }

  return (
    <div className="min-h-screen bg-gray-900">
      <Sidebar
        items={menuItems}
        user={user}
        collapsed={collapsed}
        onToggle={() => setCollapsed(!collapsed)}
      />

      <div className={`transition-all duration-300 ${collapsed ? 'ml-20' : 'ml-64'}`}>
        {/* Top bar */}
        <header className="sticky top-0 z-10 bg-gray-900/80 backdrop-blur-sm border-b border-gray-800 px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <span className="text-gray-600">/</span>
            <span className="text-gray-300 font-medium capitalize">
              {user?.role === 'admin' ? 'Admin' : 'Dashboard'}
            </span>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-800 rounded-lg border border-gray-700">
              <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
              <span className="text-xs text-gray-400">
                {user?.name || user?.email?.split('@')[0] || 'User'}
              </span>
            </div>
          </div>
        </header>

        <main className="p-6 min-h-[calc(100vh-57px)]">
          {children}
        </main>
      </div>
    </div>
  );
}
