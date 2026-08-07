import { useState, useEffect } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Menu } from 'lucide-react';
import Sidebar from './Sidebar';
import Header from './Header';

export default function Layout() {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();

  // Close mobile sidebar on navigation
  useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname]);

  // Close mobile sidebar on resize to desktop
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth > 768) {
        setMobileOpen(false);
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div className={`app-container ${isCollapsed ? 'sidebar-collapsed' : ''} ${mobileOpen ? 'mobile-sidebar-open' : ''}`}>
      {/* Mobile hamburger */}
      <button
        className="mobile-hamburger"
        onClick={() => setMobileOpen(true)}
        aria-label="Open navigation"
      >
        <Menu size={22} />
      </button>

      {/* Overlay for mobile */}
      {mobileOpen && (
        <div
          className="mobile-overlay"
          onClick={() => setMobileOpen(false)}
        />
      )}

      <Sidebar
        isCollapsed={isCollapsed}
        toggleCollapse={() => setIsCollapsed(!isCollapsed)}
        mobileOpen={mobileOpen}
        closeMobile={() => setMobileOpen(false)}
      />
      <main className="main-content">
        <Header onHamburgerClick={() => setMobileOpen(true)} />
        <Outlet />
      </main>
    </div>
  );
}
