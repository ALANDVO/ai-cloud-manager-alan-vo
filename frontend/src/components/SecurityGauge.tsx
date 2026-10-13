import { ResponsiveContainer, RadialBarChart, RadialBar, Cell } from 'recharts';

interface SecurityGaugeProps {
  score: number;
  riskLevel: string;
  size?: number;
}

const RISK_COLORS: Record<string, string> = {
  low: '#22c55e',
  medium: '#f59e0b',
  high: '#ef4444',
  critical: '#dc2626',
};

export default function SecurityGauge({ score, riskLevel, size = 200 }: SecurityGaugeProps) {
  const color = RISK_COLORS[riskLevel?.toLowerCase()] || '#888';
  const data = [{ value: score, name: 'Score' }];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
      <div style={{ width: size, height: size }}>
        <ResponsiveContainer width="100%" height="100%">
          <RadialBarChart cx="50%" cy="50%" innerRadius="60%" outerRadius="95%" data={data} startAngle={-90} endAngle={90}>
            <RadialBar
              dataKey="value"
              background={{ fill: '#334155' }}
              cornerRadius={6}
            >
              <Cell fill={color} />
            </RadialBar>
          </RadialBarChart>
        </ResponsiveContainer>
      </div>
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: '2.5rem', fontWeight: 700, color: color }}>{score}</div>
        <div style={{ fontSize: '0.875rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          {riskLevel || 'unknown'} risk
        </div>
      </div>
    </div>
  );
}