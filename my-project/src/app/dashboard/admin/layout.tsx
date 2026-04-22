'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '@/components/dashboard/Sidebar';
import Header from '@/components/dashboard/Header';

const adminMenuItems = [
  {
    title: 'Dashboard',
    href: '/dashboard/admin',
    icon: 'LayoutDashboard',
    active: true
  },
  {
    title: 'Vehicle Monitoring',
    href: '/dashboard/admin/monitoring',
    icon: 'Car',
    subItems: [
      { title: 'Real-time Tracking', href: '/dashboard/admin/monitoring/live' },
      { title: 'Fleet Overview', href: '/dashboard/admin/monitoring/fleet' },
      { title: 'Sensor Analytics', href: '/dashboard/admin/monitoring/sensors' }
    ]
  },
  {
    title: 'Service Scheduling',
    href: '/dashboard/admin/scheduling',
    icon: 'Calendar',
    badge: '15'
  },
  {
    title: 'RCA Insights',
    href: '/dashboard/admin/rca',
    icon: 'BarChart3'
  },
  {
    title: 'AI Agent Control',
    href: '/dashboard/admin/agents',
    icon: 'Bot',
    subItems: [
      { title: 'Agent Status', href: '/dashboard/admin/agents/status' },
      { title: 'Agent Configuration', href: '/dashboard/admin/agents/config' },
      { title: 'Training Data', href: '/dashboard/admin/agents/training' }
    ]
  },
  {
    title: 'System Configuration',
    href: '/dashboard/admin/system',
    icon: 'Settings'
  },
  {
    title: 'User Management',
    href: '/dashboard/admin/users',
    icon: 'Users'
  },
  {
    title: 'Reports & Analytics',
    href: '/dashboard/admin/reports',
    icon: 'FileText'
  }
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    // Check authentication and admin privileges
    const userData = localStorage.getItem('user');
    if (!userData) {
      router.push('/login');
    } else {
      const parsedUser = JSON.parse(userData);
      if (parsedUser.userType !== 'admin') {
        router.push('/dashboard/user');
      }
      setUser(parsedUser);
    }
  }, [router]);

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900">
      <Sidebar
        items={adminMenuItems}
        user={user}
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      <main className={`transition-all duration-300 ${sidebarCollapsed ? 'ml-20' : 'ml-64'}`}>
        <Header user={user} onMenuClick={() => setSidebarCollapsed(!sidebarCollapsed)} />
        
        <div className="p-6">
          {children}
        </div>
      </main>
    </div>
  );
}