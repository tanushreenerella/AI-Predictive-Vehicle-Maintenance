'use client';

import { useState } from 'react';
import { 
  Bell, Search, Menu, ChevronDown, 
  Settings, User, HelpCircle, Moon, Sun,LogOut
} from 'lucide-react';
import { useRouter } from 'next/navigation';

interface HeaderProps {
  user: any;
  onMenuClick: () => void;
}

export default function Header({ user, onMenuClick }: HeaderProps) {
  const router = useRouter();
  const [darkMode, setDarkMode] = useState(true);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

  const notifications = [
    { id: 1, title: 'Engine alert detected', time: '2 mins ago', read: false },
    { id: 2, title: 'Service scheduled', time: '15 mins ago', read: false },
    { id: 3, title: 'System update available', time: '1 hour ago', read: true },
  ];

  const unreadCount = notifications.filter(n => !n.read).length;

  const handleLogout = async () => {
  try {
    await fetch("http://localhost:8000/auth/logout", {
      method: "POST",
      credentials: "include", // 🔴 VERY IMPORTANT
    });
  } catch (error) {
    console.error("Logout failed", error);
  } finally {
    router.push("/login"); // ✅ always redirect
  }
};


  return (
    <header className="sticky top-0 z-30 bg-gray-900/80 backdrop-blur-lg border-b border-blue-800/30">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Left side - Menu button and Search */}
          <div className="flex items-center gap-4">
            <button
              onClick={onMenuClick}
              className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors lg:hidden"
            >
              <Menu className="w-5 h-5" />
            </button>
            
            <div className="relative hidden md:block">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-500" />
              <input
                type="text"
                placeholder="Search vehicles, services, or alerts..."
                className="pl-10 pr-4 py-2 w-64 lg:w-96 bg-gray-800/50 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Right side - Actions */}
          <div className="flex items-center gap-4">
            {/* Theme Toggle */}
            <button
              onClick={() => setDarkMode(!darkMode)}
              className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
              title={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>

            {/* Help */}
            <button
              className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
              title="Help & Support"
            >
              <HelpCircle className="w-5 h-5" />
            </button>

            {/* Settings */}
            <button
              className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
              title="Settings"
            >
              <Settings className="w-5 h-5" />
            </button>

            {/* Notifications */}
            <div className="relative">
              <button
                onClick={() => setShowNotifications(!showNotifications)}
                className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors relative"
              >
                <Bell className="w-5 h-5" />
                {unreadCount > 0 && (
                  <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                    {unreadCount}
                  </span>
                )}
              </button>

              {/* Notifications Dropdown */}
              {showNotifications && (
                <div className="absolute right-0 mt-2 w-80 bg-gray-900 border border-gray-800 rounded-xl shadow-xl">
                  <div className="p-4 border-b border-gray-800">
                    <h3 className="font-semibold text-white">Notifications</h3>
                    <p className="text-sm text-gray-400">{unreadCount} unread</p>
                  </div>
                  
                  <div className="max-h-96 overflow-y-auto">
                    {notifications.map(notification => (
                      <div
                        key={notification.id}
                        className={`p-4 border-b border-gray-800 hover:bg-gray-800/50 cursor-pointer ${!notification.read ? 'bg-blue-900/10' : ''}`}
                      >
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="font-medium text-white">{notification.title}</p>
                            <p className="text-sm text-gray-400 mt-1">{notification.time}</p>
                          </div>
                          {!notification.read && (
                            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  <div className="p-3 border-t border-gray-800">
                    <button className="w-full text-center text-blue-400 hover:text-blue-300 text-sm">
                      View all notifications
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* User Menu */}
            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center gap-3 p-2 text-gray-300 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
              >
                <div className="w-8 h-8 bg-linear-to-br from-blue-500 to-cyan-400 rounded-full flex items-center justify-center">
                  <span className="font-semibold text-white">
                    {user?.name?.charAt(0) || 'U'}
                  </span>
                </div>
                <div className="hidden md:block text-left">
                  <p className="text-sm font-medium">{user?.name || 'User'}</p>
                  <p className="text-xs text-gray-400">
                    {user?.userType === 'admin' ? 'Administrator' : 'Vehicle Owner'}
                  </p>
                </div>
                <ChevronDown className="w-4 h-4 hidden md:block" />
              </button>

              {/* User Dropdown Menu */}
              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-gray-900 border border-gray-800 rounded-xl shadow-xl">
                  <div className="p-4 border-b border-gray-800">
                    <p className="font-medium text-white">{user?.name || 'User'}</p>
                    <p className="text-sm text-gray-400 truncate">{user?.email}</p>
                  </div>
                  
                  <div className="p-2">
                    <button className="w-full flex items-center gap-3 p-3 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors">
                      <User className="w-4 h-4" />
                      <span>Profile</span>
                    </button>
                    
                    <button className="w-full flex items-center gap-3 p-3 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors">
                      <Settings className="w-4 h-4" />
                      <span>Account Settings</span>
                    </button>
                    
                    <div className="border-t border-gray-800 my-2"></div>
                    
                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center gap-3 p-3 text-red-400 hover:text-red-300 hover:bg-red-900/20 rounded-lg transition-colors"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Logout</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Mobile Search */}
        <div className="mt-4 md:hidden">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input
              type="text"
              placeholder="Search vehicles, services, or alerts..."
              className="w-full pl-10 pr-4 py-2 bg-gray-800/50 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {/* Close dropdowns when clicking outside */}
      {(showNotifications || showUserMenu) && (
        <div
          className="fixed inset-0 z-20"
          onClick={() => {
            setShowNotifications(false);
            setShowUserMenu(false);
          }}
        />
      )}
    </header>
  );
}