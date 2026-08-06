import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { TrendingDown, TrendingUp } from 'lucide-react';
import { getAuditReport } from '../api/client';
import SensitivityChart from '../components/SensitivityChart';
import Loader from '../components/Loader';

export default function Scenarios() {
  const { jobId } = useParams();
  const [report, setReport] = useState(null);

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

  if (!report) return <Loader message="Running scenario sensitivities..." />;

  const scenarios = report.scenario_results || [];
  
  // Find biggest impact for the hero card
  let biggestImpact = null;
  let maxDelta = 0;
  
  scenarios.forEach(s => {
    if (Math.abs(s.delta_pct) > maxDelta) {
      maxDelta = Math.abs(s.delta_pct);
      biggestImpact = s;
    }
  });

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">Sensitivity Analysis</h2>
        <p className="page-subtitle">Impact of ±20% operational perturbations on key metrics.</p>
      </div>

      <div className="card" style={{ marginBottom: '2rem', display: 'flex', gap: '2rem', alignItems: 'center' }}>
        <div style={{ flex: 1 }}>
          <h3 className="section-title" style={{ margin: 0, color: 'var(--text-main)' }}>Key Impact Summary</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.5rem', lineHeight: 1.6 }}>
            The financial model is highly sensitive to changes in {biggestImpact ? <strong>{biggestImpact.input_metric}</strong> : 'key metrics'}. 
            A ±20% variance drives severe downstream effects.
          </p>
        </div>
        
        {biggestImpact && (
          <div style={{ 
            background: 'var(--status-critical-bg)', 
            padding: '1.5rem 2rem', 
            borderRadius: 'var(--radius-lg)',
            minWidth: '220px'
          }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--status-critical-text)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              {biggestImpact.output_metric} Shift
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginTop: '0.5rem' }}>
              <div style={{ fontSize: '2.5rem', fontWeight: 700, color: 'var(--status-critical-text)', fontFamily: 'Lora', lineHeight: 1 }}>
                {biggestImpact.delta_pct > 0 ? '+' : ''}{(biggestImpact.delta_pct * 100).toFixed(1)}%
              </div>
              <div style={{ background: '#fecaca', padding: '0.5rem', borderRadius: '50%', color: 'var(--status-critical-text)' }}>
                {biggestImpact.delta_pct < 0 ? <TrendingDown size={20} /> : <TrendingUp size={20} />}
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="card-grid-3" style={{ gridTemplateColumns: 'repeat(2, 1fr)' }}>
        {scenarios.slice(0, 4).map((s, idx) => (
          <div key={idx} className="card" style={{ border: '1px solid var(--border-light)', boxShadow: 'none' }}>
            <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--primary)', marginBottom: '1rem', fontSize: '0.95rem' }}>
              {s.input_metric} (±20%)
            </h4>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '0.75rem', borderBottom: '1px solid var(--border-light)', marginBottom: '0.75rem' }}>
              <div>
                <div style={{ fontWeight: 500, fontSize: '0.9rem' }}>{s.output_metric}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Baseline: {s.baseline_value}</div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontWeight: 600, color: s.delta_pct < 0 ? 'var(--status-critical-text)' : 'var(--status-success-text)' }}>
                  {s.perturbed_value}
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  {s.delta_pct > 0 ? '+' : ''}{(s.delta_pct * 100).toFixed(1)}%
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="card" style={{ marginTop: '2rem' }}>
        <h3 className="section-title">Tornado Chart (Delta %)</h3>
        <div style={{ marginTop: '1.5rem' }}>
          <SensitivityChart scenarioResults={scenarios} />
        </div>
      </div>
    </div>
  );
}
