import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Eye, FileText, Download, Send, CheckCircle2, Circle } from 'lucide-react';
import { getAuditReport, getDownloadUrl } from '../api/client';
import Loader from '../components/Loader';

export default function Reports() {
  const { jobId } = useParams();
  const [report, setReport] = useState(null);
  const [format, setFormat] = useState('pdf');

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const data = await getAuditReport(jobId);
        setReport(data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchReport();
  }, [jobId]);

  if (!report) return <Loader message="Generating executive report..." />;

  return (
    <div style={{ display: 'flex', gap: '2rem', height: 'calc(100vh - 120px)' }}>
      {/* Left Pane: Preview */}
      <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: 0, overflow: 'hidden' }}>
        <div style={{ padding: '1rem 1.5rem', borderBottom: '1px solid var(--border-light)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600 }}>
            <Eye size={18} /> Preview
          </div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>100%</div>
        </div>
        
        <div style={{ flex: 1, overflowY: 'auto', padding: '2rem', backgroundColor: '#f0efe8' }}>
          {/* Mock Document Page */}
          <div style={{ 
            background: 'white', 
            width: '100%', 
            maxWidth: '600px', 
            margin: '0 auto',
            padding: '3rem 2.5rem',
            boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
            color: 'var(--text-main)',
            lineHeight: 1.6
          }}>
            <h1 style={{ color: 'var(--primary)', textAlign: 'center', fontSize: '2.2rem', marginBottom: '1rem', lineHeight: 1.2 }}>
              {report.company_name}<br/>Financial Integrity<br/>Assessment
            </h1>
            <p style={{ textAlign: 'center', color: 'var(--text-sidebar)', fontSize: '0.9rem', marginBottom: '2rem' }}>
              Prepared for: Board of Directors<br/>
              Date: {new Date(report.created_at).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric'})}
            </p>
            
            <hr style={{ border: 'none', borderTop: '1px solid var(--border-subtle)', marginBottom: '2rem' }} />

            <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-main)', marginBottom: '1rem' }}>
              <FileText size={20} color="var(--primary)" /> Executive Summary
            </h3>
            
            <div style={{ whiteSpace: 'pre-wrap', fontSize: '0.9rem', color: 'var(--text-sidebar)' }}>
              {report.report_markdown ? report.report_markdown.split('\n').slice(0, 15).join('\n') + '...' : 'Executive summary will be rendered here based on the markdown content.'}
            </div>
            
            <div style={{ 
              marginTop: '1.5rem', 
              paddingLeft: '1rem', 
              borderLeft: '4px solid #dcb77b', 
              fontStyle: 'italic',
              color: 'var(--text-muted)',
              fontSize: '0.9rem'
            }}>
              "While core revenue streams have stabilized, operational inefficiencies in the logic require immediate remediation to prevent potential fiscal leakage."
            </div>
          </div>
        </div>
      </div>

      {/* Right Pane: Controls */}
      <div style={{ width: '300px', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        
        <div className="card">
          <h4 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: '1rem' }}>Export Format</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <div 
              style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.75rem 1rem', background: format === 'pdf' ? 'var(--status-success-bg)' : 'transparent', border: `1px solid ${format === 'pdf' ? 'var(--primary-light)' : 'var(--border-subtle)'}`, borderRadius: 'var(--radius-md)', cursor: 'pointer' }}
              onClick={() => setFormat('pdf')}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: format==='pdf' ? 600 : 400, color: format==='pdf' ? 'var(--status-success-text)' : 'inherit' }}>
                {format === 'pdf' ? <CheckCircle2 size={16} color="var(--primary)" /> : <Circle size={16} color="var(--border-subtle)" />}
                PDF Document
              </div>
              <FileText size={16} color="var(--text-muted)" />
            </div>
            <div 
              style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.75rem 1rem', background: format === 'docx' ? 'var(--status-success-bg)' : 'transparent', border: `1px solid ${format === 'docx' ? 'var(--primary-light)' : 'var(--border-subtle)'}`, borderRadius: 'var(--radius-md)', cursor: 'pointer' }}
              onClick={() => setFormat('docx')}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: format==='docx' ? 600 : 400, color: format==='docx' ? 'var(--status-success-text)' : 'inherit' }}>
                {format === 'docx' ? <CheckCircle2 size={16} color="var(--primary)" /> : <Circle size={16} color="var(--border-subtle)" />}
                DOCX Document
              </div>
              <FileText size={16} color="var(--text-muted)" />
            </div>
          </div>
        </div>

        <div className="card">
          <h4 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: '1rem' }}>Content Options</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
              <CheckCircle2 size={16} color="var(--primary)" style={{ marginTop: '2px', flexShrink: 0 }} />
              <div>
                <div style={{ fontSize: '0.85rem', fontWeight: 500 }}>Include Cover Page</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Adds title, date, and author details.</div>
              </div>
            </div>
            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
              <CheckCircle2 size={16} color="var(--primary)" style={{ marginTop: '2px', flexShrink: 0 }} />
              <div>
                <div style={{ fontSize: '0.85rem', fontWeight: 500 }}>Include Executive Summary</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>The high-level overview section.</div>
              </div>
            </div>
            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
              <Circle size={16} color="var(--border-subtle)" style={{ marginTop: '2px', flexShrink: 0 }} />
              <div>
                <div style={{ fontSize: '0.85rem', fontWeight: 500 }}>Append Raw Data Tables</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Adds an appendix with full ledger data.</div>
              </div>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: 'auto' }}>
          <a href={getDownloadUrl(jobId, format)} target="_blank" rel="noreferrer" className="btn btn-primary" style={{ width: '100%', padding: '0.85rem' }}>
            <Download size={16} /> Download {format.toUpperCase()}
          </a>
          <button className="btn btn-outline" style={{ width: '100%', padding: '0.85rem', color: 'var(--text-main)', borderColor: 'var(--border-subtle)' }}>
            <Send size={16} /> Send via Email
          </button>
        </div>

      </div>
    </div>
  );
}
