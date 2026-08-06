import { NavLink, useParams, useNavigate } from 'react-router-dom';
import { UploadCloud, History, LayoutDashboard, FileSearch, LineChart, FileText, Settings } from 'lucide-react';

export default function Sidebar() {
  const { jobId } = useParams();
  const navigate = useNavigate();

  const handleDisabledClick = (e) => {
    // No longer disabling clicks
  };

  const targetJobId = jobId || 'demo';

  return (
    <aside className="sidebar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2.5rem' }}>
        <div style={{ width: 32, height: 32, background: 'var(--primary)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 'bold' }}>
          F
        </div>
        <div>
          <div style={{ fontFamily: 'Lora', fontWeight: 700, fontSize: '1.2rem', color: 'var(--primary)', lineHeight: 1 }}>FORECAST</div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Audit Suite</div>
        </div>
      </div>

      <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', flex: 1 }}>
        <NavLink 
          to="/" 
          className={({isActive}) => `sidebar-link ${isActive && !jobId ? 'active' : ''}`}
          style={navStyle}
        >
          <UploadCloud size={18} /> Upload
        </NavLink>
        
        <NavLink 
          to="/history" 
          className={({isActive}) => `sidebar-link ${isActive ? 'active' : ''}`}
          style={navStyle}
        >
          <History size={18} /> Audit History
        </NavLink>

        <div style={{ margin: '1rem 0', borderTop: '1px solid var(--border-light)', paddingTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <NavLink 
            to={`/audit/${targetJobId}`} 
            end
            className={({isActive}) => `sidebar-link ${isActive && jobId ? 'active' : ''}`}
            style={({ isActive }) => navStyle({ isActive: isActive && jobId })}
          >
            <LayoutDashboard size={18} /> Overview
          </NavLink>
          <NavLink 
            to={`/audit/${targetJobId}/findings`} 
            className={({isActive}) => `sidebar-link ${isActive && jobId ? 'active' : ''}`}
            style={({ isActive }) => navStyle({ isActive: isActive && jobId })}
          >
            <FileSearch size={18} /> Findings
          </NavLink>
          <NavLink 
            to={`/audit/${targetJobId}/scenarios`} 
            className={({isActive}) => `sidebar-link ${isActive && jobId ? 'active' : ''}`}
            style={({ isActive }) => navStyle({ isActive: isActive && jobId })}
          >
            <LineChart size={18} /> Scenarios
          </NavLink>
          <NavLink 
            to={`/audit/${targetJobId}/reports`} 
            className={({isActive}) => `sidebar-link ${isActive && jobId ? 'active' : ''}`}
            style={({ isActive }) => navStyle({ isActive: isActive && jobId })}
          >
            <FileText size={18} /> Reports
          </NavLink>
        </div>
      </nav>

      <div style={{ marginTop: 'auto' }}>
        <NavLink 
          to="#" 
          style={{ ...navStyle({ isActive: false }), color: 'var(--text-muted)' }}
        >
          <Settings size={18} /> Settings
        </NavLink>
        <div style={{ marginTop: '1rem' }}>
          <button className="btn btn-primary" style={{ width: '100%', padding: '0.75rem' }} onClick={() => navigate('/')}>
            Run New Audit
          </button>
        </div>
      </div>
    </aside>
  );
}

const navStyle = ({ isActive }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: '0.75rem',
  padding: '0.6rem 1rem',
  borderRadius: 'var(--radius-sm)',
  fontSize: '0.9rem',
  fontWeight: isActive ? 600 : 500,
  color: isActive ? 'var(--primary)' : 'var(--text-sidebar)',
  backgroundColor: isActive ? 'rgba(78, 131, 98, 0.1)' : 'transparent',
  transition: 'all 0.2s',
  textDecoration: 'none'
});
