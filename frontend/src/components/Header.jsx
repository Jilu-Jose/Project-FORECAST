import { Search, Database, DatabaseZap } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { isDemoMode, setDemoMode } from '../api/client';

export default function Header() {
  const navigate = useNavigate();
  const [demoActive, setDemoActive] = useState(isDemoMode());

  const toggleDemoMode = () => {
    const newState = !demoActive;
    setDemoActive(newState);
    setDemoMode(newState);
    window.location.reload(); // reload to apply to all data views
  };

  return (
    <header className="topbar">
      <div className="search-bar">
        <Search size={16} color="var(--text-muted)" />
        <input type="text" placeholder="Search audits, findings, or refs..." />
      </div>
      
      <div className="top-nav">
        <button 
          onClick={toggleDemoMode}
          className={`btn ${demoActive ? 'btn-primary' : 'btn-outline'}`}
          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 1rem' }}
          title="Toggle Fake Demo Data"
        >
          {demoActive ? <DatabaseZap size={16} /> : <Database size={16} />}
          {demoActive ? 'Demo Data: ON' : 'Demo Data: OFF'}
        </button>
        <a href="#">Support</a>
        <a href="#">Documentation</a>
        <a href="#">Help Center</a>
        <button className="btn btn-outline" onClick={() => navigate('/')}>
          Run New Audit
        </button>
      </div>
    </header>
  );
}
