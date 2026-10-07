import React, { useState, useEffect, useCallback } from 'react'
import { api } from '../api/client'
import ResourceTable from '../components/ResourceTable'

export default function Resources() {
  const [resources, setResources] = useState<any[]>([])
  const [util, setUtil] = useState<any>(null)
  const [policies, setPolicies] = useState<any[]>([])
  const [predictions, setPredictions] = useState<any[]>([])
  const [workloads, setWorkloads] = useState<any[]>([])
  const [provider, setProvider] = useState('')
  const [rtype, setRtype] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    setLoading(true); setError('')
    try {
      const params = new URLSearchParams()
      if (provider) params.set('provider', provider)
      if (rtype) params.set('resource_type', rtype)
      const [r, u, p, pr, w] = await Promise.all([
        api.resources(params.toString()),
        api.utilization(),
        api.scalingPolicies(),
        api.scalingPredictions(),
        api.workloads(),
      ])
      setResources(r); setUtil(u); setPolicies(p); setPredictions(pr); setWorkloads(w)
    } catch (e: any) { setError(e.message) }
    finally { setLoading(false) }
  }, [provider, rtype])

  useEffect(() => { load() }, [load])

  return (
    <div className="resources-page">
      <div className="dashboard-header">
        <h2>Cloud Resources</h2>
        <div className="filter-bar">
          <select value={provider} onChange={e => setProvider(e.target.value)}>
            <option value="">All Providers</option>
            <option value="aws">AWS</option>
            <option value="gcp">GCP</option>
            <option value="azure">Azure</option>
          </select>
          <select value={rtype} onChange={e => setRtype(e.target.value)}>
            <option value="">All Types</option>
            <option value="ec2_instance">EC2</option>
            <option value="gce_instance">GCE</option>
            <option value="vm">VM</option>
            <option value="s3_bucket">S3</option>
            <option value="gcs_bucket">GCS</option>
            <option value="storage_account">Storage</option>
          </select>
          <button className="btn-secondary" onClick={load}>Apply</button>
        </div>
      </div>
      {error && <div className="alert alert-error">{error}</div>}
      {loading ? <div className="loading">Loading…</div> : (
        <>
          {util && (
            <div className="stats-grid">
              <div className="stat-card"><span className="stat-label">Total Resources</span><span className="stat-value">{util.total_resources}</span></div>
              <div className="stat-card"><span className="stat-label">Avg CPU</span><span className="stat-value">{util.avg_cpu.toFixed(1)}%</span></div>
              <div className="stat-card"><span className="stat-label">Avg Memory</span><span className="stat-value">{util.avg_memory.toFixed(1)}%</span></div>
              <div className="stat-card"><span className="stat-label">Underutilized</span><span className="stat-value" style={{ color: 'var(--medium)' }}>{util.underutilized}</span></div>
            </div>
          )}
          <ResourceTable resources={resources} />
          <div className="charts-row">
            <div className="table-section">
              <h3>Auto-Scaling Policies</h3>
              <table className="data-table">
                <thead><tr><th>Resource</th><th>Type</th><th>Min</th><th>Max</th><th>Threshold</th><th>Active</th></tr></thead>
                <tbody>
                  {policies.map((p: any) => (
                    <tr key={p.id}>
                      <td className="mono">{p.resource_id}</td>
                      <td>{p.type}</td>
                      <td>{p.min_size}</td><td>{p.max_size}</td>
                      <td>{p.threshold}% {p.metric}</td>
                      <td>{p.active ? '✅' : '❌'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="table-section">
              <h3>Scaling Predictions</h3>
              <table className="data-table">
                <thead><tr><th>Resource</th><th>Hours</th><th>Predicted CPU</th><th>Action</th><th>Conf.</th></tr></thead>
                <tbody>
                  {predictions.map((p: any) => (
                    <tr key={p.resource_id}>
                      <td className="mono">{p.resource_id}</td>
                      <td>{p.forecast_hours}h</td>
                      <td>{p.predicted_cpu.toFixed(1)}%</td>
                      <td><span className={`badge ${p.recommended_action === 'scale_up' ? 'badge-high' : p.recommended_action === 'scale_down' ? 'badge-low' : 'badge-medium'}`}>{p.recommended_action}</span></td>
                      <td>{(p.confidence * 100).toFixed(0)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          <div className="table-section">
            <h3>Multi-Cloud Workloads</h3>
            <table className="data-table">
              <thead><tr><th>Workload</th><th>Provider</th><th>Region</th><th>Replicas</th><th>Status</th><th>Deployed</th></tr></thead>
              <tbody>
                {workloads.map((w: any) => (
                  <tr key={w.id}>
                    <td className="mono">{w.name}</td>
                    <td><span className={`provider-dot provider-${w.provider}`}></span>{w.provider}</td>
                    <td>{w.region}</td>
                    <td>{w.replicas}</td>
                    <td><span className={`badge ${w.status === 'running' ? 'badge-low' : 'badge-medium'}`}>{w.status}</span></td>
                    <td>{w.deployed_at ? new Date(w.deployed_at).toLocaleDateString() : '—'}</td>
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
