import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../auth/AuthContext';
import CostDashboard from '../pages/CostDashboard';
import SecurityPage from '../pages/Security';
import Resources from '../pages/Resources';
import Recommendations from '../pages/Recommendations';
import Tenants from '../pages/Tenants';
import Login from '../pages/Login';

// Mock the API client
vi.mock('../api/client', () => ({
  api: {
    me: vi.fn().mockResolvedValue({ email: 'test@example.com', name: 'Test User', role: 'operator' }),
    health: vi.fn().mockResolvedValue({ status: 'ok', service: 'ai-cloud-manager', version: '1.0.0' }),
    costSummary: vi.fn().mockResolvedValue({
      total_monthly: 5000,
      by_provider: { aws: 2000, gcp: 1500, azure: 1500 },
      by_service: { ec2: 1800, s3: 200, rds: 500 },
      month_over_month_change: 5.2,
      forecast_next_month: 5250,
      savings_available: 350,
    }),
    costTrends: vi.fn().mockResolvedValue([
      { date: '2026-10-01', cost: 160, provider: 'aws' },
      { date: '2026-10-02', cost: 165, provider: 'aws' },
      { date: '2026-10-01', cost: 120, provider: 'gcp' },
      { date: '2026-10-02', cost: 125, provider: 'gcp' },
    ]),
    costBreakdown: vi.fn().mockResolvedValue([
      { provider: 'aws', service: 'ec2', resource_type: 'instance', monthly_cost: 1800, daily_cost: 60, percent_of_total: 36 },
      { provider: 'gcp', service: 'gce', resource_type: 'instance', monthly_cost: 1200, daily_cost: 40, percent_of_total: 24 },
      { provider: 'azure', service: 'vm', resource_type: 'instance', monthly_cost: 900, daily_cost: 30, percent_of_total: 18 },
    ]),
    costAnomalies: vi.fn().mockResolvedValue([]),
    recommendations: vi.fn().mockResolvedValue([]),
    generateRecs: vi.fn().mockResolvedValue([
      { id: 'rec-1', provider: 'aws', service: 'ec2', category: 'compute', title: 'Review EC2 usage', description: 'EC2 costs $1800/mo', estimated_savings_monthly: 450, confidence: 0.8, effort: 'medium', action: 'AWS Console > EC2 > Right-sizing' },
    ]),
    rightsizing: vi.fn().mockResolvedValue([
      { resource_id: 'i-0a1b2c3d', provider: 'aws', resource_type: 'ec2_instance', name: 'prod-web-01', current_spec: 't3.large', recommended_spec: 't3.medium', current_monthly_cost: 73, estimated_savings_monthly: 36.5, reason: 'underutilized', confidence: 0.85 },
    ]),
    securityAudit: vi.fn().mockResolvedValue({
      total_checks: 10,
      passed: 5,
      warnings: 3,
      critical: 2,
      findings: [
        { id: 'f-1', provider: 'aws', resource_type: 's3_bucket', resource_id: 'bucket-1', check: 'Public ACL', severity: 'high', status: 'critical', detected_at: '2026-10-01T00:00:00Z' },
      ],
      last_audit: '2026-10-01T00:00:00Z',
    }),
    compliance: vi.fn().mockResolvedValue([
      { framework: 'SOC2', score: 78, max_score: 100, status: 'partial', categories: [], last_assessed: '2026-10-01T00:00:00Z' },
      { framework: 'ISO27001', score: 72, max_score: 100, status: 'partial', categories: [], last_assessed: '2026-10-01T00:00:00Z' },
    ]),
    posture: vi.fn().mockResolvedValue({
      overall_score: 65,
      risk_level: 'medium',
      summary: 'Security posture needs improvement',
      top_risks: [{ risk: 'Unencrypted storage', impact: 'data_breach', likelihood: 'medium', mitigation: 'Enable encryption' }],
      recommendations: ['Enable encryption', 'Implement MFA'],
      assessed_at: '2026-10-01T00:00:00Z',
    }),
    resources: vi.fn().mockResolvedValue([
      { id: 'i-0a1b2c3d', name: 'prod-web-01', provider: 'aws', resource_type: 'ec2_instance', region: 'us-east-1', status: 'running', monthly_cost: 73, utilization: { cpu: 45, memory: 62 } },
    ]),
    utilization: vi.fn().mockResolvedValue({
      total_resources: 10,
      by_provider: { aws: 5, gcp: 3, azure: 2 },
      avg_cpu: 52.3,
      avg_memory: 61.7,
      underutilized: 3,
      overutilized: 1,
    }),
    scalingPolicies: vi.fn().mockResolvedValue([
      { id: 'p-1', resource_id: 'i-0a1b2c3d', provider: 'aws', type: 'horizontal', min_size: 2, max_size: 10, metric: 'CPUUtilization', threshold: 70, cooldown_minutes: 5, active: true },
    ]),
    scalingPredictions: vi.fn().mockResolvedValue([
      { resource_id: 'i-0a1b2c3d', provider: 'aws', forecast_hours: 24, predicted_cpu: 82.5, recommended_action: 'scale_up', confidence: 0.88 },
    ]),
    workloads: vi.fn().mockResolvedValue([
      { id: 'wl-1', name: 'api-gateway', provider: 'aws', region: 'us-east-1', resource_type: 'ec2_instance', replicas: 6, status: 'running', deployed_at: '2026-10-01T00:00:00Z' },
    ]),
    tenants: vi.fn().mockResolvedValue([
      { id: 't-1', name: 'Default', plan: 'enterprise', status: 'active', cloud_providers: ['aws', 'gcp', 'azure'], user_count: 5, created_at: '2026-09-01T00:00:00Z' },
    ]),
    createTenant: vi.fn().mockResolvedValue({ id: 't-2', name: 'New Tenant', plan: 'standard', status: 'active', cloud_providers: ['aws'], user_count: 0, created_at: '2026-10-13T00:00:00Z' }),
    tenant: vi.fn().mockResolvedValue({ id: 't-1', name: 'Default', plan: 'enterprise', status: 'active', cloud_providers: ['aws', 'gcp', 'azure'], user_count: 5, created_at: '2026-09-01T00:00:00Z' }),
  },
}));

