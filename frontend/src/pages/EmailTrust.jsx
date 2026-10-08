import React, { useState } from 'react';

export default function EmailTrust() {
  const [activeTab, setActiveTab] = useState('address');
  const [addressInput, setAddressInput] = useState('');
  const [contentInput, setContentInput] = useState({ sender: '', subject: '', body: '' });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Static telemetry metrics bar
  const metrics = { scanned: 1420, safe: 1180, warning: 165, blocked: 75 };

  const handleVerifyAddress = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch('/api/email-trust/verify-address', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: addressInput })
      });

      if (!res.ok) {
        throw new Error(`Server returned status ${res.status}`);
      }

      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      setError('Failed to verify address. Ensure your FastAPI backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeContent = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch('/api/email-trust/analyze-content', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(contentInput)
      });

      if (!res.ok) {
        throw new Error(`Server returned status ${res.status}`);
      }

      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      setError('Failed to analyze content. Ensure your FastAPI backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (decision) => {
    if (decision === 'ALLOW') return 'text-emerald-400 border-emerald-500 bg-emerald-500/10';
    if (decision === 'WARN') return 'text-amber-400 border-amber-500 bg-amber-500/10';
    return 'text-rose-400 border-rose-500 bg-rose-500/10';
  };

  return (
    <div className="p-6 bg-slate-950 text-slate-100 min-h-screen space-y-6 font-sans">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Enterprise Email Trust Engine</h1>
          <p className="text-sm text-slate-400">Evaluate vector security posture indicators prior to ecosystem delivery.</p>
        </div>
        <button 
          onClick={() => alert('Telemetry report exported.')}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-sm font-medium rounded-lg border border-slate-700 transition"
        >
          Export Telemetry
        </button>
      </div>

      {/* Metrics Indicator Counter Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Emails Scanned</p>
          <p className="text-2xl font-bold mt-1 text-blue-400">{metrics.scanned}</p>
        </div>
        <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Safe Emails</p>
          <p className="text-2xl font-bold mt-1 text-emerald-400">{metrics.safe}</p>
        </div>
        <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Suspicious Emails</p>
          <p className="text-2xl font-bold mt-1 text-amber-400">{metrics.warning}</p>
        </div>
        <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">High Risk Emails</p>
          <p className="text-2xl font-bold mt-1 text-rose-400">{metrics.blocked}</p>
        </div>
      </div>

      {/* Tab Selectors */}
      <div className="flex space-x-2 border-b border-slate-800 pb-px">
        <button
          type="button"
          onClick={() => { setActiveTab('address'); setResult(null); setError(null); }}
          className={`pb-3 text-sm font-medium tracking-wide border-b-2 px-1 transition ${
            activeTab === 'address' ? 'border-blue-500 text-blue-400' : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Email Address Verification
        </button>
        <button
          type="button"
          onClick={() => { setActiveTab('content'); setResult(null); setError(null); }}
          className={`pb-3 text-sm font-medium tracking-wide border-b-2 px-1 transition ${
            activeTab === 'content' ? 'border-blue-500 text-blue-400' : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Email Content Analysis
        </button>
      </div>

      {/* Primary Workspace Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Form Column */}
        <div className="lg:col-span-5 bg-slate-900 border border-slate-800 p-5 rounded-xl space-y-4">
          {activeTab === 'address' ? (
            <form onSubmit={handleVerifyAddress} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold uppercase text-slate-400 mb-2">Email Address Target</label>
                <input
                  type="text"
                  placeholder="e.g. security@company.com"
                  className="w-full bg-slate-950 border border-slate-800 focus:border-blue-500 rounded-lg p-3 text-sm outline-none text-slate-100 transition"
                  value={addressInput}
                  onChange={(e) => setAddressInput(e.target.value)}
                  required
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 font-medium text-sm rounded-lg transition"
              >
                {loading ? 'Running Verification...' : 'Verify Email Signatures'}
              </button>
            </form>
          ) : (
            <form onSubmit={handleAnalyzeContent} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">Sender Email</label>
                <input
                  type="email"
                  placeholder="sender@untrusted.com"
                  className="w-full bg-slate-950 border border-slate-800 focus:border-blue-500 rounded-lg p-2.5 text-sm outline-none text-slate-100 transition"
                  value={contentInput.sender}
                  onChange={(e) => setContentInput({ ...contentInput, sender: e.target.value })}
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">Subject Header</label>
                <input
                  type="text"
                  placeholder="Security Alert Notification"
                  className="w-full bg-slate-950 border border-slate-800 focus:border-blue-500 rounded-lg p-2.5 text-sm outline-none text-slate-100 transition"
                  value={contentInput.subject}
                  onChange={(e) => setContentInput({ ...contentInput, subject: e.target.value })}
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">Email Body Content</label>
                <textarea
                  rows={5}
                  placeholder="Paste raw inbound transmission content payload fields..."
                  className="w-full bg-slate-950 border border-slate-800 focus:border-blue-500 rounded-lg p-2.5 text-sm outline-none text-slate-100 transition resize-none"
                  value={contentInput.body}
                  onChange={(e) => setContentInput({ ...contentInput, body: e.target.value })}
                  required
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 font-medium text-sm rounded-lg transition"
              >
                {loading ? 'Analyzing Content...' : 'Analyze Threat Indicators'}
              </button>
            </form>
          )}
        </div>

        {/* Dynamic Display Panel */}
        <div className="lg:col-span-7">
          {error && (
            <div className="bg-rose-950/40 border border-rose-800/60 p-4 rounded-xl text-rose-300 text-sm">
              {error}
            </div>
          )}

          {result && (
            <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden space-y-0">
              <div className="p-4 bg-slate-900/50 border-b border-slate-800 flex justify-between items-center">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                  Unified System Metric Execution Report
                </span>
                <span className={`px-2.5 py-1 text-xs font-bold border rounded-md uppercase ${getStatusColor(result.decision)}`}>
                  {result.decision}
                </span>
              </div>

              <div className="p-5 space-y-4">
                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800/60 text-center">
                    <p className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Trust Score</p>
                    <p className="text-xl font-bold mt-1 text-slate-200">{result.trust_score}/100</p>
                  </div>
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800/60 text-center">
                    <p className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Confidence</p>
                    <p className="text-xl font-bold mt-1 text-slate-200">{result.confidence}%</p>
                  </div>
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800/60 text-center">
                    <p className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Risk Level</p>
                    <p className="text-xl font-bold mt-1 text-slate-200">{result.risk}</p>
                  </div>
                </div>

                {/* Direct display of backend reasons */}
                {result.reasons && result.reasons.length > 0 && (
                  <div className="pt-2">
                    <p className="text-xs font-semibold uppercase text-slate-400 mb-2">Analysis Reasons & Signals</p>
                    <ul className="space-y-1.5">
                      {result.reasons.map((reason, idx) => (
                        <li key={idx} className="text-xs text-slate-300 bg-slate-950 p-2 rounded-md border border-slate-800/60">
                          • {reason}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Direct display of extracted flags if available */}
                {result.flags && result.flags.length > 0 && (
                  <div className="pt-2">
                    <p className="text-xs font-semibold uppercase text-slate-400 mb-2">Detected Threat Keywords</p>
                    <div className="flex flex-wrap gap-2">
                      {result.flags.map((flag, idx) => (
                        <span key={idx} className="px-2.5 py-1 bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs rounded-md">
                          {flag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {!result && !error && (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 text-center text-slate-500">
              Run verification or content analysis to display telemetry reports.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}