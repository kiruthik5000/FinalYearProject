import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

export default function SignUp() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState({});
  const [submitError, setSubmitError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const validate = () => {
    const newErrors = {};
    if (!name.trim()) {
      newErrors.name = 'Full name is required';
    } else if (name.trim().length < 2) {
      newErrors.name = 'Name must be at least 2 characters';
    }
    if (!email.trim()) {
      newErrors.email = 'Email address is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = 'Please enter a valid email address';
    }
    if (!password) {
      newErrors.password = 'Password is required';
    } else if (password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
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
      // TODO: Replace with actual API call — e.g. await api.post('/api/auth/register', { name, email, password })
      await new Promise((_, reject) => setTimeout(() => reject(new Error('not_implemented')), 800));
      navigate('/login');
    } catch (err) {
      if (err.message === 'not_implemented') {
        setSubmitError('Registration service is not connected yet. Please configure the backend API.');
      } else {
        setSubmitError(err.response?.data?.detail || 'Account creation failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleGitHubSignUp = () => {
    setSubmitError('GitHub authentication is not configured yet.');
    setTimeout(() => setSubmitError(''), 4000);
  };

  // Password strength indicator
  const getPasswordStrength = () => {
    if (!password) return { label: '', color: '', width: '0%' };
    if (password.length < 6) return { label: 'Weak', color: 'bg-rose-400', width: '25%' };
    if (password.length < 8) return { label: 'Fair', color: 'bg-amber-400', width: '50%' };
    if (password.length < 12) return { label: 'Good', color: 'bg-emerald-400', width: '75%' };
    return { label: 'Strong', color: 'bg-emerald-500', width: '100%' };
  };

  const strength = getPasswordStrength();

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-['Hanken_Grotesk',sans-serif] flex flex-col justify-between relative overflow-hidden">
      {/* Top Bar — Light mode */}
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
      <main className="flex-1 flex items-center justify-center px-4 pt-24 pb-12 z-10">
        <div className="w-full max-w-md bg-white border border-slate-200 rounded-2xl p-8 shadow-xl animate-slide-up">
          <div className="text-center mb-8 animate-fade-in-up">
            <h1 className="text-2xl font-bold text-slate-900 mb-2">Create your Smart RAG account</h1>
            <p className="text-xs text-slate-500">Start building your intelligent knowledge base today</p>
          </div>

          {/* Global submit error */}
          {submitError && (
            <div className="mb-5 p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-700 font-medium flex items-center gap-2 animate-fade-in-up">
              <span className="material-symbols-outlined text-sm">error</span>
              {submitError}
            </div>
          )}

          <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2 font-['JetBrains_Mono',monospace]">
                Full Name
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => { setName(e.target.value); setErrors((prev) => ({ ...prev, name: '' })); }}
                placeholder="Your full name"
                className={`w-full bg-slate-50 border rounded-xl px-4 py-3 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none transition-all ${
                  errors.name ? 'border-rose-400 focus:border-rose-500 focus:ring-1 focus:ring-rose-500' : 'border-slate-200 focus:border-amber-500 focus:ring-1 focus:ring-amber-500'
                }`}
              />
              {errors.name && (
                <p className="mt-1.5 text-xs text-rose-600 flex items-center gap-1 animate-fade-in-up">
                  <span className="material-symbols-outlined text-xs">warning</span>
                  {errors.name}
                </p>
              )}
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2 font-['JetBrains_Mono',monospace]">
                Work Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => { setEmail(e.target.value); setErrors((prev) => ({ ...prev, email: '' })); }}
                placeholder="you@company.com"
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
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2 font-['JetBrains_Mono',monospace]">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => { setPassword(e.target.value); setErrors((prev) => ({ ...prev, password: '' })); }}
                placeholder="Minimum 8 characters"
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
              {/* Password strength bar */}
              {password && (
                <div className="mt-2 animate-fade-in">
                  <div className="w-full h-1 bg-slate-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${strength.color}`}
                      style={{ width: strength.width }}
                    />
                  </div>
                  <p className="text-[10px] text-slate-400 mt-1 text-right">{strength.label}</p>
                </div>
              )}
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-amber-500 hover:bg-amber-600 disabled:opacity-60 text-white font-bold rounded-xl text-sm transition-all shadow-md hover:shadow-lg hover:scale-[1.01] active:scale-[0.99] flex items-center justify-center gap-2 mt-3"
            >
              {loading ? (
                <>
                  <span className="material-symbols-outlined text-lg animate-spin">sync</span>
                  Creating account...
                </>
              ) : (
                <>
                  <span className="material-symbols-outlined text-lg">person_add</span>
                  Create Account
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
            onClick={handleGitHubSignUp}
            className="w-full py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-medium rounded-xl text-xs transition-all shadow-sm hover:shadow-md hover:scale-[1.01] active:scale-[0.99] flex items-center justify-center gap-2"
          >
            <span className="material-symbols-outlined text-base">code</span>
            Continue with GitHub
          </button>

          <p className="text-center text-xs text-slate-500 mt-6">
            Already have an account?{' '}
            <Link to="/login" className="text-amber-600 font-semibold hover:underline">
              Sign in instead
            </Link>
          </p>
        </div>
      </main>

      {/* Footer */}
      <footer className="py-4 text-center text-xs text-slate-400 border-t border-slate-200 bg-white">
        <p>© 2026 Smart RAG Inc. · System Status: Operational</p>
      </footer>
    </div>
  );
}
