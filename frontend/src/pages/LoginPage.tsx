import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export function LoginPage() {
  const [username, setUsername] = useState("authority_demo@nirikshan.gov.in");
  const [password, setPassword] = useState("••••••••••••");
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    login(username);
    navigate("/");
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center items-center p-4 text-slate-100">
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-xl shadow-2xl p-8 space-y-6">
        <div className="text-center space-y-2">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-lg bg-blue-900/60 border border-blue-500/40 text-blue-400 font-bold text-xl mb-2">
            N
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">NIRIKSHAN</h1>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-400 font-medium">
            Monitoring & Development
          </p>
        </div>

        <div className="bg-amber-950/40 border border-amber-800/50 rounded-lg p-3 text-xs text-amber-300 text-center">
          <strong>DEMO AUTHORITY LOGIN</strong>
          <br />
          Local demonstration authentication for SIH presentation.
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1">
              Authority Email / Username
            </label>
            <input
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-md px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="authority@nirikshan.gov.in"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1">
              Password
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-md px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="••••••••••••"
            />
          </div>

          <button
            type="submit"
            className="w-full bg-blue-600 hover:bg-blue-500 font-semibold py-2.5 px-4 rounded-md text-sm text-white transition-colors duration-150 shadow-md focus:outline-none focus:ring-2 focus:ring-blue-400"
          >
            Access Monitoring Dashboard
          </button>
        </form>

        <div className="text-center pt-2">
          <p className="text-[11px] text-slate-500">
            Smart India Hackathon • MPLADS Project Intelligence System
          </p>
        </div>
      </div>
    </div>
  );
}
