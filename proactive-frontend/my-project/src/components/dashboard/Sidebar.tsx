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
    await fetch('http://localhost:8000/auth/logout', {
      method: 'POST',
      credentials: 'include',
    });
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
          <div className="w-10 h-10 bg-linear-to-br from-blue-500 to-cyan-400 rounded-full flex items-center justify-center">
            <span className="font-semibold text-white">
              {user?.email?.charAt(0) || 'U'}
            </span>
          </div>
          {!collapsed && (
            <div className="flex-1">
              <h3 className="font-semibold text-white truncate">{user?.email || 'User'}</h3>
              <p className="text-xs text-gray-400">{user?.email}</p>
              <div className="mt-1">
                <span className="inline-block px-2 py-1 text-xs bg-blue-500/20 text-blue-400 rounded-full">
                  {user?.role === 'admin' ? 'Administrator' : 'Vehicle Owner'}
                </span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4 px-3">
        <ul className="space-y-2">
          {items.map((item) => (
            <li key={item.title}>
              {item.subItems ? (
                <div>
                  <button
                    onClick={() => toggleExpand(item.title)}
                    className={`w-full flex items-center justify-between p-3 rounded-xl transition-colors ${
                      pathname.startsWith(item.href)|| expandedItems.includes(item.title)
                        ? 'bg-blue-900/30 text-blue-400'
                        : 'text-gray-400 hover:bg-gray-800/50 hover:text-gray-300'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      {iconMap[item.icon]}
                      {!collapsed && <span>{item.title}</span>}
                    </div>
                    {!collapsed && (
                      <ChevronRight className={`w-4 h-4 transition-transform ${
                        expandedItems.includes(item.title) ? 'rotate-90' : ''
                      }`} />
                    )}
                  </button>
                  
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
                  className={`flex items-center gap-3 p-3 rounded-xl transition-colors relative ${
                   pathname.startsWith(item.href)
                      ? 'bg-blue-900/30 text-blue-400'
                      : 'text-gray-400 hover:bg-gray-800/50 hover:text-gray-300'
                  }`}
                >
                  {iconMap[item.icon]}
                  {!collapsed && <span>{item.title}</span>}
                  {item.badge && (
                    <span className="absolute right-3 px-2 py-1 text-xs bg-red-500 text-white rounded-full">
                      {item.badge}
                    </span>
                  )}
                </Link>
              )}
            </li>
          ))}
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