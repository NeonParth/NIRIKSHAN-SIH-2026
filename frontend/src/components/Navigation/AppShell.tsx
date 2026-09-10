import { useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

const links = [
  { to: "/", label: "Dashboard", icon: "📊" },
  { to: "/projects", label: "Projects", icon: "📁" },
  { to: "/risks", label: "Risk Analysis", icon: "⚠️" },
  { to: "/map", label: "Risk Map", icon: "🗺️" },
  { to: "/investigation", label: "Investigation", icon: "🔍" },
];

export function AppShell() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-slate-100 flex text-slate-900 font-sans">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:left-4 focus:top-4 focus:bg-white focus:text-slate-900 focus:px-4 focus:py-2 focus:rounded-md focus:shadow-lg"
      >
        Skip to content
      </a>

      {/* Mobile Backdrop */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-30 bg-slate-950/60 lg:hidden"
          onClick={() => setMobileOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Left Vertical Sidebar */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-40 w-64 bg-slate-900 text-white flex flex-col transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        } shadow-xl border-r border-slate-800`}
      >
        {/* Branding Area */}
        <div className="p-6 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-lg bg-blue-900/80 border border-blue-500/50 flex items-center justify-center font-bold text-xl text-blue-300 shadow-inner">
              N
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight text-white leading-tight">
                NIRIKSHAN
              </h1>
              <p className="text-[10px] uppercase tracking-wider text-slate-400 font-medium">
                Monitoring & Development
              </p>
            </div>
          </div>
          <button
            onClick={() => setMobileOpen(false)}
            className="lg:hidden text-slate-400 hover:text-white p-1"
            aria-label="Close sidebar"
          >
            ✕
          </button>
        </div>

        {/* Primary Navigation */}
        <nav aria-label="Primary" className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === "/"}
              onClick={() => setMobileOpen(false)}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? "bg-blue-600 text-white shadow-md font-semibold"
                    : "text-slate-300 hover:bg-slate-800 hover:text-white"
                }`
              }
            >
              <span className="text-base" aria-hidden="true">{link.icon}</span>
              <span>{link.label}</span>
            </NavLink>
          ))}

        </nav>

        {/* User Status & Logout Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/50">
          {user ? (
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 rounded-full bg-slate-700 text-slate-200 flex items-center justify-center text-xs font-semibold">
                  {user.username.charAt(0).toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-semibold text-slate-200 truncate">
                    {user.username}
                  </p>
                  <p className="text-[10px] text-slate-400 truncate">
                    {user.role}
                  </p>
                </div>
              </div>
              <button
                onClick={handleLogout}
                className="w-full text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white py-1.5 px-3 rounded-md transition-colors border border-slate-700"
              >
                Sign Out
              </button>
            </div>
          ) : (
            <NavLink
              to="/login"
              className="block text-center text-xs bg-blue-600 hover:bg-blue-500 text-white py-2 px-3 rounded-md transition-colors font-medium"
            >
              Authority Login
            </NavLink>
          )}
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 lg:pl-64">
        {/* Mobile Header Bar */}
        <header className="lg:hidden bg-slate-900 text-white px-4 py-3 flex items-center justify-between border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setMobileOpen(true)}
              className="p-2 rounded-md hover:bg-slate-800 text-slate-300"
              aria-label="Open sidebar"
            >
              ☰
            </button>
            <span className="font-bold text-sm">NIRIKSHAN</span>
          </div>
          <span className="text-xs text-slate-400 font-medium">Monitoring & Development</span>
        </header>

        <main id="main" className="flex-1 p-4 md:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
