# Changelog

## 1.3.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.2.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-13

### Added
- Initial release of AI Cloud Manager
- Multi-cloud cost dashboard with trend analysis, breakdown by service, and anomaly detection
- AI-powered cost optimization recommendations with fallback heuristics
- Resource right-sizing suggestions for under/over-utilized instances across AWS, GCP, Azure
- Security audit engine with findings for public resources, encryption, IAM policies
- Compliance scoring for SOC2, ISO27001, HIPAA frameworks
- AI security posture assessment with risk scoring and prioritized recommendations
- Cloud resource inventory with filtering by provider, type, region
- Resource utilization analysis with CPU, memory, storage metrics
- Auto-scaling policies management (horizontal and vertical)
- Predictive scaling forecasts with confidence scores
- Multi-cloud workload orchestration and deployment
- Tenant management with multi-cloud provider connections
- SAML SSO authentication with Keycloak/IdP support
- OAuth2 authentication as alternative
- JWT-based session management with role-based access control
- Rate limiting and request logging middleware
- Docker and docker-compose deployment configurations
- React + TypeScript frontend with Vite, Recharts visualizations
- Responsive dark-theme UI with sidebar navigation

### Fixed
- Syntax errors in LLM integration f-strings (optimization.py, posture.py)
- Import paths after backend restructuring to backend/app/
- Provider registry to return mock data when cloud credentials not configured
- Test imports to use PYTHONPATH=backend

### Security
- No hardcoded secrets; all credentials via environment variables
- JWT tokens with configurable expiry
- Rate limiting on API endpoints
- Input validation via Pydantic models