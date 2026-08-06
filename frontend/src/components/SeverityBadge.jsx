export default function SeverityBadge({ severity }) {
  const labels = {
    critical: '🔴 Critical',
    warning: '🟡 Warning',
    info: '🔵 Info',
  };

  return (
    <span className={`badge badge-${severity}`}>
      {labels[severity] || severity}
    </span>
  );
}

export function VerdictBadge({ verdict }) {
  const labels = {
    realistic: '✅ Realistic',
    aggressive: '⚠️ Aggressive',
    unrealistic: '❌ Unrealistic',
    unknown: '— Unknown',
  };

  return (
    <span className={`badge badge-verdict-${verdict || 'unknown'}`}>
      {labels[verdict] || verdict || 'N/A'}
    </span>
  );
}
