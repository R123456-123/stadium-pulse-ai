import React, { useEffect, useState } from 'react';
import { Activity, Users, ShieldAlert, Zap, BarChart2 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import './OpsDashboard.css';

// Mock data for initial render
const MOCK_ZONES = [
  { name: 'North Stand', occupancy: 12500, capacity: 15000 },
  { name: 'South Stand', occupancy: 14200, capacity: 15000 },
  { name: 'East Stand', occupancy: 8000, capacity: 12000 },
  { name: 'West Stand', occupancy: 11000, capacity: 12000 },
  { name: 'Fan Zone', occupancy: 7500, capacity: 8000 },
];

const OpsDashboard: React.FC = () => {
  const [zones, setZones] = useState(MOCK_ZONES);
  const [recommendations, setRecommendations] = useState<any[]>([
    {
      priority: 'High',
      action: 'Deploy extra stewards to South Stand',
      reason: 'Occupancy is approaching 95% capacity.'
    }
  ]);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/api/v1/ws/crowd');

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.zones) {
          const updatedZones = data.zones.map((z: any) => ({
            name: z.name,
            occupancy: z.current_occupancy,
            capacity: z.capacity
          }));
          setZones(updatedZones);
        }
        if (data.alerts) {
          const updatedRecommendations = data.alerts.map((a: any) => ({
            priority: a.level === 'critical' ? 'High' : 'Medium',
            action: `Review status in ${a.zone_name}`,
            reason: a.message
          }));
          setRecommendations(updatedRecommendations.length > 0 ? updatedRecommendations : [
            { priority: 'Low', action: 'All clear', reason: 'No immediate action required.' }
          ]);
        }
      } catch (error) {
        console.error('Error parsing websocket data', error);
      }
    };

    return () => {
      ws.close();
    };
  }, []);

  const totalOccupancy = zones.reduce((acc, z) => acc + z.occupancy, 0);
  const totalCapacity = zones.reduce((acc, z) => acc + z.capacity, 0);
  const overallDensity = (totalOccupancy / totalCapacity) * 100;

  return (
    <div className="ops-container">
      <header className="ops-header">
        <div>
          <h2 className="gradient-text">Operations Command Center</h2>
          <p>Live stadium telemetry and AI insights</p>
        </div>
        <div className="status-badge live">
          <span className="pulse-dot"></span>
          LIVE SYSTEM ACTIVE
        </div>
      </header>

      <div className="metrics-grid">
        <div className="metric-card glass-panel">
          <div className="metric-icon"><Users size={24} /></div>
          <div className="metric-info">
            <h3>Total Occupancy</h3>
            <p className="metric-value">{totalOccupancy.toLocaleString()}</p>
            <span className="metric-subtitle">Out of {totalCapacity.toLocaleString()}</span>
          </div>
        </div>

        <div className="metric-card glass-panel">
          <div className="metric-icon warning"><Activity size={24} /></div>
          <div className="metric-info">
            <h3>Overall Density</h3>
            <p className="metric-value">{overallDensity.toFixed(1)}%</p>
            <div className="progress-bar">
              <div 
                className="progress-fill warning" 
                style={{ width: `${overallDensity}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      <div className="dashboard-main">
        <div className="chart-section glass-panel">
          <div className="section-header">
            <BarChart2 size={20} className="section-icon" />
            <h3>Zone Density Analytics</h3>
          </div>
          <div className="chart-container">
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
        </div>

        <div className="ai-section glass-panel">
          <div className="section-header">
            <Zap size={20} className="section-icon glow" />
            <h3>AI Recommendations</h3>
          </div>
          
          <div className="recommendations-list">
            {recommendations.map((rec, i) => (
              <div key={i} className={`rec-card ${rec.priority.toLowerCase()}`}>
                <div className="rec-header">
                  <ShieldAlert size={16} />
                  <span className="priority-badge">{rec.priority} Priority</span>
                </div>
                <h4>{rec.action}</h4>
                <p>{rec.reason}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default OpsDashboard;
