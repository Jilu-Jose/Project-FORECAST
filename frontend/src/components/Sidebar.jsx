import { NavLink, useParams, useNavigate } from 'react-router-dom';
import { UploadCloud, History, LayoutDashboard, FileSearch, LineChart, FileText, Settings, Workflow, ChevronLeft, ChevronRight } from 'lucide-react';

export default function Sidebar({ isCollapsed, toggleCollapse }) {
  const { jobId } = useParams();
  const navigate = useNavigate();

  const handleDisabledClick = (e) => {
    // No longer disabling clicks
  };

  const targetJobId = jobId || '';

  return (
    <aside className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2.5rem', justifyContent: isCollapsed ? 'center' : 'flex-start' }}>
        <div style={{ width: 32, height: 32, background: 'var(--primary)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 'bold', flexShrink: 0 }}>
          F
        </div>
        {!isCollapsed && (
          <div>
            <div style={{ fontFamily: 'Lora', fontWeight: 700, fontSize: '1.2rem', color: 'var(--primary)', lineHeight: 1 }}>FORECAST</div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Audit Suite</div>
          </div>
        )}
      </div>

      <button 
        onClick={toggleCollapse} 
        style={{ 
          background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', 
          position: 'absolute', top: '1.5rem', right: isCollapsed ? '1rem' : '0.5rem',
          display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}
      >
        {isCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
      </button>

      <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', flex: 1 }}>
        <NavLink 
          to="/" 
          className={({isActive}) => `sidebar-link ${isActive && !jobId ? 'active' : ''}`}
          style={navStyle}
        >
          <UploadCloud size={18} /> <span className="nav-text">Upload</span>
        </NavLink>
        
        <NavLink 
          to="/history" 
          className={({isActive}) => `sidebar-link ${isActive ? 'active' : ''}`}
          style={navStyle}
        >
          <History size={18} /> <span className="nav-text">Audit History</span>
        </NavLink>

        <div style={{ margin: '1rem 0', borderTop: '1px solid var(--border-light)', paddingTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <NavLink 
            to={jobId ? `/audit/${targetJobId}` : '#'} 
            end
            className={({isActive}) => `sidebar-link ${isActive && jobId ? 'active' : ''}`}
            style={({ isActive }) => navStyle({ isActive: isActive && jobId, disabled: !jobId })}
          >
            <LayoutDashboard size={18} /> <span className="nav-text">Overview</span>
          </NavLink>
          <NavLink 
            to={jobId ? `/audit/${targetJobId}/findings` : '#'} 
            className={({isActive}) => `sidebar-link ${isActive && jobId ? 'active' : ''}`}
            style={({ isActive }) => navStyle({ isActive: isActive && jobId, disabled: !jobId })}
          >
            <FileSearch size={18} /> <span className="nav-text">Findings</span>
          </NavLink>
          <NavLink 
            to={jobId ? `/audit/${targetJobId}/scenarios` : '#'} 
            className={({isActive}) => `sidebar-link ${isActive && jobId ? 'active' : ''}`}
            style={({ isActive }) => navStyle({ isActive: isActive && jobId, disabled: !jobId })}
          >
            <LineChart size={18} /> <span className="nav-text">Scenarios</span>
          </NavLink>
          <NavLink 
            to={jobId ? `/audit/${targetJobId}/reports` : '#'} 
            className={({isActive}) => `sidebar-link ${isActive && jobId ? 'active' : ''}`}
            style={({ isActive }) => navStyle({ isActive: isActive && jobId, disabled: !jobId })}
          >
            <FileText size={18} /> <span className="nav-text">Reports</span>
          </NavLink>
          <NavLink 
            to={jobId ? `/audit/${targetJobId}/workflow` : '#'} 
            className={({isActive}) => `sidebar-link ${isActive && jobId ? 'active' : ''}`}
            style={({ isActive }) => navStyle({ isActive: isActive && jobId, disabled: !jobId })}
          >
            <Workflow size={18} /> <span className="nav-text">Workflow</span>
          </NavLink>
        </div>
      </nav>

      <div style={{ marginTop: 'auto' }}>
        <NavLink 
          to="#" 
          style={{ ...navStyle({ isActive: false }), color: 'var(--text-muted)' }}
        >
          <Settings size={18} /> <span className="nav-text">Settings</span>
        </NavLink>
        <div style={{ marginTop: '1rem' }}>
          <button className="btn btn-primary" style={{ width: '100%', padding: '0.75rem', overflow: 'hidden' }} onClick={() => navigate('/')}>
            <span className="nav-text" style={{ whiteSpace: 'nowrap' }}>Run New Audit</span>
            {isCollapsed && <UploadCloud size={18} style={{ margin: '0 auto' }} />}
          </button>
        </div>
      </div>
    </aside>
  );
}

const navStyle = ({ isActive, disabled }) => ({
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
  textDecoration: 'none',
  pointerEvents: disabled ? 'none' : 'auto',
  opacity: disabled ? 0.5 : 1
});
