import React, { useState, useEffect, useRef } from 'react';
import {
  Briefcase,
  Download,
  Play,
  RefreshCcw,
  CheckCircle,
  AlertCircle,
  Search,
  Zap,
  Layout,
  Globe,
  Globe2,
  Languages,
  Filter,
  Terminal,
  ChevronRight,
  TrendingUp,
  Mail,
  ExternalLink
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const JobAgentDashboard = () => {
  const [status, setStatus] = useState({
    active: false,
    progress: 0,
    message: 'Idle',
    job_count: 0,
    ready_to_download: false,
    current_role: '',
    filters: null
  });

  const [stats, setStats] = useState({
    total_jobs: 0,
    total_scans: 0
  });

  const [savedJobs, setSavedJobs] = useState([]);

  const [filters, setFilters] = useState({
    roles: ['Frontend Developer', 'Nurse'],
    location: 'Germany',
    language: 'English'
  });

  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState([]);
  const logEndRef = useRef(null);

  const roleCategories = {
    "Tech & IT": ["Frontend Developer", "Backend Developer", "Fullstack Developer", "DevOps Engineer", "Data Scientist", "Mobile Developer"],
    "Healthcare": ["Nurse", "Doctor", "Pharmacist", "Physiotherapist"],
    "Trade & Skilled": ["Electrician", "Plumber", "Carpenter", "Construction Worker"],
    "Business & MGMT": ["Project Manager", "Product Manager", "Marketing Manager", "HR Specialist"]
  };

  const languages = [
    { name: "English", code: "en", label: "🇺🇸 English Only" },
    { name: "German", code: "de", label: "🇩🇪 German" },
    { name: "French", code: "fr", label: "🇫🇷 French" },
    { name: "Spanish", code: "es", label: "🇪🇸 Spanish" },
    { name: "Italian", code: "it", label: "🇮🇹 Italian" },
    { name: "All", code: "all", label: "🌍 All Languages" }
  ];

  const fetchStatus = async () => {
    try {
      const res = await fetch('/api/status');
      const data = await res.json();

      // If status just became inactive after being active, refresh stats
      if (!data.active && status.active) {
        fetchStats();
      }

      setStatus(data);

      if (!data.active && data.message === 'Idle') {
        setLoading(false);
      }

      // Update logs based on status message changes
      if (data.active && data.message !== status.message) {
        addLog(data.message, 'info');
      }
    } catch (err) {
      console.error('Failed to fetch status:', err);
    }
  };

  const fetchStats = async () => {
    try {
      const res = await fetch('/api/stats');
      const data = await res.json();
      setStats(data);
      if (data.total_jobs > 0) fetchSavedJobs();
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  const fetchSavedJobs = async () => {
    try {
      const res = await fetch('/api/jobs?limit=5');
      const data = await res.json();
      setSavedJobs(data);
    } catch (err) {
      console.error('Failed to fetch jobs:', err);
    }
  };

  const addLog = (message, type = 'info') => {
    const time = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, { time, message, type }].slice(-50));
  };

  useEffect(() => {
    fetchStats();
    fetchStatus();
    const interval = setInterval(fetchStatus, 3000);
    return () => clearInterval(interval);
  }, [status.message]);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const handleStartSearch = async () => {
    setLoading(true);
    setLogs([{ time: new Date().toLocaleTimeString(), message: 'Initializing agent clusters...', type: 'system' }]);
    try {
      const res = await fetch('/api/start-search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(filters)
      });
      const data = await res.json();
      if (data.error) {
        addLog(data.error, 'error');
        setLoading(false);
      } else {
        addLog('Search mission launched successfully', 'success');
      }
    } catch (err) {
      addLog('Failed to establish connection with agent', 'error');
      setLoading(false);
    }
  };

  const toggleRole = (role) => {
    setFilters(prev => ({
      ...prev,
      roles: prev.roles.includes(role)
        ? prev.roles.filter(r => r !== role)
        : [...prev.roles, role]
    }));
  };

  return (
    <div className="min-h-screen bg-[#0b0e14] text-white font-sans selection:bg-cyan-500/30 overflow-x-hidden relative">
      {/* Dynamic Background */}
      <div className="fixed inset-0 z-0">
        <div className="absolute top-[-10%] left-[-10%] w-[800px] h-[800px] bg-cyan-500/10 blur-[150px] rounded-full animate-blob pointer-events-none" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[900px] h-[900px] bg-purple-600/10 blur-[150px] rounded-full animate-blob-slow pointer-events-none" />
      </div>

      <main className="max-w-7xl mx-auto px-6 py-12 relative z-10">
        {/* Nav / Header */}
        <header className="flex justify-between items-center mb-16 px-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gradient-to-br from-cyan-400 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Zap size={28} className="text-black" fill="black" />
            </div>
            <div>
              <h1 className="text-2xl font-black tracking-tighter">JOBAGENT <span className="text-cyan-400">PRO</span></h1>
              <p className="text-[10px] text-gray-500 uppercase tracking-widest font-bold">Enterprise SaaS Edition</p>
            </div>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-gray-400">
            <a href="#" className="hover:text-white transition-colors">Dashboard</a>
            <a href="#" className="hover:text-white transition-colors">Analytics</a>
            <a href="#" className="hover:text-white transition-colors">Settings</a>
            <div className="h-8 w-px bg-white/10" />
            <div className="flex items-center gap-3 bg-white/5 border border-white/10 rounded-full px-4 py-2 text-xs">
              <div className="w-2 h-2 rounded-full bg-green-500" />
              <span>API ACTIVE</span>
            </div>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">

          {/* Left Column: Filters & Config */}
          <div className="lg:col-span-4 space-y-6">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="glass-card p-8 border-cyan-400/10 shadow-[0_20px_50px_rgba(0,0,0,0.5)]"
            >
              <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-cyan-400/10 rounded-lg">
                    <Filter size={20} className="text-cyan-400" />
                  </div>
                  <h2 className="text-lg font-black tracking-tight">Select Filters</h2>
                </div>
                <div className="text-[10px] font-bold text-gray-500 uppercase px-2 py-1 bg-white/5 rounded-md">Config</div>
              </div>

              {/* Roles Selection (Categorized) */}
              <div className="mb-8">
                <label className="text-xs font-bold text-gray-500 uppercase mb-4 block tracking-widest">Target Personnel</label>
                <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                  {Object.entries(roleCategories).map(([category, roles]) => (
                    <div key={category}>
                      <p className="text-[10px] font-bold text-cyan-400/60 uppercase mb-2 ml-1">{category}</p>
                      <div className="flex flex-wrap gap-2">
                        {roles.map(role => (
                          <button
                            key={role}
                            onClick={() => toggleRole(role)}
                            className={`px-3 py-1.5 rounded-xl text-xs font-semibold border transition-all duration-300 ${filters.roles.includes(role)
                              ? 'bg-cyan-500/20 border-cyan-400/50 text-white shadow-[0_0_20px_rgba(34,211,238,0.15)] scale-[1.05]'
                              : 'bg-white/5 border-white/5 text-gray-400 hover:border-white/20'
                              }`}
                          >
                            {role}
                          </button>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Location Input */}
              <div className="mb-8">
                <label className="text-xs font-bold text-gray-500 uppercase mb-3 block tracking-widest">Geographic Focus</label>
                <div className="relative group">
                  <Globe className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-cyan-400 transition-colors" size={18} />
                  <input
                    type="text"
                    value={filters.location}
                    onChange={(e) => setFilters(prev => ({ ...prev, location: e.target.value }))}
                    className="w-full glass-input pl-12 py-4 text-sm font-medium"
                    placeholder="e.g. Germany, Berlin, Remote"
                  />
                </div>
              </div>

              {/* Language Selector */}
              <div className="mb-10">
                <label className="text-xs font-bold text-gray-500 uppercase mb-3 block tracking-widest">Language Strictness</label>
                <div className="grid grid-cols-2 gap-2">
                  {languages.map(lang => (
                    <button
                      key={lang.name}
                      onClick={() => setFilters(prev => ({ ...prev, language: lang.name }))}
                      className={`flex items-center justify-center py-3 rounded-2xl text-[11px] font-black border transition-all duration-300 ${filters.language === lang.name
                        ? 'bg-gradient-to-br from-white/15 to-white/5 border-white/30 text-white shadow-xl'
                        : 'bg-transparent border-white/5 text-gray-500 hover:bg-white/5'
                        }`}
                    >
                      {lang.label}
                    </button>
                  ))}
                </div>
                {filters.language === 'English' && (
                  <p className="text-[10px] text-cyan-400/80 mt-3 flex items-center gap-1.5 px-1 font-medium animate-pulse">
                    <CheckCircle size={10} /> Strict mode active: German requirements will be auto-discarded
                  </p>
                )}
              </div>

              <button
                onClick={handleStartSearch}
                disabled={status.active || loading}
                className={`w-full group relative flex items-center justify-center gap-3 px-8 py-4 rounded-2xl font-bold transition-all 
                  ${status.active
                    ? 'bg-white/5 text-gray-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-cyan-400 to-blue-500 text-black hover:shadow-cyan-500/40 hover:scale-[1.02] active:scale-95 shadow-[0_10px_30px_rgba(34,211,238,0.2)]'}`}
              >
                {status.active ? (
                  <RefreshCcw className="animate-spin" size={20} />
                ) : (
                  <Play size={20} fill="black" />
                )}
                <span className="tracking-tight">{status.active ? 'AGENT ACTIVE' : 'LAUNCH DISCOVERY'}</span>
                {!status.active && <ChevronRight size={18} className="group-hover:translate-x-1 transition-transform" />}
              </button>
            </motion.div>

            {/* Quick Stats Block */}
            <div className="grid grid-cols-2 gap-4">
              <div className="glass-card p-6 bg-gradient-to-br from-cyan-500/10 to-transparent">
                <p className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1">Saved Database</p>
                <h3 className="text-2xl font-black">{stats.total_jobs}</h3>
                <p className="text-[9px] text-cyan-400 font-bold uppercase mt-1">Global Leads</p>
              </div>
              <div className="glass-card p-6 border-white/5">
                <p className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1">Deployments</p>
                <h3 className="text-2xl font-black">{stats.total_scans}</h3>
                <p className="text-[9px] text-gray-500 font-bold uppercase mt-1">Total Scans</p>
              </div>
            </div>
          </div>

          {/* Right Column: Status & Feed */}
          <div className="lg:col-span-8 space-y-6">

            {/* Status Panel */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass-card p-8 min-h-[300px] flex flex-col justify-between"
            >
              <div className="flex justify-between items-start">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                    <span className="text-xs font-bold text-cyan-400 uppercase tracking-widest">{status.active ? 'Processing...' : 'Ready'}</span>
                  </div>
                  <h2 className="text-4xl font-black tracking-tighter">
                    {status.active ? status.current_role : 'Idle Mode'}
                  </h2>
                </div>
                {status.ready_to_download && (
                  <div className="flex flex-col items-end gap-2">
                    <a
                      href={`/api/download-report?v=${Date.now()}`}
                      download="jobs_report.xlsx"
                      target="_self"
                      className="flex items-center gap-2 bg-white text-black px-6 py-3 rounded-2xl font-bold hover:bg-cyan-400 transition-colors cursor-pointer no-underline shadow-lg"
                      onClick={() => console.log(`Attempting download from: /api/download-report?v=${Date.now()}`)}
                    >
                      <Download size={20} />
                      EXPORT DATA
                    </a>
                    <p className="text-[9px] text-gray-500 italic">Right-click &gt; Save Link As if issue persists</p>
                  </div>
                )}
              </div>

              <div className="my-12 flex items-center gap-8">
                <div>
                  <p className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-1">Discoveries</p>
                  <div className="flex items-baseline gap-2">
                    <span className="text-7xl font-black tabular-nums">{status.job_count}</span>
                    <span className="text-sm font-medium text-gray-400">Total</span>
                  </div>
                </div>
                <div className="h-16 w-px bg-white/10 hidden md:block" />
                <div className="flex-1 hidden md:block">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-[10px] font-bold text-gray-500 uppercase">Real-time Progress</span>
                    <span className="text-[10px] font-bold text-cyan-400">{status.progress}%</span>
                  </div>
                  <div className="h-3 w-full bg-white/5 rounded-full overflow-hidden p-0.5 border border-white/5">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${status.progress}%` }}
                      className="h-full bg-gradient-to-r from-cyan-400 to-blue-600 rounded-full shadow-[0_0_20px_rgba(34,211,238,0.4)]"
                    />
                  </div>
                </div>
              </div>

              <div className="flex flex-wrap gap-4 text-xs font-medium text-gray-500 border-t border-white/5 pt-6">
                <div className="flex items-center gap-1.5 border border-white/10 rounded-full px-3 py-1">
                  <TrendingUp size={14} className="text-purple-400" />
                  <span>LinkedIn Engine</span>
                </div>
                <div className="flex items-center gap-1.5 border border-white/10 rounded-full px-3 py-1">
                  <Briefcase size={14} className="text-yellow-400" />
                  <span>Stepstone Crawler</span>
                </div>
                <div className="flex items-center gap-1.5 border border-white/10 rounded-full px-3 py-1">
                  <Search size={14} className="text-blue-400" />
                  <span>Indeed Query</span>
                </div>
                <div className="flex items-center gap-1.5 border border-white/10 rounded-full px-3 py-1">
                  <Zap size={14} className="text-green-400" />
                  <span>HR Email Extraction</span>
                </div>
              </div>
            </motion.div>

            {/* Event Log / Console */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="glass-card bg-[#000]/40 backdrop-blur-3xl p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <Terminal size={18} className="text-gray-500" />
                  <h2 className="text-xs font-bold uppercase tracking-widest text-gray-500">Event Stream</h2>
                </div>
                <div className="flex gap-1">
                  <div className="w-1.5 h-1.5 rounded-full bg-red-500/50" />
                  <div className="w-1.5 h-1.5 rounded-full bg-yellow-500/50" />
                  <div className="w-1.5 h-1.5 rounded-full bg-green-500/50" />
                </div>
              </div>
              <div className="bg-black/20 rounded-2xl p-4 h-[200px] overflow-y-auto font-mono text-[11px] space-y-2 border border-white/5">
                {logs.length === 0 && <p className="text-gray-600 italic">Agent waiting for instruction...</p>}
                {logs.map((log, i) => (
                  <div key={i} className="flex gap-4 group">
                    <span className="text-gray-600 shrink-0">{log.time}</span>
                    <span className={
                      log.type === 'error' ? 'text-red-400' :
                        log.type === 'success' ? 'text-green-400' :
                          log.type === 'system' ? 'text-purple-400 font-bold' :
                            'text-gray-300'
                    }>
                      {log.message}
                    </span>
                  </div>
                ))}
                <div ref={logEndRef} />
              </div>
            </motion.div>

            {/* Recent Leads Table */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="glass-card p-6"
            >
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <Layout size={18} className="text-cyan-400" />
                  <h2 className="text-xs font-bold uppercase tracking-widest text-gray-500">Recent Persistent Leads</h2>
                </div>
                <button
                  onClick={fetchSavedJobs}
                  className="text-[10px] font-bold text-cyan-400 hover:text-white transition-colors"
                >
                  REFRESH DATABASE
                </button>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="text-gray-500 border-b border-white/5">
                      <th className="pb-3 font-bold uppercase tracking-tighter">Role</th>
                      <th className="pb-3 font-bold uppercase tracking-tighter">Company</th>
                      <th className="pb-3 font-bold uppercase tracking-tighter">Location</th>
                      <th className="pb-3 font-bold uppercase tracking-tighter">Contact</th>
                      <th className="pb-3 text-right font-bold uppercase tracking-tighter">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {savedJobs.length === 0 ? (
                      <tr>
                        <td colSpan="5" className="py-8 text-center text-gray-600 italic">No data in SaaS vault yet...</td>
                      </tr>
                    ) : savedJobs.map((job) => (
                      <tr key={job.id} className="group hover:bg-white/5 transition-colors">
                        <td className="py-4 pr-4">
                          <p className="font-bold text-gray-200 group-hover:text-cyan-400 transition-colors line-clamp-1">{job.title}</p>
                          <p className="text-[9px] text-gray-500 uppercase mt-0.5">{job.source}</p>
                        </td>
                        <td className="py-4 pr-4 font-medium text-gray-400">{job.company}</td>
                        <td className="py-4 pr-4 text-gray-500">{job.location}</td>
                        <td className="py-4 pr-4">
                          {job.emails ? (
                            <div className="flex items-center gap-1.5 text-cyan-400/80">
                              <Mail size={12} />
                              <span className="truncate max-w-[120px]">{job.emails.split('\n')[0]}</span>
                            </div>
                          ) : (
                            <span className="text-gray-700">None found</span>
                          )}
                        </td>
                        <td className="py-4 text-right">
                          <a
                            href={job.link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="bg-white/5 border border-white/10 hover:border-cyan-400/50 hover:bg-cyan-400/10 px-3 py-1.5 rounded-lg transition-all inline-flex items-center gap-1.5 text-[10px] font-bold"
                          >
                            VIEW <ExternalLink size={10} />
                          </a>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </motion.div>
          </div>
        </div>

        {/* Footer info */}
        <footer className="mt-20 border-t border-white/5 pt-12 text-center">
          <div className="flex justify-center gap-12 mb-8 opacity-40 grayscale hover:grayscale-0 hover:opacity-100 transition-all duration-700">
            <img src="https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png" className="h-5" />
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/Indeed_Logo.svg/1024px-Indeed_Logo.svg.png" className="h-5" />
            <div className="text-sm font-black tracking-widest uppercase">STEPSTONE</div>
            <div className="text-sm font-black tracking-widest uppercase flex items-center gap-1">
              <Globe2 size={16} /> STARTUPJOBS
            </div>
          </div>
          <p className="text-[10px] text-gray-600 font-bold tracking-[0.2em] uppercase">
            Designed for scaling & revenue • v2.0.0 Stable
          </p>
        </footer>
      </main>
    </div>
  );
};

export default JobAgentDashboard;
