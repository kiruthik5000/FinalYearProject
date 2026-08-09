import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [remember, setRemember] = useState(false);
  const [errors, setErrors] = useState({});
  const [submitError, setSubmitError] = useState('');
  const [loading, setLoading] = useState(false);
  const [forgotMsg, setForgotMsg] = useState('');
  const navigate = useNavigate();

  const validate = () => {
    const newErrors = {};
    if (!email.trim()) {
      newErrors.email = 'Email address is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = 'Please enter a valid email address';
    }
    if (!password) {
      newErrors.password = 'Password is required';
    } else if (password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitError('');
    if (!validate()) return;

    setLoading(true);
    try {
      // TODO: Replace with actual API call — e.g. await api.post('/api/auth/login', { email, password })
      await new Promise((_, reject) => setTimeout(() => reject(new Error('not_implemented')), 800));
      navigate('/');
    } catch (err) {
      if (err.message === 'not_implemented') {
        setSubmitError('Login service is not connected yet. Please configure the backend API.');
      } else {
        setSubmitError(err.response?.data?.detail || 'Invalid email or password. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = (e) => {
    e.preventDefault();
    if (!email.trim()) {
      setErrors((prev) => ({ ...prev, email: 'Enter your email above first, then click Forgot' }));
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setErrors((prev) => ({ ...prev, email: 'Enter a valid email to receive reset link' }));
      return;
    }
    setForgotMsg(`Password reset link sent to ${email}. Check your inbox.`);
    setTimeout(() => setForgotMsg(''), 5000);
  };

  const handleGitHubLogin = () => {
    setSubmitError('GitHub authentication is not configured yet.');
    setTimeout(() => setSubmitError(''), 4000);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-['Hanken_Grotesk',sans-serif] flex flex-col justify-between relative overflow-hidden">
      {/* Top Header */}
      <header className="fixed top-0 w-full bg-white/80 backdrop-blur-md border-b border-slate-200 flex justify-between items-center px-8 py-3 z-50 animate-fade-in">
        <Link to="/" className="flex items-center gap-2 group">
          <div className="w-7 h-7 rounded-lg bg-amber-500 flex items-center justify-center text-white font-bold text-sm transition-transform group-hover:scale-110">
            S
          </div>
          <span className="font-semibold text-base tracking-widest text-slate-900">SMART RAG</span>
        </Link>
        <div className="flex items-center gap-2 px-3 py-1 bg-slate-100 border border-slate-200 rounded-full">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span className="font-['JetBrains_Mono',monospace] text-xs text-slate-600">Service healthy</span>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center px-4 pt-20 pb-12 z-10">
        <div className="w-full max-w-md bg-white border border-slate-200 rounded-2xl p-8 shadow-xl animate-slide-up">
          <div className="text-center mb-8 animate-fade-in-up">
            <h1 className="text-2xl font-bold text-slate-900 mb-2">Sign in to Smart RAG</h1>
            <p className="text-xs text-slate-500">Access your intelligent knowledge base dashboard</p>
          </div>

          {/* Global submit error */}
          {submitError && (
            <div className="mb-5 p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-700 font-medium flex items-center gap-2 animate-fade-in-up">
              <span className="material-symbols-outlined text-sm">error</span>
              {submitError}
            </div>
          )}

          {/* Forgot password success message */}
          {forgotMsg && (
            <div className="mb-5 p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-700 font-medium flex items-center gap-2 animate-fade-in-up">
              <span className="material-symbols-outlined text-sm">check_circle</span>
              {forgotMsg}
            </div>
          )}

          <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-5">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2 font-['JetBrains_Mono',monospace]">
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => { setEmail(e.target.value); setErrors((prev) => ({ ...prev, email: '' })); }}
                placeholder="name@company.com"
                className={`w-full bg-slate-50 border rounded-xl px-4 py-3 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none transition-all ${
                  errors.email ? 'border-rose-400 focus:border-rose-500 focus:ring-1 focus:ring-rose-500' : 'border-slate-200 focus:border-amber-500 focus:ring-1 focus:ring-amber-500'
                }`}
              />
              {errors.email && (
                <p className="mt-1.5 text-xs text-rose-600 flex items-center gap-1 animate-fade-in-up">
                  <span className="material-symbols-outlined text-xs">warning</span>
                  {errors.email}
                </p>
              )}
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider font-['JetBrains_Mono',monospace]">
                  Password
                </label>
                <button
                  type="button"
                  onClick={handleForgotPassword}
                  className="text-xs font-medium text-amber-600 hover:underline"
                >
                  Forgot?
                </button>
              </div>
              <input
                type="password"
                value={password}
                onChange={(e) => { setPassword(e.target.value); setErrors((prev) => ({ ...prev, password: '' })); }}
                placeholder="Enter your password"
                className={`w-full bg-slate-50 border rounded-xl px-4 py-3 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none transition-all ${
                  errors.password ? 'border-rose-400 focus:border-rose-500 focus:ring-1 focus:ring-rose-500' : 'border-slate-200 focus:border-amber-500 focus:ring-1 focus:ring-amber-500'
                }`}
              />
              {errors.password && (
                <p className="mt-1.5 text-xs text-rose-600 flex items-center gap-1 animate-fade-in-up">
                  <span className="material-symbols-outlined text-xs">warning</span>
                  {errors.password}
                </p>
              )}
            </div>

            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={remember}
                  onChange={(e) => setRemember(e.target.checked)}
                  className="w-4 h-4 rounded border-slate-300 text-amber-500 focus:ring-amber-500"
                />
                <span className="text-xs text-slate-600">Remember for 30 days</span>
              </label>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-amber-500 hover:bg-amber-600 disabled:opacity-60 text-white font-semibold rounded-xl text-sm transition-all shadow-md hover:shadow-lg hover:scale-[1.01] active:scale-[0.99] flex items-center justify-center gap-2 mt-2"
            >
              {loading ? (
                <>
                  <span className="material-symbols-outlined text-lg animate-spin">sync</span>
                  Signing in...
                </>
              ) : (
                <>
                  <span className="material-symbols-outlined text-lg">login</span>
                  Sign In
                </>
              )}
            </button>
          </form>

          <div className="relative my-6 text-center">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200"></div>
            </div>
            <span className="relative bg-white px-3 text-xs text-slate-400 uppercase font-['JetBrains_Mono',monospace]">
              Or continue with
            </span>
          </div>

          <button
            type="button"
            onClick={handleGitHubLogin}
            className="w-full py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-medium rounded-xl text-xs transition-all shadow-sm hover:shadow-md hover:scale-[1.01] active:scale-[0.99] flex items-center justify-center gap-2"
          >
            <span className="material-symbols-outlined text-base">code</span>
            Continue with GitHub
          </button>

          <p className="text-center text-xs text-slate-500 mt-6">
            New to Smart RAG?{' '}
            <Link to="/signup" className="text-amber-600 font-semibold hover:underline">
              Create an account
            </Link>
          </p>
        </div>
      </main>

      {/* Footer */}
      <footer className="py-4 text-center text-xs text-slate-400 border-t border-slate-200 bg-white">
        <p>© 2026 Smart RAG Inc. · v1.0.4-stable</p>
      </footer>
    </div>
  );
}
