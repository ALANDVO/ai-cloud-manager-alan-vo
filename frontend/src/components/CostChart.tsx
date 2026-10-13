import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

interface CostChartProps {
  data: Array<{ date: string; cost: number; provider: string }>;
  title?: string;
}

const COLORS: Record<string, string> = { aws: '#f59e0b', gcp: '#4285f4', azure: '#0078d4' };

export default function CostChart({ data, title = 'Cost Trends' }: CostChartProps) {
  if (!data?.length) {
    return (
      <div className="chart-card">
        <h3>{title}</h3>
        <div className="chart-container" style={{display: 'flex', alignItems: 'center', justifyContent: 'center', height: '300px'}}>
          <div className="empty-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
              <path d="M18 20V10M12 20V4M6 20v-6" />
              <path d="M2 20h20" />
            </svg>
            <h3>No cost trend data</h3>
            <p>Configure cloud provider credentials to see cost trends</p>
          </div>
        </div>
      </div>
    );
  }

  const providers = [...new Set(data.map(d => d.provider))];
  const dates = [...new Set(data.map(d => d.date))].sort();
  const series = providers.map(provider => ({
    name: provider.toUpperCase(),
    data: dates.map(date => {
      const point = data.find(d => d.date === date && d.provider === provider);
      return { date, cost: point?.cost || 0 };
    }),
    color: COLORS[provider] || '#888',
  }));

  return (
    <div className="chart-card">
      <h3>{title}</h3>
      <div className="chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={series[0]?.data || []} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} tick={{ fill: '#94a3b8' }} />
            <YAxis stroke="#94a3b8" fontSize={12} tick={{ fill: '#94a3b8' }} tickFormatter={(v) => `$${v/1000}k`} />
            <Tooltip
              contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
              labelStyle={{ color: '#f1f5f9' }}
              formatter={(value: number) => [`$${value.toFixed(2)}`, 'Cost']}
            />
            <Legend />
            {series.map((s) => (
              <Line
                key={s.name}
                type="monotone"
                dataKey="cost"
                stroke={s.color}
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 6 }}
                name={s.name}
                data={s.data}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}