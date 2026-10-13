
interface ResourceTableProps {
  resources: Array<{
    id: string;
    name: string;
    provider: string;
    resource_type: string;
    region: string;
    status: string;
    monthly_cost?: number;
    utilization?: Record<string, number>;
  }>;
}

const STATUS_BADGES: Record<string, string> = {
  running: 'badge-success',
  stopped: 'badge-gray',
  pending: 'badge-warning',
  error: 'badge-danger',
  terminated: 'badge-gray',
};

const PROVIDER_ICONS: Record<string, string> = {
  aws: '☁️',
  gcp: '☁️',
  azure: '☁️',
};

export default function ResourceTable({ resources }: ResourceTableProps) {
  if (!resources?.length) {
    return (
      <div className="table-section">
        <div className="empty-state" style={{ padding: '48px' }}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
            <rect x="2" y="3" width="20" height="14" rx="2" />
            <path d="M8 21h8M12 17v4" />
          </svg>
          <h3>No resources found</h3>
          <p>Configure cloud provider credentials to discover resources</p>
        </div>
      </div>
    );
  }

  return (
    <div className="table-section">
      <h3>Resources ({resources.length})</h3>
      <div className="table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th>Provider</th>
              <th>Name / ID</th>
              <th>Type</th>
              <th>Region</th>
              <th>Status</th>
              <th>Monthly Cost</th>
              <th>Utilization</th>
            </tr>
          </thead>
          <tbody>
            {resources.slice(0, 100).map((r) => (
              <tr key={r.id}>
                <td>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span>{PROVIDER_ICONS[r.provider] || '☁️'}</span>
                    {r.provider.toUpperCase()}
                  </span>
                </td>
                <td>
                  <div style={{ fontWeight: 500 }}>{r.name}</div>
                  <div style={{ fontSize: '0.7rem', color: '#94a3b8' }}>{r.id}</div>
                </td>
                <td>{r.resource_type}</td>
                <td>{r.region}</td>
                <td>
                  <span className={`badge ${STATUS_BADGES[r.status] || 'badge-gray'}`}>
                    {r.status}
                  </span>
                </td>
                <td>${(r.monthly_cost || 0).toFixed(2)}</td>
                <td>
                  {r.utilization && Object.keys(r.utilization).length > 0 ? (
                    <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                      {Object.entries(r.utilization).map(([key, val]) => (
                        <span key={key} style={{ fontSize: '0.7rem', color: '#94a3b8' }}>
                          {key}: {Math.round(val)}%
                        </span>
                      ))}
                    </div>
                  ) : (
                    <span style={{ color: '#94a3b8', fontSize: '0.8rem' }}>—</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {resources.length > 100 && (
        <div style={{ padding: '12px 20px', borderTop: '1px solid var(--border)', color: '#94a3b8', fontSize: '0.8rem' }}>
          Showing 100 of {resources.length} resources
        </div>
      )}
    </div>
  );
}