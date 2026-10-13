import { useState, useEffect, useCallback } from 'react';
import { api } from '../api/client';

interface Recommendation {
  id: string;
  provider: string;
  service: string;
  category: string;
  title: string;
  description: string;
  estimated_savings_monthly: number;
  confidence: number;
  effort: string;
  action: string;
}

const CATEGORY_COLORS: Record<string, string> = {
  compute: 'var(--primary)',
  storage: 'var(--warning)',
  network: 'var(--success)',
  database: 'var(--danger)',
  reserved: 'var(--medium)',
};

const EFFORT_BADGES: Record<string, string> = {
  low: 'badge-success',
  medium: 'badge-warning',
  high: 'badge-danger',
};

export default function Recommendations() {
  const [recs, setRecs] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [generating, setGenerating] = useState(false);

  const load = useCallback(async () => {
    setLoading(true); setError('');
    try {
      const data = await api.recommendations();
      setRecs(data);
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  }, []);

  const generate = useCallback(async () => {
    setGenerating(true);
    try {
      const data = await api.generateRecs();
      setRecs(data);
    } catch (e: any) { setError(e.message); }
    finally { setGenerating(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const totalSavings = recs.reduce((sum, r) => sum + (r.estimated_savings_monthly || 0), 0);

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>AI Cost Optimization Recommendations</h2>
        <div className="filter-bar">
          <button className="btn btn-primary" onClick={generate} disabled={generating}>
            {generating ? 'Generating…' : 'Generate with AI'}
          </button>
        </div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {loading ? (
        <div className="loading">Loading recommendations…</div>
      ) : recs.length === 0 ? (
        <div className="empty-state">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" />
          </svg>
          <h3>No recommendations yet</h3>
          <p>Click "Generate with AI" to get cost optimization suggestions based on your cloud spend</p>
        </div>
      ) : (
        <>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="label">Total Recommendations</div>
              <div className="value">{recs.length}</div>
            </div>
            <div className="stat-card">
              <div className="label">Estimated Monthly Savings</div>
              <div className="value positive">${totalSavings.toFixed(2)}</div>
            </div>
            <div className="stat-card">
              <div className="label">High Confidence</div>
              <div className="value">{recs.filter(r => r.confidence >= 0.8).length}</div>
            </div>
            <div className="stat-card">
              <div className="label">Low Effort</div>
              <div className="value">{recs.filter(r => r.effort === 'low').length}</div>
            </div>
          </div>

          <div className="table-section">
            <div className="table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Provider</th>
                    <th>Service</th>
                    <th>Category</th>
                    <th>Est. Savings/mo</th>
                    <th>Confidence</th>
                    <th>Effort</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {recs.map((r) => (
                    <tr key={r.id}>
                      <td>
                        <div style={{ fontWeight: 500 }}>{r.title}</div>
                        <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{r.description}</div>
                      </td>
                      <td>{r.provider.toUpperCase()}</td>
                      <td>{r.service}</td>
                      <td>
                        <span
                          className="badge"
                          style={{
                            background: `${CATEGORY_COLORS[r.category] || '#666'}20`,
                            color: CATEGORY_COLORS[r.category] || '#888',
                          }}
                        >
                          {r.category}
                        </span>
                      </td>
                      <td className="positive">${(r.estimated_savings_monthly || 0).toFixed(2)}</td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <div style={{ width: '60px', height: '6px', background: '#334155', borderRadius: '3px', overflow: 'hidden' }}>
                            <div
                              style={{
                                width: `${Math.round((r.confidence || 0) * 100)}%`,
                                height: '100%',
                                background: r.confidence >= 0.8 ? 'var(--success)' : r.confidence >= 0.6 ? 'var(--warning)' : 'var(--danger)',
                              }}
                            />
                          </div>
                          <span style={{ fontSize: '0.8rem' }}>{Math.round((r.confidence || 0) * 100)}%</span>
                        </div>
                      </td>
                      <td>
                        <span className={`badge ${EFFORT_BADGES[r.effort] || 'badge-gray'}`}>
                          {r.effort}
                        </span>
                      </td>
                      <td style={{ fontSize: '0.8rem', color: '#94a3b8', maxWidth: '300px' }}>
                        {r.action}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}