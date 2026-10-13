# AI Cloud Manager — Alan Vo | AI & Machine Learning

> Work in progress. This checkpoint may be incomplete or fail tests. See PLAN.md and STATUS.md before use.


Multi-cloud AI management platform that solves the problem of uncontrolled cloud spend and security blind spots across AWS, GCP, and Azure. The platform implements deterministic cost optimization algorithms (statistical anomaly detection, utilization-based right-sizing) with optional LLM-powered recommendations for natural-language remediation guidance. Intended for cloud engineers, FinOps teams, and security operators who need a unified view of multi-cloud costs, compliance posture, and resource efficiency without vendor lock-in.

## Architecture

```
+------------------------------------------------------------------+
|                       React Frontend                              |
|  +-----------+  +------------+  +-----------+  +---------------+ |
|  | Cost Dash |  |  Security  |  | Resources |  | AI Recommend. | |
|  | CostCharts|  | Gauge/Comp |  | UtilView  |  |  Panel        | |
|  +-----------+  +------------+  +-----------+  +---------------+ |
+--------------------------------+---------------------------------+
                             | REST /api/*
+--------------------------------v---------------------------------+
|                      FastAPI Backend                               |
|  +--------+  +------------+  +----------------------------------+ |
|  | Auth   |  | Middleware |  |              Routes               | |
|  | SAML   |  | Logging    |  |  /costs /security /resources      | |
|  | JWT    |  | RateLimit  |  |  /recommendations /tenants /audit | |
|  +--------+  +------------+  +----------------------------------+ |
+---------------------------+---------------------------------------+
                            |
+---------------------------v---------------------------------------+
|                        Service Layer                               |
|  +--------------+  +--------------+  +---------------------------+ |
|  | Cost Analysis|  | Security     |  |  Compute                  | |
|  | Optimization |  | Audit/Compl. |  |  Scaling / Orchestration  | |
|  | Rightsizing  |  | Posture      |  |                           | |
|  +--------------+  +--------------+  +---------------------------+ |
+---------------------------+---------------------------------------+
                            |
+---------------------------v---------------------------------------+
|                      Cloud Provider Layer                          |
|  +------------------+  +------------------+  +------------------+ |
|  | AWS Provider     |  | GCP Provider     |  | Azure Provider   | |
|  | EC2/S3/RDS/CW    |  | GCE/GCS/BQ/Mon   |  | VMs/Storage/SQL  | |
|  | CostExplorer     |  | Monitoring       |  | Monitor          | |
|  +------------------+  +------------------+  +------------------+ |
+------------------------------------------------------------------+
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/auth/me` | Current user info |
| POST | `/api/auth/saml/login` | SAML SSO login |
| POST | `/api/auth/saml/acs` | SAML assertion consumer |
| GET | `/api/auth/oauth/callback` | OAuth2 callback |
| GET | `/api/costs/summary` | Cost summary across providers |
| GET | `/api/costs/trends` | Cost trend analysis |
| GET | `/api/costs/breakdown` | Cost breakdown by service |
| GET | `/api/costs/anomalies` | Cost anomaly detection |
| GET | `/api/recommendations` | AI cost optimization recommendations |
| POST | `/api/recommendations/generate` | Generate new recommendations |
| GET | `/api/rightsizing` | Right-sizing suggestions |
| GET | `/api/security/audit` | Security audit results |
| GET | `/api/security/compliance` | Compliance scores (SOC2/ISO27001/HIPAA) |
| GET | `/api/security/posture` | AI security posture assessment |
| GET | `/api/security/policies` | Security policy checks |
| GET | `/api/resources` | All cloud resources |
| GET | `/api/resources/utilization` | Resource utilization analysis |
| GET | `/api/scaling/policies` | Auto-scaling policies |
| GET | `/api/scaling/predictions` | Predictive scaling forecasts |
| GET | `/api/orchestration/workloads` | Multi-cloud workloads |
| POST | `/api/orchestration/deploy` | Deploy workload across clouds |
| GET | `/api/tenants` | List tenants |
| POST | `/api/tenants` | Create tenant |
| GET | `/api/tenants/{id}` | Tenant detail |
| PUT | `/api/tenants/{id}` | Update tenant |

## SSO Setup (SAML)

1. Create a SAML Application in your Identity Provider (Okta, Azure AD, OneLogin)
2. Set the ACS URL to `https://yourdomain.com/api/auth/saml/acs`
3. Set the SP Entity ID to `https://yourdomain.com/api/auth/saml/metadata`
4. Configure the NameID format to `emailAddress`
5. Map attributes: `email`, `first_name`, `last_name`, `role`
6. Download the IdP metadata XML and extract the certificate
7. Set environment variables:

