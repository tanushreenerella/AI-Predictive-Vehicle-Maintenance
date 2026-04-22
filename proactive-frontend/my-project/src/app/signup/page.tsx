'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Car, Eye, Calendar,EyeOff, AlertCircle, User, Phone, Mail, Hash,Key } from 'lucide-react';
import Link from 'next/link';

export default function SignupPage() {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    phone: '',
    userType: 'user',
    vehicleNumber: '',
    password: '',
    confirmPassword: ''
  });
  const [errors, setErrors] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrors([]);

    // Validate form
    const newErrors = [];
    if (!formData.fullName) newErrors.push('Full name is required');
    if (!formData.email) newErrors.push('Email is required');
    if (!formData.phone) newErrors.push('Phone number is required');
    if (formData.userType === 'user' && !formData.vehicleNumber) newErrors.push('Vehicle number is required');
    if (!formData.password) newErrors.push('Password is required');
    if (formData.password !== formData.confirmPassword) newErrors.push('Passwords do not match');
    if (formData.password.length < 8) newErrors.push('Password must be at least 8 characters');

    if (newErrors.length > 0) {
      setErrors(newErrors);
      setLoading(false);
      return;
    }

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // For demo purposes, simulate successful registration
    await fetch("http://localhost:8000/auth/signup", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  credentials: "include",
  body: JSON.stringify({
    email: formData.email,
    password: formData.password,
    role: formData.userType,
  }),
});



      // Redirect to appropriate dashboard
      if (formData.userType === 'admin') {
        router.push('/dashboard/admin');
      } else {
        router.push('/dashboard/user');
      }
    } catch (error) {
      setErrors(['Registration failed. Please try again.']);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-linear-to-br from-gray-900 via-blue-900/20 to-gray-900 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-linear-to-br from-blue-600 to-cyan-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Car className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold bg-linear-to-br from-blue-400 to-cyan-400 bg-clip-text text-transparent">
            Join ProactiveAI
          </h1>
          <p className="text-gray-400 mt-2">Register for intelligent vehicle maintenance</p>
        </div>

        {/* Signup Card */}
        <div className="bg-gray-800/50 backdrop-blur-sm border border-blue-800/30 rounded-2xl p-8 shadow-2xl">
          <h2 className="text-2xl font-bold text-white mb-6">Create Account</h2>
          
          {errors.length > 0 && (
            <div className="mb-6 p-4 bg-red-900/30 border border-red-700/50 rounded-lg">
              <div className="flex items-center gap-2 text-red-400">
                <AlertCircle className="w-5 h-5" />
                <span className="font-semibold">Please fix the following:</span>
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
              <label className="text-sm font-medium text-gray-300">Register As</label>
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
                        <div className="text-xs text-gray-400">Monitor your personal vehicles</div>
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
                        <div className="text-xs text-gray-400">System & fleet management</div>
                      </div>
                    </div>
                  </div>
                </label>
              </div>
            </div>

            {/* Two Column Grid for Personal Info */}
            <div className="grid md:grid-cols-2 gap-6">
              {/* Full Name */}
              <div className="space-y-2">
                <label htmlFor="fullName" className="text-sm font-medium text-gray-300">
                  Full Name
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <input
                    id="fullName"
                    type="text"
                    value={formData.fullName}
                    onChange={(e) => setFormData({...formData, fullName: e.target.value})}
                    className="w-full pl-10 pr-4 py-3 bg-gray-900/50 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="John Doe"
                    required
                  />
                </div>
              </div>

              {/* Email */}
              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium text-gray-300">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    className="w-full pl-10 pr-4 py-3 bg-gray-900/50 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="owner@example.com"
                    required
                  />
                </div>
              </div>

              {/* Phone */}
              <div className="space-y-2">
                <label htmlFor="phone" className="text-sm font-medium text-gray-300">
                  Phone Number
                </label>
                <div className="relative">
                  <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <input
                    id="phone"
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => setFormData({...formData, phone: e.target.value})}
                    className="w-full pl-10 pr-4 py-3 bg-gray-900/50 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="+1 (555) 123-4567"
                    required
                  />
                </div>
              </div>

              {/* Vehicle Number (only for users) */}
              {formData.userType === 'user' && (
                <div className="space-y-2">
                  <label htmlFor="vehicleNumber" className="text-sm font-medium text-gray-300">
                    Vehicle Registration Number
                  </label>
                  <div className="relative">
                    <Hash className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-500" />
                    <input
                      id="vehicleNumber"
                      type="text"
                      value={formData.vehicleNumber}
                      onChange={(e) => setFormData({...formData, vehicleNumber: e.target.value.toUpperCase()})}
                      className="w-full pl-10 pr-4 py-3 bg-gray-900/50 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="ABC1234"
                      required
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Two Column Grid for Passwords */}
            <div className="grid md:grid-cols-2 gap-6">
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
                <p className="text-xs text-gray-500">Minimum 8 characters</p>
              </div>

              {/* Confirm Password */}
              <div className="space-y-2">
                <label htmlFor="confirmPassword" className="text-sm font-medium text-gray-300">
                  Confirm Password
                </label>
                <div className="relative">
                  <input
                    id="confirmPassword"
                    type={showPassword ? "text" : "password"}
                    value={formData.confirmPassword}
                    onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
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
            </div>

            {/* Terms and Conditions */}
            <div className="space-y-2">
              <label className="flex items-start space-x-3">
                <input
                  type="checkbox"
                  required
                  className="mt-1 w-4 h-4 rounded bg-gray-900 border-gray-700 text-blue-500 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-400">
                  I agree to the{' '}
                  <button type="button" className="text-blue-400 hover:text-blue-300">
                    Terms of Service
                  </button>{' '}
                  and{' '}
                  <button type="button" className="text-blue-400 hover:text-blue-300">
                    Privacy Policy
                  </button>
                </span>
              </label>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-linear-to-br from-blue-600 to-cyan-600 text-white py-3 rounded-xl font-semibold hover:shadow-lg hover:shadow-blue-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating Account...' : 'Create Account'}
            </button>

            {/* Login Link */}
            <div className="text-center pt-4 border-t border-gray-800">
              <p className="text-gray-400">
                Already have an account?{' '}
                <Link href="/login" className="text-blue-400 hover:text-blue-300 font-semibold transition-colors">
                  Sign in
                </Link>
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}