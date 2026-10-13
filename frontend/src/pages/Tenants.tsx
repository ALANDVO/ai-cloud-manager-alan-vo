import { useState, useEffect, useCallback } from 'react'
import { api } from '../api/client'

interface Tenant {
  id: string
  name: string
  plan: string
  status: string
  cloud_providers: string[]
  user_count: number
  created_at: string
}

interface ProviderConn {
  provider: string
  status: string
  account: string
  last_sync: string
}

export default function Tenants() {
  const [tenants, setTenants] = useState<Tenant[]>([])
  const [selected, setSelected] = useState('')
  const [connections, setConnections] = useState<ProviderConn[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState({ name: '', plan: 'standard' })

  const load = useCallback(async () => {
    setLoading(true); setError('')
    try { setTenants(await api.tenants()) }
    catch (e) { setError(e instanceof Error ? e.message : String(e)) }
    finally { setLoading(false) }
  }, [])

  const loadConnections = useCallback(async (id: string) => {
    try {
      if (id) { setConnections(await api.tenantConnections(id)) } else { setConnections([]) }
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
      setConnections([])
    }
  }, [])

  const create = useCallback(async (ev: React.FormEvent) => {
    ev.preventDefault()
    try {
      await api.createTenant(form)
      setShowModal(false); setForm({ name: '', plan: 'standard' }); load()
    } catch (e) { setError(e instanceof Error ? e.message : String(e)) }
  }, [form, load])

  useEffect(() => { load() }, [load])
  useEffect(() => { loadConnections(selected) }, [selected, loadConnections])

  return (
    <div className="tenants-page">
      <div className="dashboard-header">
        <h2>Multi-Tenant Management</h2>
        <button className="btn-primary" onClick={() => setShowModal(true)}>+ New Tenant</button>
      </div>
      {error && <div className="alert alert-error">{error}</div>}
      {loading ? <div className="loading">Loading…</div> : (
        <div className="tenants-layout">
          <div className="tenant-list">
            {tenants.map((t) => (
              <button key={t.id} className={`tenant-item ${t.id === selected ? 'active' : ''}`} onClick={() => setSelected(t.id)}>
                <span className="tenant-name">{t.name}</span>
                <span className={`badge badge-${t.status === 'active' ? 'low' : 'high'}`}>{t.status}</span>
                <span className="tenant-meta">{t.user_count} users · {t.plan}</span>
              </button>
            ))}
          </div>
          <div className="tenant-detail">
            <h3>Cloud Provider Connections</h3>
            {selected && connections.length > 0 ? (
              <table className="data-table">
                <thead><tr><th>Provider</th><th>Account</th><th>Status</th><th>Last Sync</th></tr></thead>
                <tbody>
                  {connections.map((c) => (
                    <tr key={c.provider}>
                      <td><span className={`provider-dot provider-${c.provider}`}></span>{c.provider}</td>
                      <td className="mono">{c.account}</td>
                      <td><span className={`badge badge-${c.status === 'connected' ? 'low' : 'high'}`}>{c.status}</span></td>
                      <td>{c.last_sync}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="empty-state">{selected ? 'No connections' : 'Select a tenant'}</div>
            )}
          </div>
        </div>
      )}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Create Tenant</h3>
            <form onSubmit={create}>
              <label>Name
                <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
              </label>
              <label>Plan
                <select value={form.plan} onChange={(e) => setForm({ ...form, plan: e.target.value })}>
                  <option value="standard">standard</option>
                  <option value="enterprise">enterprise</option>
                </select>
              </label>
              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn-primary">Create</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
