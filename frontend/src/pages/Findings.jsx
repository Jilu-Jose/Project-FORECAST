import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getAuditReport } from '../api/client';
import FindingsTable from '../components/FindingsTable';

export default function Findings() {
  const { jobId } = useParams();
  const [report, setReport] = useState(null);
  const [filter, setFilter] = useState('All');

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

  if (!report) return <div style={{ padding: '2rem' }}>Loading findings...</div>;

  const allFindings = [
    ...(report.formula_anomalies || []),
    ...(report.consistency_issues || []).map(i => ({
      ...i,
      issue_type: i.issue_type || 'consistency',
      sheet: i.sheets_involved?.[0] || '',
      cell: i.cells_involved?.[0] || '',
    })),
    ...(report.cap_table_issues || []).map(i => ({
      ...i,
      issue_type: i.issue_type || 'cap_table',
      sheet: 'Cap Table',
      cell: '',
    }))
  ];

  const filtered = filter === 'All' 
    ? allFindings 
    : allFindings.filter(f => (f.severity === filter.toLowerCase() || (filter === 'Critical' && f.severity === 'high')));

  const criticalCount = allFindings.filter(f => f.severity === 'critical' || f.severity === 'high').length;
  const warningCount = allFindings.filter(f => f.severity === 'warning' || f.severity === 'medium').length;

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h2 className="page-title">{report.company_name} Dataset Anomalies</h2>
          <p className="page-subtitle" style={{ maxWidth: '600px' }}>
            Detailed review of {allFindings.length} flagged anomalies requiring immediate reconciliation before quarter close.
          </p>
        </div>
        
        <div style={{ display: 'flex', gap: '1rem' }}>
          <div className="card" style={{ padding: '0.75rem 1.5rem', textAlign: 'center', background: '#f5efea' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-sidebar)' }}>Critical</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--status-critical-text)' }}>{criticalCount}</div>
          </div>
          <div className="card" style={{ padding: '0.75rem 1.5rem', textAlign: 'center', background: '#f2f0e6' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-sidebar)' }}>Warning</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--status-warning-text)' }}>{warningCount}</div>
          </div>
        </div>
      </div>

      <div className="filter-tabs">
        <button className={`filter-btn ${filter === 'All' ? 'active' : ''}`} onClick={() => setFilter('All')}>
          All Severities
        </button>
        <button className={`filter-btn ${filter === 'Critical' ? 'active' : ''}`} onClick={() => setFilter('Critical')}>
          Critical Only
        </button>
        <button className={`filter-btn ${filter === 'Warning' ? 'active' : ''}`} onClick={() => setFilter('Warning')}>
          Warnings Only
        </button>
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden', marginTop: '1rem' }}>
        <div style={{ padding: '1rem 1.5rem', borderBottom: '1px solid var(--border-light)', display: 'flex', justifyContent: 'flex-end', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          Showing {filtered.length} of {allFindings.length}
        </div>
        <FindingsTable findings={filtered} />
      </div>
    </div>
  );
}
