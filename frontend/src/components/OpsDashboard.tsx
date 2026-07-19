import React, { useEffect, useState, useMemo, useRef } from 'react';
import { Activity, Users, ShieldAlert, Zap, BarChart2 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import './OpsDashboard.css';

// Interfaces for strict typing
interface ZoneData {
  name: string;
  occupancy: number;
  capacity: number;
}

interface AlertData {
  priority: string;
  action: string;
  reason: string;
}

// Mock data for initial render
const MOCK_ZONES: ZoneData[] = [
  { name: 'North Stand', occupancy: 12500, capacity: 15000 },
  { name: 'South Stand', occupancy: 14200, capacity: 15000 },
  { name: 'East Stand', occupancy: 8000, capacity: 12000 },
  { name: 'West Stand', occupancy: 11000, capacity: 12000 },
  { name: 'Fan Zone', occupancy: 7500, capacity: 8000 },
];

const OpsDashboard: React.FC = () => {
  const [zones, setZones] = useState<ZoneData[]>(MOCK_ZONES);
  const [recommendations, setRecommendations] = useState<AlertData[]>([
    {
      priority: 'High',
      action: 'Deploy extra stewards to South Stand',
      reason: 'Occupancy is approaching 95% capacity.'
    }
  ]);
  const [isConnected, setIsConnected] = useState(false);
  
  // Use a ref to store the websocket to prevent stale closures
  const wsRef = useRef<WebSocket | null>(null);
  
  const WS_URL = import.meta.env.VITE_WS_URL || 'wss://stadium-pulse-ai-t33k.onrender.com/api/v1/ws/crowd';

  useEffect(() => {
    let reconnectTimeout: ReturnType<typeof setTimeout>;
    
    const connect = () => {
      if (wsRef.current?.readyState === WebSocket.OPEN) return;
      
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.zones) {
            const updatedZones = data.zones.map((z: { name: string; current_occupancy: number; capacity: number }) => ({
              name: z.name,
              occupancy: z.current_occupancy,
              capacity: z.capacity
            }));
            setZones(updatedZones);
          }
          if (data.alerts) {
            const updatedRecommendations = data.alerts.map((a: { level: string; zone_name: string; message: string }) => ({
              priority: a.level === 'critical' ? 'High' : 'Medium',
              action: `Review status in ${a.zone_name}`,
              reason: a.message
            }));
            setRecommendations(updatedRecommendations.length > 0 ? updatedRecommendations : [
              { priority: 'Low', action: 'All clear', reason: 'No immediate action required.' }
            ]);
          }
        } catch {
          // Silent error handling for WebSocket JSON parse
        }
      };
      
      ws.onclose = () => {
        setIsConnected(false);
        wsRef.current = null;
        // Attempt to reconnect after 3 seconds
        reconnectTimeout = setTimeout(connect, 3000);
      };
      
      ws.onerror = () => {
        // Silent error handler. The connection will likely close, triggering onclose and reconnect.
      };
    };

    connect();

    return () => {
      clearTimeout(reconnectTimeout);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [WS_URL]);

  // Memoize heavy calculations for React Efficiency
  const { totalOccupancy, totalCapacity, overallDensity } = useMemo(() => {
    const occ = zones.reduce((acc, z) => acc + z.occupancy, 0);
    const cap = zones.reduce((acc, z) => acc + z.capacity, 0);
    const den = cap > 0 ? (occ / cap) * 100 : 0;
    return { totalOccupancy: occ, totalCapacity: cap, overallDensity: den };
  }, [zones]);

  return (
    <main className="ops-container" aria-label="Operations Command Center Dashboard">
      <header className="ops-header">
        <div>
          <h2 className="gradient-text" id="ops-heading">Operations Command Center</h2>
          <p>Live stadium telemetry and AI insights</p>
        </div>
        <div className={`status-badge ${isConnected ? 'live' : 'offline'}`} aria-live="polite">
          <span className="pulse-dot" aria-hidden="true" style={{ backgroundColor: isConnected ? '' : '#ef4444' }}></span>
          {isConnected ? 'LIVE SYSTEM ACTIVE' : 'RECONNECTING...'}
        </div>
      </header>

      <section className="metrics-grid" aria-label="Key Metrics">
        <article className="metric-card glass-panel">
          <div className="metric-icon" aria-hidden="true"><Users size={24} /></div>
          <div className="metric-info">
            <h3 id="occupancy-label">Total Occupancy</h3>
            <p className="metric-value" aria-labelledby="occupancy-label">{totalOccupancy.toLocaleString()}</p>
            <span className="metric-subtitle">Out of {totalCapacity.toLocaleString()}</span>
          </div>
        </article>

        <article className="metric-card glass-panel">
          <div className="metric-icon warning" aria-hidden="true"><Activity size={24} /></div>
          <div className="metric-info">
            <h3 id="density-label">Overall Density</h3>
            <p className="metric-value" aria-labelledby="density-label">{overallDensity.toFixed(1)}%</p>
            <div 
              className="progress-bar" 
              role="progressbar" 
              aria-valuenow={Math.round(overallDensity)} 
              aria-valuemin={0} 
              aria-valuemax={100}
              aria-label="Overall stadium density"
            >
              <div 
                className="progress-fill warning" 
                style={{ width: `${overallDensity}%` }}
              ></div>
            </div>
          </div>
        </article>
      </section>

      <div className="dashboard-main">
        <section className="chart-section glass-panel" aria-label="Zone Density Analytics">
          <header className="section-header">
            <BarChart2 size={20} className="section-icon" aria-hidden="true" />
            <h3>Zone Density Analytics</h3>
          </header>
          <div className="chart-container" aria-hidden="true">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={zones} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                <XAxis dataKey="name" stroke="#a1a1aa" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#a1a1aa" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#18181b', borderColor: '#3f3f46', borderRadius: '8px' }}
                  itemStyle={{ color: '#f8fafc' }}
                />
                <Bar dataKey="occupancy" radius={[4, 4, 0, 0]}>
                  {zones.map((entry, index) => {
                    const percent = entry.occupancy / entry.capacity;
                    return <Cell key={`cell-${index}`} fill={percent > 0.9 ? '#ef4444' : percent > 0.75 ? '#f59e0b' : '#3b82f6'} />;
                  })}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="ai-section glass-panel" aria-label="AI Recommendations">
          <header className="section-header">
            <Zap size={20} className="section-icon glow" aria-hidden="true" />
            <h3>AI Recommendations</h3>
          </header>
          
          <div className="recommendations-list" aria-live="polite">
            {recommendations.map((rec, i) => (
              <article key={i} className={`rec-card ${rec.priority.toLowerCase()}`}>
                <header className="rec-header">
                  <ShieldAlert size={16} aria-hidden="true" />
                  <span className="priority-badge">{rec.priority} Priority</span>
                </header>
                <h4>{rec.action}</h4>
                <p>{rec.reason}</p>
              </article>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
};

export default OpsDashboard;
