import { useAuth } from '../auth/AuthContext'

export default function Login() {
  const { login } = useAuth()
  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-logo">☁️</div>
        <h1>AI Cloud Manager</h1>
        <p className="login-sub">Multi-Cloud Cost Optimization &amp; Security</p>
        <button className="btn-primary" onClick={login}>Sign in with SSO</button>
        <p className="login-footer">Powered by AI · Enterprise Edition</p>
      </div>
    </div>
  )
}
