# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

tenant-connections

## Roadmap

### tenant-connections — Tenant cloud provider connections endpoint

Status: done

Acceptance:
- GET /api/tenants/{id}/connections returns connections filtered by tenant's configured providers
- Response validated against ProviderConnection schema
- Test verifies default tenant returns all three provider connections

Implementation: `backend/app/api/routes.py`, `backend/app/api/schemas.py`, `tests/test_core.py`

Tests: `tests/test_core.py::test_tenant_connections`

### continue-implementation — Continue implementation and resolve known failures

Status: done

Acceptance:
- Run checks, fix failures, and implement the next planned feature

Implementation: `backend/app/providers/registry.py`, `tests/test_core.py`

Tests: `tests/test_core.py`

---

Alan Vo · [alanvo.net](https://alanvo.net) · [X: @alanvoasi](https://x.com/alanvoasi)
