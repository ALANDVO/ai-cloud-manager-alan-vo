import { useState, useEffect, useCallback } from 'react'
import { api } from '../api/client'
import CostChart from '../components/CostChart'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

const PROV_COLORS: Record<string, string> = { aws: '#f59e0b', gcp: '#4285f4', azure: '#0078d4' }

export default function CostDashboard() {
  const [summary, setSummary] = useState<any>(null)
  const [trends, setTrends] = useState<any[]>([])
  const [breakdown, setBreakdown] = useState<any[]>([])
  const [anomalies, setAnomalies] = useState<any[]>([])
  const [provider, setProvider] = useState('')
  const [days, setDays] = useState(30)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    setLoading(true); setError('')
    try {
      const params = new URLSearchParams()
      if (provider) params.set('provider', provider)
      params.set('days', String(days))
      const [s, t, b, a] = await Promise.all([
        api.costSummary(),
        api.costTrends(params.toString()),
        api.costBreakdown(provider ? `provider=${provider}` : ''),
        api.costAnomalies(),
      ])
      setSummary(s); setTrends(t); setBreakdown(b); setAnomalies(a)
    } catch (e: any) { setError(e.message) }
    finally { setLoading(false) }
  }, [provider, days])

  useEffect(() => { load() }, [load])

  const provData = summary ? Object.entries(summary.by_provider || {}).map(([k, v]) => ({ name: k, value: v })) : []
  const svcData = breakdown.slice(0, 8).map((b: any) => ({ name: b.service, value: b.monthly_cost }))

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Cost Dashboard</h2>
        <div className="filter-bar">
          <select value={provider} onChange={e => setProvider(e.target.value)}>
            <option value="">All Providers</option>
            <option value="aws">AWS</option>
            <option value="gcp">GCP</option>
            <option value="azure">Azure</option>
          </select>
          <select value={days} onChange={e => setDays(Number(e.target.value))}>
            <option value={7}>7 days</option>
            <option value={30}>30 days</option>
            <option value={90}>90 days</option>
          </select>
          <button className="btn-secondary" onClick={load}>Apply</button>
        </div>
      </div>
      {error && <div className="alert alert-error">{error}</div>}
      {loading ? <div className="loading">Loading…</div> : summary && (
        <>
          <div className="stats-grid">
            <div className="stat-card"><span className="stat-label">Monthly Total</span><span className="stat-value">${summary.total_monthly.toLocaleString()}</span></div>
            <div className="stat-card"><span className="stat-label">MoM Change</span><span className="stat-value">{summary.month_over_month_change}%</span></div>
            <div className="stat-card"><span className="stat-label">Forecast</span><span className="stat-value">${summary.forecast_next_month.toLocaleString()}</span></div>
            <div className="stat-card"><span className="stat-label">Savings Available</span><span className="stat-value savings">${summary.savings_available.toLocaleString()}</span></div>
          </div>
          <div className="charts-row">
            <div className="chart-box">
              <h3>Cost Trends</h3>
              <CostChart data={trends} />
            </div>
            <div className="chart-box">
              <h3>By Provider</h3>
              <ResponsiveContainer width="100%" height={220}>
                <PieChart><Pie data={provData} dataKey="value" label>{provData.map((d: any) => <Cell key={d.name} fill={PROV_COLORS[d.name] || '#6b7280'} />)}</Pie><Tooltip /></PieChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="charts-row">
            <div className="chart-box">
              <h3>Top Services</h3>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={svcData}><XAxis dataKey="name" /><YAxis /><Tooltip /><Bar dataKey="value" fill="#3b82f6" /></BarChart>
              </ResponsiveContainer>
            </div>
            <div className="chart-box">
              <h3>Cost Anomalies</h3>
              {anomalies.length === 0 ? <div className="empty">No anomalies detected</div> : (
                <div className="anomaly-list">
                  {anomalies.slice(0, 5).map((a: any) => (
                    <div key={a.id} className="anomaly-item">
                      <span className={`badge badge-${a.severity}`}>{a.severity}</span>
                      <span>{a.description}</span>
                      <span className="anomaly-amount">+${(a.actual_cost - a.expected_cost).toFixed(0)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
          <div className="table-section">
            <h3>Cost Breakdown</h3>
            <table className="data-table">
              <thead><tr><th>Provider</th><th>Service</th><th>Type</th><th>Monthly</th><th>Daily</th><th>%</th></tr></thead>
              <tbody>
                {breakdown.map((b: any) => (
                  <tr key={b.provider + b.service}>
                    <td><span className={`provider-dot provider-${b.provider}`}></span>{b.provider}</td>
                    <td>{b.service}</td><td>{b.resource_type}</td>
                    <td className="mono">${b.monthly_cost.toLocaleString()}</td>
                    <td className="mono">${b.daily_cost.toLocaleString()}</td>
                    <td>{b.percent_of_total}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  )
}
