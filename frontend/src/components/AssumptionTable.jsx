import { VerdictBadge } from './SeverityBadge';

export default function AssumptionTable({ assumptions }) {
  if (!assumptions || assumptions.length === 0) {
    return (
      <div className="card animate-in">
        <h3 className="card-title">Assumptions</h3>
        <div className="empty-state">
          <p>No assumptions extracted.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card animate-in">
      <div className="card-header">
        <h3 className="card-title">Assumption Realism</h3>
        <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          {assumptions.length} metrics
        </span>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Metric</th>
              <th>Value</th>
              <th>Unit</th>
              <th>Sheet / Cell</th>
              <th>Verdict</th>
              <th>Benchmark Range</th>
              <th>Source</th>
            </tr>
          </thead>
          <tbody>
            {assumptions.map((a, idx) => (
              <tr key={idx} className="animate-slide" style={{ animationDelay: `${idx * 0.04}s` }}>
                <td style={{ fontWeight: 500, color: 'var(--text-primary)' }}>{a.name}</td>
                <td>{typeof a.value === 'number' ? a.value.toLocaleString() : a.value}</td>
                <td style={{ color: 'var(--text-muted)' }}>{a.unit}</td>
                <td>
                  <span className="cell-ref">{a.sheet}!{a.cell}</span>
                </td>
                <td><VerdictBadge verdict={a.benchmark_verdict} /></td>
                <td style={{ fontSize: '0.85rem' }}>{a.benchmark_range || '—'}</td>
                <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)', maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {a.benchmark_source || '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
