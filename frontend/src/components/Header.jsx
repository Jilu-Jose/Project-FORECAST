import { Search, Headset, BookOpen, CircleHelp, ExternalLink, Mail, GitFork, Keyboard, Play, FileCode, BookMarked, Upload, FileSearch, BarChart3, FileText, ChevronDown } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useState, useRef, useEffect } from 'react';

export default function Header() {
  const navigate = useNavigate();
  const [openDropdown, setOpenDropdown] = useState(null);
  const dropdownRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setOpenDropdown(null);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const toggleDropdown = (name) => {
    setOpenDropdown(prev => prev === name ? null : name);
  };

  return (
    <header className="topbar">
      <div className="search-bar">
        <Search size={16} color="var(--text-muted)" />
        <input type="text" placeholder="Search audits, findings, or refs..." />
      </div>
      
      <div className="top-nav" ref={dropdownRef}>

        {/* ── Support Dropdown ── */}
        <div className="header-dropdown-wrapper">
          <button
            className={`header-dropdown-trigger ${openDropdown === 'support' ? 'active' : ''}`}
            onClick={() => toggleDropdown('support')}
          >
            <Headset size={15} />
            Support
            <ChevronDown size={13} className={`header-chevron ${openDropdown === 'support' ? 'open' : ''}`} />
          </button>
          {openDropdown === 'support' && (
            <div className="header-dropdown-panel">
              <div className="header-dropdown-title">Get Help</div>
              <a href="https://github.com/Jilu-Jose/Project-FORECAST/issues" target="_blank" rel="noopener noreferrer" className="header-dropdown-item">
                <GitFork size={16} />
                <div>
                  <div className="header-dropdown-item-label">Report an Issue</div>
                  <div className="header-dropdown-item-desc">Open a bug report or feature request on GitHub</div>
                </div>
                <ExternalLink size={13} className="header-dropdown-ext" />
              </a>
              <a href="mailto:support@forecast-audit.io" className="header-dropdown-item">
                <Mail size={16} />
                <div>
                  <div className="header-dropdown-item-label">Email Support</div>
                  <div className="header-dropdown-item-desc">support@forecast-audit.io</div>
                </div>
              </a>
              <div className="header-dropdown-divider" />
              <div className="header-dropdown-title">Keyboard Shortcuts</div>
              <div className="header-dropdown-shortcuts">
                <div className="header-shortcut-row">
                  <span>New Audit</span>
                  <span className="header-kbd-group"><kbd>Ctrl</kbd> + <kbd>N</kbd></span>
                </div>
                <div className="header-shortcut-row">
                  <span>Search</span>
                  <span className="header-kbd-group"><kbd>Ctrl</kbd> + <kbd>K</kbd></span>
                </div>
                <div className="header-shortcut-row">
                  <span>Toggle Sidebar</span>
                  <span className="header-kbd-group"><kbd>Ctrl</kbd> + <kbd>B</kbd></span>
                </div>
              </div>
              <div className="header-dropdown-footer">
                FORECAST v1.0 — Built with LangGraph + NVIDIA NIM
              </div>
            </div>
          )}
        </div>

        {/* ── Documentation Dropdown ── */}
        <div className="header-dropdown-wrapper">
          <button
            className={`header-dropdown-trigger ${openDropdown === 'docs' ? 'active' : ''}`}
            onClick={() => toggleDropdown('docs')}
          >
            <BookOpen size={15} />
            Documentation
            <ChevronDown size={13} className={`header-chevron ${openDropdown === 'docs' ? 'open' : ''}`} />
          </button>
          {openDropdown === 'docs' && (
            <div className="header-dropdown-panel">
              <div className="header-dropdown-title">Learn FORECAST</div>
              <a href="https://youtu.be/WkJoQr_kiMo?si=ebXWUhBomfv7rrEs" target="_blank" rel="noopener noreferrer" className="header-dropdown-item header-dropdown-item-highlight">
                <Play size={16} />
                <div>
                  <div className="header-dropdown-item-label">Video Demo</div>
                  <div className="header-dropdown-item-desc">Watch the full walkthrough on YouTube</div>
                </div>
                <ExternalLink size={13} className="header-dropdown-ext" />
              </a>
              <a href="https://github.com/Jilu-Jose/Project-FORECAST" target="_blank" rel="noopener noreferrer" className="header-dropdown-item">
                <BookMarked size={16} />
                <div>
                  <div className="header-dropdown-item-label">README & Architecture</div>
                  <div className="header-dropdown-item-desc">System design, agent pipeline, and setup guide</div>
                </div>
                <ExternalLink size={13} className="header-dropdown-ext" />
              </a>
              <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="header-dropdown-item">
                <FileCode size={16} />
                <div>
                  <div className="header-dropdown-item-label">API Reference</div>
                  <div className="header-dropdown-item-desc">FastAPI interactive docs (Swagger UI)</div>
                </div>
                <ExternalLink size={13} className="header-dropdown-ext" />
              </a>
              <div className="header-dropdown-divider" />
              <div className="header-dropdown-title">Tech Stack</div>
              <div className="header-dropdown-tags">
                <span className="header-tag">Python 3.11+</span>
                <span className="header-tag">FastAPI</span>
                <span className="header-tag">LangGraph</span>
                <span className="header-tag">React 19</span>
                <span className="header-tag">NVIDIA NIM</span>
              </div>
            </div>
          )}
        </div>

        {/* ── Help Center Dropdown ── */}
        <div className="header-dropdown-wrapper">
          <button
            className={`header-dropdown-trigger ${openDropdown === 'help' ? 'active' : ''}`}
            onClick={() => toggleDropdown('help')}
          >
            <CircleHelp size={15} />
            Help Center
            <ChevronDown size={13} className={`header-chevron ${openDropdown === 'help' ? 'open' : ''}`} />
          </button>
          {openDropdown === 'help' && (
            <div className="header-dropdown-panel header-dropdown-panel-wide">
              <div className="header-dropdown-title">Quick Start Guide</div>
              <div className="header-steps">
                <div className="header-step">
                  <div className="header-step-icon"><Upload size={16} /></div>
                  <div>
                    <div className="header-dropdown-item-label">1. Upload Financial Model</div>
                    <div className="header-dropdown-item-desc">Upload an Excel (.xlsx) or CSV file containing your startup's financial projections — revenue, burn rate, cap table, etc.</div>
                  </div>
                </div>
                <div className="header-step">
                  <div className="header-step-icon"><FileSearch size={16} /></div>
                  <div>
                    <div className="header-dropdown-item-label">2. AI Agents Audit</div>
                    <div className="header-dropdown-item-desc">7 specialized agents run sequentially — analyzing structure, assumptions, benchmarks, consistency, scenarios, cap table, and generating the report.</div>
                  </div>
                </div>
                <div className="header-step">
                  <div className="header-step-icon"><BarChart3 size={16} /></div>
                  <div>
                    <div className="header-dropdown-item-label">3. Review Findings</div>
                    <div className="header-dropdown-item-desc">Explore cell-level findings with severity ratings, scenario analyses, and benchmark comparisons across your model.</div>
                  </div>
                </div>
                <div className="header-step">
                  <div className="header-step-icon"><FileText size={16} /></div>
                  <div>
                    <div className="header-dropdown-item-label">4. Export Report</div>
                    <div className="header-dropdown-item-desc">Download the investor-grade audit report as PDF or DOCX, ready to share with stakeholders.</div>
                  </div>
                </div>
              </div>
              <div className="header-dropdown-divider" />
              <div className="header-dropdown-title">FAQ</div>
              <details className="header-faq">
                <summary>What file formats are supported?</summary>
                <p>FORECAST accepts <strong>.xlsx</strong> and <strong>.csv</strong> files. For best results, use Excel files with formulas and multiple sheets.</p>
              </details>
              <details className="header-faq">
                <summary>How long does an audit take?</summary>
                <p>Most audits complete in <strong>under 2 minutes</strong>. Complex models with many sheets may take slightly longer.</p>
              </details>
              <details className="header-faq">
                <summary>What do the severity levels mean?</summary>
                <p><strong>Critical</strong> — material errors that could mislead investors. <strong>Warning</strong> — issues worth flagging. <strong>Info</strong> — observations and best-practice suggestions.</p>
              </details>
            </div>
          )}
        </div>

        <button className="btn btn-outline" onClick={() => navigate('/')}>
          Run New Audit
        </button>
      </div>
    </header>
  );
}