const renderWithProviders = (component: React.ReactNode) => {
  return render(
    <BrowserRouter>
      <AuthProvider>
        {component}
      </AuthProvider>
    </BrowserRouter>
  );
};

describe('CostDashboard', () => {
  it('renders cost summary stats', async () => {
    renderWithProviders(<CostDashboard />);
    await waitFor(() => expect(screen.getByText('Cost Dashboard')).toBeInTheDocument(), { timeout: 3000 });
    await waitFor(() => expect(screen.getByText('$5,000')).toBeInTheDocument(), { timeout: 3000 });
  });
});

describe('SecurityPage', () => {
  it('renders security audit and compliance', async () => {
    renderWithProviders(<SecurityPage />);
    await waitFor(() => expect(screen.getByText('Security Posture')).toBeInTheDocument());
    await waitFor(() => expect(screen.getByText('SOC2')).toBeInTheDocument());
  });
});

describe('Resources', () => {
  it('renders resource table', async () => {
    renderWithProviders(<Resources />);
    await waitFor(() => expect(screen.getByText('Cloud Resources')).toBeInTheDocument());
    await waitFor(() => expect(screen.getByText('prod-web-01')).toBeInTheDocument(), { timeout: 3000 });
  });
});

describe('Recommendations', () => {
  it('renders recommendations page with generate button', async () => {
    renderWithProviders(<Recommendations />);
    await waitFor(() => expect(screen.getByText('AI Cost Optimization Recommendations')).toBeInTheDocument(), { timeout: 3000 });
    await waitFor(() => expect(screen.getByText('Generate with AI')).toBeInTheDocument(), { timeout: 3000 });
  });
});

describe('Tenants', () => {
  it('renders tenant page', async () => {
    renderWithProviders(<Tenants />);
    // Component renders tenant detail section
    await waitFor(() => expect(screen.getByText('Select a tenant')).toBeInTheDocument(), { timeout: 3000 });
  });
});

describe('Login', () => {
  it('renders login page with SSO button', () => {
    renderWithProviders(<Login />);
    expect(screen.getByText('AI Cloud Manager')).toBeInTheDocument();
    expect(screen.getByText('Sign in with SSO')).toBeInTheDocument();
  });
});