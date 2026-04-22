'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Car, Eye, EyeOff, AlertCircle, User, Key } from 'lucide-react';
import Link from 'next/link';

export default function LoginPage() {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    userType: 'user'
  });
  const [errors, setErrors] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrors([]);

    // Validate form
    const newErrors = [];
    if (!formData.email) newErrors.push('Email is required');
    if (!formData.password) newErrors.push('Password is required');

    if (newErrors.length > 0) {
      setErrors(newErrors);
      setLoading(false);
      return;
    }

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // For demo purposes, simulate successful login
    await fetch("http://localhost:8000/auth/login", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  credentials: "include", // 🔴 IMPORTANT
  body: JSON.stringify({
    email: formData.email,
    password: formData.password,
  }),
});

      // Redirect to appropriate dashboard
      if (formData.userType === 'admin') {
        router.push('/dashboard/admin');
      } else {
        router.push('/dashboard/user');
      }
    } catch (error) {
      setErrors(['Login failed. Please try again.']);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-linear-to-br from-gray-900 via-blue-900/20 to-gray-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-linear-to-br from-blue-600 to-cyan-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Car className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold bg-linear-to-br from-blue-400 to-cyan-400 bg-clip-text text-transparent">
            ProactiveAI
          </h1>
          <p className="text-gray-400 mt-2">Predictive Vehicle Maintenance System</p>
        </div>

        {/* Login Card */}
        <div className="bg-gray-800/50 backdrop-blur-sm border border-blue-800/30 rounded-2xl p-8 shadow-2xl">
          <h2 className="text-2xl font-bold text-white mb-6">Welcome Back</h2>
          
          {errors.length > 0 && (
            <div className="mb-6 p-4 bg-red-900/30 border border-red-700/50 rounded-lg">
              <div className="flex items-center gap-2 text-red-400">
                <AlertCircle className="w-5 h-5" />
                <span className="font-semibold">Error</span>
              </div>
              <ul className="mt-2 text-sm text-red-300">
                {errors.map((error, index) => (
                  <li key={index}>• {error}</li>
                ))}
              </ul>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* User Type Selection */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-300">Login As</label>
              <div className="flex gap-4">
                <label className="flex-1">
                  <input
                    type="radio"
                    name="userType"
                    value="user"
                    checked={formData.userType === 'user'}
                    onChange={(e) => setFormData({...formData, userType: e.target.value})}
                    className="sr-only"
                  />
                  <div className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${formData.userType === 'user' ? 'border-blue-500 bg-blue-900/20' : 'border-gray-700 hover:border-gray-600'}`}>
                    <div className="flex items-center gap-3">
                      <User className={`w-5 h-5 ${formData.userType === 'user' ? 'text-blue-400' : 'text-gray-500'}`} />
                      <div>
                        <div className="font-semibold text-white">Vehicle Owner</div>
                        <div className="text-xs text-gray-400">Monitor your vehicles</div>
                      </div>
                    </div>
                  </div>
                </label>
                
                <label className="flex-1">
                  <input
                    type="radio"
                    name="userType"
                    value="admin"
                    checked={formData.userType === 'admin'}
                    onChange={(e) => setFormData({...formData, userType: e.target.value})}
                    className="sr-only"
                  />
                  <div className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${formData.userType === 'admin' ? 'border-blue-500 bg-blue-900/20' : 'border-gray-700 hover:border-gray-600'}`}>
                    <div className="flex items-center gap-3">
                      <Key className={`w-5 h-5 ${formData.userType === 'admin' ? 'text-blue-400' : 'text-gray-500'}`} />
                      <div>
                        <div className="font-semibold text-white">Administrator</div>
                        <div className="text-xs text-gray-400">System management</div>
                      </div>
                    </div>
                  </div>
                </label>
              </div>
            </div>

            {/* Email */}
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium text-gray-300">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                className="w-full px-4 py-3 bg-gray-900/50 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="owner@example.com"
                required
              />
            </div>

            {/* Password */}
            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium text-gray-300">
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  className="w-full px-4 py-3 bg-gray-900/50 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="••••••••"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-400"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {/* Remember & Forgot */}
            <div className="flex items-center justify-between">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  className="w-4 h-4 rounded bg-gray-900 border-gray-700 text-blue-500 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-400">Remember me</span>
              </label>
              <button
                type="button"
                className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
              >
                Forgot password?
              </button>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-linear-to-br from-blue-600 to-cyan-600 text-white py-3 rounded-xl font-semibold hover:shadow-lg hover:shadow-blue-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>

            {/* Sign Up Link */}
            <div className="text-center pt-4 border-t border-gray-800">
              <p className="text-gray-400">
                Don't have an account?{' '}
                <Link href="/signup" className="text-blue-400 hover:text-blue-300 font-semibold transition-colors">
                  Sign up now
                </Link>
              </p>
            </div>
          </form>
        </div>

        {/* Demo Credentials */}
        <div className="mt-8 text-center">
          <details className="text-sm text-gray-500">
            <summary className="cursor-pointer hover:text-gray-400">Demo Credentials</summary>
            <div className="mt-2 space-y-1 bg-gray-900/30 p-4 rounded-xl">
              <p><strong>User:</strong> user@demo.com / demo123</p>
              <p><strong>Admin:</strong> admin@demo.com / admin123</p>
            </div>
          </details>
        </div>
      </div>
    </div>
  );
}