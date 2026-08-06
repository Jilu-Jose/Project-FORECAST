import { Check } from 'lucide-react';

const AGENTS = [
  { key: 'ingestion', label: 'Ingest' },
  { key: 'structural', label: 'Structure' },
  { key: 'assumption', label: 'Assumptions' },
  { key: 'benchmark', label: 'Benchmark' },
  { key: 'consistency', label: 'Consistency' },
  { key: 'scenario', label: 'Scenarios' },
  { key: 'captable', label: 'Cap Table' },
  { key: 'report', label: 'Report' },
];

export default function AuditProgress({ currentAgent, status }) {
  const currentIdx = AGENTS.findIndex(a => a.key === currentAgent);

  return (
    <div className="progress-stepper">
      {AGENTS.map((agent, idx) => {
        let stepClass = '';
        if (status === 'complete') {
          stepClass = 'complete';
        } else if (idx < currentIdx) {
          stepClass = 'complete';
        } else if (idx === currentIdx) {
          stepClass = 'active';
        }

        return (
          <div key={agent.key} className={`progress-step ${stepClass}`}>
            <div className="step-dot">
              {stepClass === 'complete' ? <Check size={14} /> : idx + 1}
            </div>
            <span className="step-label">{agent.label}</span>
          </div>
        );
      })}
    </div>
  );
}
