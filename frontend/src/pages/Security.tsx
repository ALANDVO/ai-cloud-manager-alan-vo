import React, { useState, useEffect, useCallback } from 'react'
import { api } from '../api/client'
import SecurityGauge from '../components/SecurityGauge'

export default function SecurityPage() {
  const [audit, setAudit] = useState<any>(null)
  const [compliance, setCompliance] = useState<any[]>([])
  const [posture, setPosture] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [assessing, setAssessing] = useState(false)

  const load = useCallback(async () => {
    setLoading(true); setError('')
    try {
      const [a, c, p] = await Promise.all([api.securityAudit(), api.compliance(), api.posture()])
      setAudit(a); setCompliance(c); setPosture(p)
    } catch (e: any) { setError(e.message) }
    finally { setLoading(false) }
  }, [])

  const assess = useCallback(async () => {
    setAssessing(true)
    try {
      const p = await api.posture()
      setPosture(p)
    } catch (e: any) { setError(e.message) }
    finally { setAssessing(false) }
  }, [])

  useEffect(() => { load() }, [load])

  const riskColor = (level: string) => level === 'low' ? 'var(--low)' : level === 'medium' ? 'var(--medium)' : level === 'high' ? 'var(--high)' : 'var(--critical)'

  return (
    <div className="security-page">
      <div className="dashboard-header">
        <h2>Security Posture</h2>
        <button className="btn-primary" onClick={assess} disabled={assessing}>
          {assessing ? 'Assessing…' : 'Run AI Assessment'}
        </button>
      </div>
      {error && <div className="alert alert-error">{error}</div>}
      {loading ? <div className="loading">Loading…</div> : (
        <>
          <div className="posture-grid">
            <div className="chart-box">
              <h3>Overall Score</h3>
              <SecurityGauge score={posture?.overall_score || 0} riskLevel={posture?.risk_level || 'unknown'} />
            </div>
            <div className="audit-summary">
              <div className="stat-card"><span className="stat-label">Total Checks</span><span className="stat-value">{audit?.total_checks || 0}</span></div>
              <div className="stat-card"><span className="stat-label">Passed</span><span className="stat-value" style={{ color: 'var(--low)' }}>{audit?.passed || 0}</span></div>
              <div className="stat-card"><span className="stat-label">Warnings</span><span className="stat-value" style={{ color: 'var(--medium)' }}>{audit?.warnings || 0}</span></div>
              <div className="stat-card"><span className="stat-label">Critical</span><span className="stat-value" style={{ color: 'var(--critical)' }}>{audit?.critical || 0}</span></div>
            </div>
          </div>

          {posture?.summary && (
            <div className="llm-box">
              <h4>AI Assessment</h4>
              <p>{posture.summary}</p>
            </div>
          )}

          {posture?.top_risks && (
            <div className="table-section">
              <h3>Top Risks</h3>
              <table className="data-table">
                <thead><tr><th>Risk</th><th>Impact</th><th>Likelihood</th><th>Mitigation</th></tr></thead>
                <tbody>
                  {posture.top_risks.map((r: any, i: number) => (
                    <tr key={i}>
                      <td>{r.risk}</td><td><span className={`badge badge-${r.impact}`}>{r.impact}</span></td>
                      <td><span className={`badge badge-${r.likelihood}`}>{r.likelihood}</span></td>
                      <td>{r.mitigation}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div className="compliance-grid">
            {compliance.map((c: any) => (
              <div key={c.framework} className="score-card">
                <div className="score-header">
                  <span className="score-asset">{c.framework}</span>
                  <span className={`badge ${c.status === 'compliant' ? 'badge-low' : c.status === 'partial' ? 'badge-medium' : 'badge-critical'}`}>{c.status}</span>
                </div>
                <div className="score-bar">
                  <div className="score-fill" style={{ width: `${c.score}%`, background: riskColor(c.status === 'compliant' ? 'low' : c.status === 'partial' ? 'medium' : 'high') }} />
                </div>
                <span className="score-value">{c.score}/{c.max_score}</span>
                <div className="score-factors">
                  {c.categories.map((cat: any) => (
                    <span key={cat.name} className="factor-tag">{cat.name}: {cat.score}%</span>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="table-section">
            <h3>Audit Findings</h3>
            <table className="data-table">
              <thead><tr><th>Provider</th><th>Resource</th><th>Check</th><th>Severity</th><th>Status</th></tr></thead>
              <tbody>
                {audit?.findings?.map((f: any) => (
                  <tr key={f.id} className={f.status === 'critical' ? 'row-critical' : ''}>
                    <td><span className={`provider-dot provider-${f.provider}`}></span>{f.provider}</td>
                    <td className="mono">{f.resource_id}</td>
                    <td>{f.check}</td>
                    <td><span className={`badge badge-${f.severity}`}>{f.severity}</span></td>
                    <td><span className={`badge ${f.status === 'pass' ? 'badge-low' : f.status === 'critical' ? 'badge-critical' : 'badge-medium'}`}>{f.status}</span></td>
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
