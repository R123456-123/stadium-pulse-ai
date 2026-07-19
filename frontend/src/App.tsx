import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Navigate, NavLink } from 'react-router-dom';
import { Bot, Activity, Menu, Zap, Loader2 } from 'lucide-react';
import './components/Layout.css';

const FanChat = lazy(() => import('./components/FanChat'));
const OpsDashboard = lazy(() => import('./components/OpsDashboard'));

const Layout = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="layout-container">
      {/* Sidebar */}
      <aside className="sidebar glass-panel">
        <div className="sidebar-brand">
          <Zap className="brand-icon" size={28} />
          <h1 className="brand-text">Stadium<span className="gradient-text">Pulse</span></h1>
        </div>
        
        <nav className="sidebar-nav" aria-label="Main Navigation">
          <NavLink 
            to="/chat" 
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            aria-label="Fan Assistant Chat"
          >
            <Bot size={20} aria-hidden="true" />
            <span>Fan Assistant</span>
          </NavLink>
          
          <NavLink 
            to="/ops" 
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            aria-label="Operations Dashboard"
          >
            <Activity size={20} aria-hidden="true" />
            <span>Ops Dashboard</span>
          </NavLink>
        </nav>
      </aside>

      {/* Main Content Area */}
      <main className="main-content">
        {/* Mobile Header */}
        <header className="mobile-header glass-panel">
          <div className="sidebar-brand">
            <Zap className="brand-icon" size={24} />
            <h1 className="brand-text">Stadium<span className="gradient-text">Pulse</span></h1>
          </div>
          <button className="menu-btn">
            <Menu size={24} />
          </button>
        </header>

        <div className="page-container">
          {children}
        </div>
      </main>
    </div>
  );
};

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Suspense fallback={
          <div style={{ display: 'flex', height: '100%', alignItems: 'center', justifyContent: 'center', color: '#a1a1aa' }}>
            <Loader2 className="spinner" size={32} />
          </div>
        }>
          <Routes>
            <Route path="/" element={<Navigate to="/chat" replace />} />
            <Route path="/chat" element={<FanChat />} />
            <Route path="/ops" element={<OpsDashboard />} />
          </Routes>
        </Suspense>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
