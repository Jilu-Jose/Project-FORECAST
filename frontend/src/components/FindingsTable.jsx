import { AlertCircle, AlertTriangle, Info, FileSpreadsheet } from 'lucide-react';

export default function FindingsTable({ findings, minimal = false }) {
  if (!findings || findings.length === 0) {
    return <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>No findings to display.</div>;
  }

  const getBadge = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
      case 'high':
        return <span className="badge badge-critical">Critical</span>;
      case 'warning':
      case 'medium':
        return <span className="badge badge-warning">Warning</span>;
      default:
        return <span className="badge badge-info">Info</span>;
    }
  };

  return (
    <div className="table-container">
      <table className="data-table">
        <thead>
          <tr>
            <th style={{ width: '80px' }}>REF ID</th>
            <th>Anomaly Description</th>
            <th style={{ width: '180px' }}>Location</th>
            <th style={{ width: '150px' }}>Category</th>
            <th style={{ width: '100px' }}>Severity</th>
            {!minimal && <th style={{ width: '100px' }}>Value Impact</th>}
          </tr>
        </thead>
        <tbody>
          {findings.map((f, idx) => (
            <tr key={idx}>
              <td style={{ color: 'var(--text-muted)', fontSize: '0.8rem', fontWeight: 500 }}>
                #AF-{String(idx + 1).padStart(3, '0')}
              </td>
              <td>
                <div style={{ fontWeight: 500, color: 'var(--text-main)' }}>
                  {f.issue_type?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </div>
                {!minimal && (
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.25rem', maxWidth: '400px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {f.description || f.reasoning}
                  </div>
                )}
              </td>
              <td>
                <span style={{ 
                  display: 'inline-flex', alignItems: 'center', gap: '0.25rem', 
                  background: 'var(--bg-sidebar)', padding: '0.25rem 0.5rem', 
                  borderRadius: 'var(--radius-sm)', fontSize: '0.8rem'
                }}>
                  <FileSpreadsheet size={14} color="var(--primary)" />
                  {f.sheet}{f.cell ? `!${f.cell}` : ''}
                </span>
              </td>
              <td style={{ color: 'var(--text-sidebar)', fontSize: '0.85rem' }}>
                {f.category || (f.issue_type === 'consistency' ? 'Reconciliation' : 'Logic Error')}
              </td>
              <td>
                {getBadge(f.severity)}
              </td>
              {!minimal && (
                <td style={{ fontWeight: 500 }}>
                  {/* We don't have Value Impact natively, so we show Confidence instead, as stated in plan */}
                  {f.confidence ? `${(f.confidence * 100).toFixed(0)}% Conf` : '—'}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
