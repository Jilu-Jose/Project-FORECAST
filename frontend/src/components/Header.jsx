import { Search } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Header() {
  const navigate = useNavigate();

  return (
    <header className="topbar">
      <div className="search-bar">
        <Search size={16} color="var(--text-muted)" />
        <input type="text" placeholder="Search audits, findings, or refs..." />
      </div>
      
      <div className="top-nav">
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
