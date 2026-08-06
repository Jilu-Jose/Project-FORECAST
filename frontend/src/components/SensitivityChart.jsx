import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from 'recharts';

export default function SensitivityChart({ scenarioResults }) {
  if (!scenarioResults || scenarioResults.length === 0) {
    return (
      <div className="card animate-in">
        <h3 className="card-title">Sensitivity Analysis</h3>
        <div className="empty-state">
          <p>No scenario results available.</p>
        </div>
      </div>
    );
  }

  // Build tornado chart data — group by assumption, show ±20% impact
  const assumptionMap = {};
  scenarioResults.forEach(r => {
    const key = r.assumption_perturbed;
    if (!assumptionMap[key]) {
      assumptionMap[key] = { name: key };
    }
    if (r.perturbation === '+20%') {
      assumptionMap[key].positive = r.delta_pct;
    } else if (r.perturbation === '-20%') {
      assumptionMap[key].negative = r.delta_pct;
    }
  });

  const chartData = Object.values(assumptionMap)
    .filter(d => d.positive != null || d.negative != null)
    .sort((a, b) => {
      const aSpread = Math.abs(a.positive || 0) + Math.abs(a.negative || 0);
      const bSpread = Math.abs(b.positive || 0) + Math.abs(b.negative || 0);
      return bSpread - aSpread;
    })
    .slice(0, 10);

  if (chartData.length === 0) {
    // Show all scenario results as a simple bar chart instead
    const simpleData = scenarioResults.slice(0, 15).map(r => ({
      name: `${r.assumption_perturbed} (${r.perturbation})`,
      delta: r.delta_pct,
    }));

    return (
      <div className="card animate-in">
        <div className="card-header">
          <h3 className="card-title">Sensitivity Analysis</h3>
        </div>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={simpleData} layout="vertical" margin={{ left: 120, right: 30 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis type="number" tick={{ fill: '#6b6b90', fontSize: 12 }} />
              <YAxis
                type="category"
                dataKey="name"
                tick={{ fill: '#a0a0c0', fontSize: 11 }}
                width={110}
              />
              <Tooltip
                contentStyle={{
                  background: 'rgba(26, 26, 62, 0.95)',
                  border: '1px solid rgba(255,255,255,0.08)',
                  borderRadius: '8px',
                  color: '#f0f0f8',
                }}
                formatter={(val) => [`${val > 0 ? '+' : ''}${val.toFixed(1)}%`, 'Impact']}
              />
              <Bar dataKey="delta" radius={[0, 4, 4, 0]}>
                {simpleData.map((entry, index) => (
                  <Cell
                    key={index}
                    fill={entry.delta >= 0 ? '#10b981' : '#ef4444'}
                    opacity={0.8}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  }

  return (
    <div className="card animate-in">
      <div className="card-header">
        <h3 className="card-title">Sensitivity Tornado Chart</h3>
        <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
          Impact of ±20% perturbation on key metrics
        </span>
      </div>
      <div className="chart-container">
        <ResponsiveContainer width="100%" height={Math.max(300, chartData.length * 50)}>
          <BarChart data={chartData} layout="vertical" margin={{ left: 120, right: 30 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
            <XAxis
              type="number"
              tick={{ fill: '#6b6b90', fontSize: 12 }}
              tickFormatter={(v) => `${v > 0 ? '+' : ''}${v}%`}
            />
            <YAxis
              type="category"
              dataKey="name"
              tick={{ fill: '#a0a0c0', fontSize: 11 }}
              width={110}
            />
            <Tooltip
              contentStyle={{
                background: 'rgba(26, 26, 62, 0.95)',
                border: '1px solid rgba(255,255,255,0.08)',
                borderRadius: '8px',
                color: '#f0f0f8',
              }}
              formatter={(val, name) => {
                const label = name === 'positive' ? '+20% impact' : '-20% impact';
                return [`${val > 0 ? '+' : ''}${val.toFixed(1)}%`, label];
              }}
            />
            <ReferenceLine x={0} stroke="rgba(255,255,255,0.15)" />
            <Bar dataKey="negative" fill="#ef4444" opacity={0.8} radius={[4, 0, 0, 4]} name="negative" />
            <Bar dataKey="positive" fill="#10b981" opacity={0.8} radius={[0, 4, 4, 0]} name="positive" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
