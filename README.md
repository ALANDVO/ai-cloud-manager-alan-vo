# AI Cloud Manager

Multi-cloud AI management platform with cost optimization, security posture scoring, resource right-sizing, compliance auditing, and AI-powered recommendations across AWS, GCP, and Azure.

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
docker build -t ai-cloud-manager .
docker run -d --name aicm -p 8000:8000 --env-file .env ai-cloud-manager
```

## Tech Stack

- Python 3.11, FastAPI, python3-saml
- React 18, TypeScript, Vite, Recharts
- Docker, docker-compose

**Built by [Alan Vo](https://github.com/ALANDVO)** | alanvo@gmail.com | AI, ML & Cybersecurity
