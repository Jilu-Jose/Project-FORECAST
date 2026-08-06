import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { AlertCircle, AlertTriangle, Info, TrendingUp, Workflow, CheckCircle2, Loader2 } from 'lucide-react';
import { getAuditStatus, getAuditReport } from '../api/client';
import FindingsTable from '../components/FindingsTable';

export default function Overview() {
  const { jobId } = useParams();
  const [status, setStatus] = useState(null);
  const [report, setReport] = useState(null);

  useEffect(() => {
    let interval;
    const poll = async () => {
      try {
        const data = await getAuditStatus(jobId);
        setStatus(data);
        if (data.status === 'complete') {
          clearInterval(interval);
          const reportData = await getAuditReport(jobId);
          setReport(reportData);
        }
      } catch (err) {
        clearInterval(interval);
      }
    };
    poll();
    interval = setInterval(poll, 2000);
    return () => clearInterval(interval);
  }, [jobId]);

  if (!status || status.status !== 'complete' || !report) {
    return <div style={{ padding: '2rem' }}>Processing Audit...</div>;
  }

  const summary = report.summary || {};
  const totalIssues = (summary.critical_count || 0) + (summary.warning_count || 0) + (summary.info_count || 0);
  // Fake health score logic, just for the visual of the circular ring
  const healthScore = Math.max(0, 100 - (summary.critical_count * 5) - (summary.warning_count * 2));

  // Combine top findings
  const criticalFindings = [
    ...(report.formula_anomalies || []),
    ...(report.consistency_issues || []).map(i => ({
      ...i,
      issue_type: i.issue_type || 'consistency',
      sheet: i.sheets_involved?.[0] || '',
      cell: i.cells_involved?.[0] || '',
    }))
  ].filter(f => f.severity === 'critical' || f.severity === 'high').slice(0, 2);

  const warningFindings = [
    ...(report.formula_anomalies || []),
    ...(report.consistency_issues || []).map(i => ({
      ...i,
      issue_type: i.issue_type || 'consistency',
      sheet: i.sheets_involved?.[0] || '',
      cell: i.cells_involved?.[0] || '',
    }))
  ].filter(f => f.severity === 'warning' || f.severity === 'medium').slice(0, 2);

  const topFindings = [...criticalFindings, ...warningFindings];

  return (
    <div>
      <div className="card-grid-3">
        {/* Model Health */}
        <div className="card health-ring-container">
          <h3 className="section-title" style={{ alignSelf: 'flex-start' }}>Model Health</h3>
          <div style={{ position: 'relative', width: 140, height: 140, margin: '1rem 0' }}>
            <svg viewBox="0 0 36 36" style={{ width: '100%', height: '100%', transform: 'rotate(-90deg)' }}>
              <path
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none" stroke="#e6ede8" strokeWidth="4"
              />
              <path
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none" stroke="var(--primary)" strokeWidth="4"
                strokeDasharray={`${healthScore}, 100`}
              />
            </svg>
            <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
              <div style={{ fontSize: '2rem', fontWeight: 700, fontFamily: 'Lora', lineHeight: 1 }}>{healthScore}</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>/ 100</div>
            </div>
          </div>
          <p style={{ textAlign: 'center', fontSize: '0.85rem', color: 'var(--text-sidebar)' }}>
            Health score is {healthScore > 80 ? 'strong' : healthScore > 60 ? 'stable' : 'at risk'}, but requires attention on {summary.critical_count} critical assumptions.
          </p>
        </div>

        {/* Findings Summary */}
        <div className="card">
          <h3 className="section-title">Findings Summary</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '1.5rem' }}>
            <div className="summary-item" style={{ background: 'var(--status-critical-bg)', color: 'var(--status-critical-text)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 500 }}>
                <AlertTriangle size={18} /> Critical
              </div>
              <div style={{ fontWeight: 700, fontSize: '1.2rem' }}>{summary.critical_count || 0}</div>
            </div>
            <div className="summary-item" style={{ background: 'var(--status-warning-bg)', color: 'var(--status-warning-text)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 500 }}>
                <AlertCircle size={18} /> Warning
              </div>
              <div style={{ fontWeight: 700, fontSize: '1.2rem' }}>{summary.warning_count || 0}</div>
            </div>
            <div className="summary-item" style={{ background: 'var(--status-info-bg)', color: 'var(--status-info-text)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 500 }}>
                <Info size={18} /> Info
              </div>
              <div style={{ fontWeight: 700, fontSize: '1.2rem' }}>{summary.info_count || 0}</div>
            </div>
          </div>
        </div>

        {/* External Workflow (n8n) */}
        {status?.n8n_status && status.n8n_status !== 'pending' && (
          <div className="card">
            <h3 className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Workflow size={18} /> External Workflow (n8n)
            </h3>
            <div style={{ 
              marginTop: '1rem', 
              padding: '1rem', 
              borderRadius: 'var(--radius-md)', 
              backgroundColor: 'var(--background-body)',
              border: '1px solid var(--border-light)',
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem'
            }}>
              {status.n8n_status === 'Workflow Complete' ? (
                <CheckCircle2 size={20} color="var(--status-info-text)" />
              ) : (
                <Loader2 size={20} color="var(--primary)" className="spin" />
              )}
              <div>
                <div style={{ fontWeight: 600, fontSize: '0.95rem' }}>Status</div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-sidebar)' }}>{status.n8n_status}</div>
              </div>
            </div>
          </div>
        )}

        {/* Assumption Benchmarks */}
        <div className="card">
          <h3 className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <TrendingUp size={18} /> Assumption Benchmarks
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>
            {(report.assumptions || []).slice(0, 3).map((assump, idx) => {
              // Parse value to compare with benchmark conceptually (just UI logic for bars)
              const val = parseFloat(String(assump.value).replace(/[^0-9.-]+/g,""));
              const rangeStr = assump.benchmark_range || "";
              const limits = rangeStr.match(/[0-9.]+/g);
              let benchmarkCenter = val;
              if (limits && limits.length >= 2) {
                benchmarkCenter = (parseFloat(limits[0]) + parseFloat(limits[1])) / 2;
              } else if (limits && limits.length === 1) {
                benchmarkCenter = parseFloat(limits[0]);
              }
              const isAggressive = val > benchmarkCenter;

              return (
                <div key={idx} style={{ marginBottom: '0.5rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', fontWeight: 500, marginBottom: '0.25rem' }}>
                    <span>{assump.metric}</span>
                    <span style={{ color: isAggressive ? 'var(--status-warning-text)' : 'var(--text-main)' }}>
                      {assump.value} {assump.unit} vs {assump.benchmark_range}
                    </span>
                  </div>
                  <div style={{ height: '4px', background: '#e2e8f0', borderRadius: '2px', position: 'relative' }}>
                    <div style={{ 
                      position: 'absolute', top: 0, left: 0, height: '100%', borderRadius: '2px',
                      width: isAggressive ? '80%' : '50%', 
                      background: isAggressive ? 'var(--status-warning-text)' : 'var(--primary)' 
                    }} />
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                    {isAggressive ? 'Aggressive compared to peers.' : 'Within healthy limits.'}
                  </div>
                </div>
              );
            })}
            {(!report.assumptions || report.assumptions.length === 0) && (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No key assumptions extracted to benchmark.</p>
            )}
          </div>
        </div>
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-light)' }}>
          <h3 className="section-title" style={{ margin: 0 }}>Critical & Warning Findings</h3>
        </div>
        <FindingsTable findings={topFindings} minimal />
      </div>
    </div>
  );
}
