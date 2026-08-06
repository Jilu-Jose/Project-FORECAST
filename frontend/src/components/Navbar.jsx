import { NavLink } from 'react-router-dom';
import { Upload, History, BarChart3 } from 'lucide-react';

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <div className="logo-icon">F</div>
        <div>
          <h1>FORECAST</h1>
        </div>
        <span className="brand-tag">Agentic Auditor</span>
      </div>

      <div className="navbar-links">
        <NavLink to="/" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} end>
          <Upload size={16} /> New Audit
        </NavLink>
        <NavLink to="/history" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <History size={16} /> History
        </NavLink>
      </div>
    </nav>
  );
}