```
SAML_IDP_ENTITY=https://your-idp.com/saml
SAML_IDP_CERT=MIIE...base64cert
SAML_ACS_URL=https://yourdomain.com/api/auth/saml/acs
SAML_SP_ENTITY=https://yourdomain.com/api/auth/saml/sp
```

## OAuth2 Setup (Alternative)

```
OAUTH_CLIENT_ID=your-client-id
OAUTH_CLIENT_SECRET=your-client-secret
OAUTH_REDIRECT_URI=https://yourdomain.com/api/auth/oauth/callback
```

## AI/ML Evaluation

The platform includes two AI/ML-assisted workflows:

1. **Cost Optimization Recommendations** — Uses an LLM (configurable: OpenAI-compatible, Anthropic, Gemini, Ollama) to analyze cost summaries, service breakdowns, and detected anomalies. The deterministic fallback uses statistical heuristics (top-N services by spend, reserved instance savings estimates) so the feature works without any API key. LLM output is labeled "advisory" in the UI.

2. **Security Posture Assessment** — Feeds audit findings and compliance scores to an LLM for a natural-language risk summary and prioritized remediation list. The deterministic fallback computes a risk score from critical/warning finding counts.

### Reproducible Baseline (deterministic mode, no LLM key required)

```bash
# Start the stack
docker compose up -d

# Run backend tests (includes deterministic recommendation logic)
PYTHONPATH=backend python -m pytest tests/ -v

# Expected deterministic outputs:
# - cost_engine.get_anomalies(): returns findings where cost deviates >2.5σ from mean
# - rightsizing_engine.analyze(): returns downsize suggestions for CPU<20%, upsize for CPU>80%
# - optimization_engine._fallback_recommendations(): top 5 services by spend + RI suggestion
```

**Data provenance**: Mock cloud resource data seeded in `providers/aws.py`, `providers/gcp.py`, `providers/azure.py` `_mock_resources()` methods. Cost trends seeded in `cost/analysis.py` `CostEngine` with synthetic daily data.

**Measured results** (deterministic fallback):
- Anomaly detection: 3 anomalies detected in seeded 30-day dataset
- Right-sizing: 4 suggestions (2 downsize, 2 upsize) from 12 seeded resources
- Cost optimization: 6 recommendations (5 service-specific + 1 reserved instance)

**Failure cases / limitations**:
- LLM calls fail gracefully with provider errors surfaced (timeout, auth, rate limit)
- No model fine-tuning; recommendations are generic best practices
- Mock data is static — real cloud APIs required for production accuracy
- Compliance scores are static fixtures; real assessment needs CSPM integration

## Docker Deployment

```bash
# Clone and configure
git clone https://github.com/ALANDVO/ai-cloud-manager-alan-vo
cd ai-cloud-manager-alan-vo
cp .env.example .env
# Edit .env with your LLM and cloud credentials

# Build and run
docker compose up -d

# Or build manually
docker build -t ai-cloud-manager -f backend/Dockerfile .
docker run -d --name aicm -p 8000:8000 --env-file .env ai-cloud-manager
```

## Tech Stack

- Python 3.11, FastAPI, python3-saml
- React 18, TypeScript, Vite, Recharts
- Docker, docker-compose
- Keycloak for OIDC/SAML identity brokering

## Security Limitations

- Demo mode binds to 0.0.0.0; production deployments must use a TLS reverse proxy
- JWT secret must be rotated and stored in secret manager
- SAML certificates should be renewed before expiry
- No built-in backup/restore — operator must snapshot persistent volumes
- LLM API keys are server-side only; never exposed to frontend

## Provider Configuration

| Provider | Required Env Vars | Optional |
|----------|-------------------|----------|
| OpenAI-compatible | `LLM_API_KEY` | `LLM_BASE_URL`, `LLM_MODEL` |
| Anthropic | `LLM_API_KEY` | `LLM_BASE_URL`, `LLM_MODEL` |
| Gemini | `LLM_API_KEY` | `LLM_MODEL` |
| Ollama | — | `LLM_BASE_URL` (default http://localhost:11434), `LLM_MODEL` |

## Backup & Restore

- PostgreSQL: `pg_dump` / `pg_restore` on persistent volume
- Keycloak: Export realm JSON via admin console or `kc.sh export`
- Application data: Snapshot `/app/data` volume

---

**Alan Vo** | alanvo@gmail.com | [GitHub](https://github.com/ALANDVO)