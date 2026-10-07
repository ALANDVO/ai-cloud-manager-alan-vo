import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './auth/AuthContext'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import Login from './pages/Login'
import CostDashboard from './pages/CostDashboard'
import SecurityPage from './pages/Security'
import Resources from './pages/Resources'
import Recommendations from './pages/Recommendations'
import Tenants from './pages/Tenants'

function ProtectedLayout({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="loading">Loading…</div>
  if (!user) return <Navigate to="/login" replace />
  return (
    <div className="app-shell">
      <Header />
      <div className="app-body">
        <Sidebar />
        <main className="main-content">{children}</main>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<ProtectedLayout><CostDashboard /></ProtectedLayout>} />
      <Route path="/security" element={<ProtectedLayout><SecurityPage /></ProtectedLayout>} />
      <Route path="/resources" element={<ProtectedLayout><Resources /></ProtectedLayout>} />
      <Route path="/recommendations" element={<ProtectedLayout><Recommendations /></ProtectedLayout>} />
      <Route path="/tenants" element={<ProtectedLayout><Tenants /></ProtectedLayout>} />
    </Routes>
  )
}
