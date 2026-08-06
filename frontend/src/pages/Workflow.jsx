import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Workflow as WorkflowIcon, CheckCircle2, Loader2 } from 'lucide-react';
import { getAuditStatus } from '../api/client';

export default function Workflow() {
  const { jobId } = useParams();
  const [status, setStatus] = useState(null);

  useEffect(() => {
    let interval;
    const poll = async () => {
      try {
        const data = await getAuditStatus(jobId);
        setStatus(data);
      } catch (err) {
        // handle error silently
      }
    };
    poll();
    interval = setInterval(poll, 2000);
    return () => clearInterval(interval);
  }, [jobId]);

  if (!status) {
    return <div style={{ padding: '2rem' }}>Loading workflow status...</div>;
  }

  return (
    <div style={{ padding: '0 1rem' }}>
      <div className="card">
        <h2 className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '1.25rem', marginBottom: '1.5rem' }}>
          <WorkflowIcon size={24} /> n8n Workflow Status
        </h2>
        
        <div style={{ 
          padding: '2rem', 
          borderRadius: 'var(--radius-lg)', 
          backgroundColor: 'var(--background-body)',
          border: '1px solid var(--border-light)',
          display: 'flex',
          alignItems: 'center',
          gap: '1rem',
          boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.02)'
        }}>
          {status.n8n_status === 'Workflow Complete' ? (
            <CheckCircle2 size={32} color="var(--status-info-text)" />
          ) : (
            <Loader2 size={32} color="var(--primary)" className="spin" />
          )}
          <div>
            <div style={{ fontWeight: 600, fontSize: '1.1rem', color: 'var(--text-main)' }}>Current Stage</div>
            <div style={{ fontSize: '1rem', color: 'var(--text-sidebar)', marginTop: '0.25rem' }}>
              {status.n8n_status || 'Pending initialization...'}
            </div>
          </div>
        </div>
        
        <div style={{ marginTop: '2.5rem' }}>
          <h3 className="section-title" style={{ fontSize: '1rem', marginBottom: '1rem' }}>Audit Job Context</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <div className="summary-item" style={{ background: '#f8fafc', border: '1px solid #e2e8f0', color: 'var(--text-main)' }}>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Overall Status</div>
              <div style={{ fontWeight: 600, textTransform: 'capitalize' }}>{status.status}</div>
            </div>
            <div className="summary-item" style={{ background: '#f8fafc', border: '1px solid #e2e8f0', color: 'var(--text-main)' }}>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Active Agent</div>
              <div style={{ fontWeight: 600, textTransform: 'capitalize' }}>{status.current_agent || 'None'}</div>
            </div>
            <div className="summary-item" style={{ background: '#f8fafc', border: '1px solid #e2e8f0', color: 'var(--text-main)' }}>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Progress</div>
              <div style={{ fontWeight: 600 }}>{status.progress_pct}%</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
