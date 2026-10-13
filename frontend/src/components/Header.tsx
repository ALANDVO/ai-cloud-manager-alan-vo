import { useAuth } from '../auth/AuthContext';

export default function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="header">
      <div className="header-brand">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
        </svg>
        <span>AI Cloud Manager</span>
      </div>
      <div className="header-actions">
        {user && (
          <>
            <div className="header-user">
              <span className="avatar">{user.name?.charAt(0) || user.email?.charAt(0) || 'U'}</span>
              <span>{user.name || user.email}</span>
              <span style={{color: 'var(--fg-muted)'}}>({user.role})</span>
            </div>
            <button className="btn btn-ghost" onClick={logout}>Logout</button>
          </>
        )}
      </div>
    </header>
  );
}