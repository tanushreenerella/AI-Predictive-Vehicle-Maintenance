'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, Car, Calendar, Bell, 
  BarChart3, FileText, Bot, Users, 
  Settings, ChevronLeft, ChevronRight,
  LogOut, Home, TrendingUp
} from 'lucide-react';

const iconMap: { [key: string]: React.ReactNode } = {
  LayoutDashboard: <LayoutDashboard className="w-5 h-5" />,
  Car: <Car className="w-5 h-5" />,
  Calendar: <Calendar className="w-5 h-5" />,
  Bell: <Bell className="w-5 h-5" />,
  BarChart3: <BarChart3 className="w-5 h-5" />,
  FileText: <FileText className="w-5 h-5" />,
  Bot: <Bot className="w-5 h-5" />,
  Users: <Users className="w-5 h-5" />,
  Settings: <Settings className="w-5 h-5" />,
  Home: <Home className="w-5 h-5" />,
  TrendingUp: <TrendingUp className="w-5 h-5" />,
};

export interface MenuItem {
  title: string;
  href: string;
  icon: string;
  active?: boolean;
  badge?: string;
  subItems?: Array<{ title: string; href: string }>;
}

interface SidebarProps {
  items: MenuItem[];
  user: any;
  collapsed: boolean;
  onToggle: () => void;
}

export default function Sidebar({ items, user, collapsed, onToggle }: SidebarProps) {
  const pathname = usePathname();
  const [expandedItems, setExpandedItems] = useState<string[]>([]);

  const toggleExpand = (title: string) => {
    setExpandedItems(prev =>
      prev.includes(title) 
        ? prev.filter(item => item !== title)
        : [...prev, title]
    );
  };

const handleLogout = async () => {
  try {
    localStorage.removeItem('access_token');
    await fetch('https://ai-predictive-vehicle-maintenance-production.up.railway.app/auth/logout', { method: 'POST' });
  } finally {
    window.location.href = '/login';
  }
};

  return (
    <aside className={`fixed left-0 top-0 h-screen bg-gray-900 border-r border-blue-800/30 transition-all duration-300 flex flex-col ${collapsed ? 'w-20' : 'w-64'}`}>
      {/* Logo */}
      <div className="p-6 border-b border-blue-800/30">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-linear-to-br from-blue-600 to-cyan-500 rounded-xl flex items-center justify-center shrink-0">
            <Car className="w-6 h-6 text-white" />
          </div>
          {!collapsed && (
            <div>
              <h2 className="text-xl font-bold bg-linear-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                ProactiveAI
              </h2>
              <p className="text-xs text-gray-500">{user?.role === 'admin' ? 'Admin Panel' : 'User Panel'}</p>
            </div>
          )}
        </div>
      </div>

      {/* User Profile */}
      <div className="p-4 border-b border-blue-800/30">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-linear-to-br from-blue-500 to-cyan-400 rounded-full flex items-center justify-center shrink-0">
            <span className="font-bold text-white text-sm uppercase">
              {user?.email?.charAt(0) || 'U'}
            </span>
          </div>
          {!collapsed && (
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-white truncate">
                {user?.name || user?.email?.split('@')[0] || 'User'}
              </p>
              <p className="text-xs text-gray-500 truncate">{user?.email}</p>
              <span className="inline-block mt-1 px-2 py-0.5 text-xs bg-blue-500/15 text-blue-400 rounded-full border border-blue-500/20">
                {user?.role === 'admin' ? 'Administrator' : 'Vehicle Owner'}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4 px-3">
        {!collapsed && <p className="text-xs font-semibold text-gray-600 uppercase tracking-wider px-3 mb-2">Main</p>}
        <ul className="space-y-1">
          {items.map((item) => {
            const isManagementStart = item.title === 'AI Analysis';
            return (
            <li key={item.title}>
              {!collapsed && isManagementStart && (
                <p className="text-xs font-semibold text-gray-600 uppercase tracking-wider px-3 pt-4 pb-2">Tools</p>
              )}
              {item.subItems ? (
                <div>
                  <div className={`flex items-center rounded-xl border-l-[3px] overflow-hidden ${
                    pathname.startsWith(item.href) || expandedItems.includes(item.title)
                      ? 'border-blue-500'
                      : 'border-transparent'
                  }`}>
                    <Link
                      href={item.href}
                      onClick={() => { if (!expandedItems.includes(item.title)) toggleExpand(item.title); }}
                      className={`flex-1 flex items-center gap-3 pl-2.5 py-3 pr-1 transition-all text-sm font-medium ${
                        pathname.startsWith(item.href) || expandedItems.includes(item.title)
                          ? 'bg-blue-900/20 text-blue-400'
                          : 'text-gray-400 hover:bg-gray-800/50 hover:text-gray-200'
                      }`}
                    >
                      {iconMap[item.icon]}
                      {!collapsed && <span>{item.title}</span>}
                    </Link>
                    {!collapsed && (
                      <button
                        onClick={() => toggleExpand(item.title)}
                        className={`px-2.5 py-3 transition-all ${
                          pathname.startsWith(item.href) || expandedItems.includes(item.title)
                            ? 'bg-blue-900/20 text-blue-400'
                            : 'text-gray-500 hover:bg-gray-800/50 hover:text-gray-300'
                        }`}
                      >
                        <ChevronRight className={`w-4 h-4 transition-transform ${expandedItems.includes(item.title) ? 'rotate-90' : ''}`} />
                      </button>
                    )}
                  </div>

                  {!collapsed && expandedItems.includes(item.title) && (
                    <ul className="ml-8 mt-2 space-y-1">
                      {item.subItems.map((subItem) => (
                        <li key={subItem.title}>
                          <Link
                            href={subItem.href}
                            className="flex items-center gap-3 p-2 text-sm rounded-lg text-gray-400 hover:text-gray-300 hover:bg-gray-800/30 transition-colors"
                          >
                            <span className="w-1 h-1 bg-gray-500 rounded-full"></span>
                            {subItem.title}
                          </Link>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              ) : (
                <Link
                  href={item.href}
                  className={`flex items-center gap-3 p-3 rounded-xl transition-all relative ${
                    (item.href === '/dashboard/user' ? pathname === item.href : pathname.startsWith(item.href))
                      ? 'bg-blue-900/20 text-blue-400 border-l-[3px] border-blue-500 pl-2.25'
                      : 'text-gray-400 hover:bg-gray-800/50 hover:text-gray-200 border-l-[3px] border-transparent pl-2.25'
                  }`}
                >
                  {iconMap[item.icon]}
                  {!collapsed && <span className="text-sm font-medium">{item.title}</span>}
                  {item.badge && !collapsed && (
                    <span className="absolute right-3 flex items-center gap-1 text-xs text-blue-400 font-semibold">
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
                      {item.badge}
                    </span>
                  )}
                </Link>
              )}
            </li>
            );
          })}
        </ul>
      </nav>

      {/* Bottom Actions */}
      <div className="p-4 border-t border-blue-800/30 space-y-2">
        <button
          onClick={onToggle}
          className="w-full flex items-center justify-center gap-3 p-3 text-gray-400 hover:text-gray-300 hover:bg-gray-800/50 rounded-xl transition-colors"
        >
          {collapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
          {!collapsed && <span>Collapse</span>}
        </button>
        
        <button
          onClick={handleLogout}
          className="w-full flex items-center justify-center gap-3 p-3 text-red-400 hover:text-red-300 hover:bg-red-900/20 rounded-xl transition-colors"
        >
          <LogOut className="w-5 h-5" />
          {!collapsed && <span>Logout</span>}
        </button>
      </div>
    </aside>
  );
}