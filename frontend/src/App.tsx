import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, NavLink } from 'react-router-dom';
import { Bot, Activity, Menu, Zap } from 'lucide-react';
import FanChat from './components/FanChat';
import OpsDashboard from './components/OpsDashboard';
import './components/Layout.css';

const Layout = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="layout-container">
      {/* Sidebar */}
      <aside className="sidebar glass-panel">
        <div className="sidebar-brand">
          <Zap className="brand-icon" size={28} />
          <h1 className="brand-text">Stadium<span className="gradient-text">Pulse</span></h1>
        </div>
        
        <nav className="sidebar-nav">
          <NavLink 
            to="/chat" 
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <Bot size={20} />
            <span>Fan Assistant</span>
          </NavLink>
          
          <NavLink 
            to="/ops" 
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <Activity size={20} />
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
        <Routes>
          <Route path="/" element={<Navigate to="/chat" replace />} />
          <Route path="/chat" element={<FanChat />} />
          <Route path="/ops" element={<OpsDashboard />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
