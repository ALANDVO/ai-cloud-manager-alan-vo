import logging, uuid
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class AuditEngine:

    def __init__(self):
        self.findings: List[Dict[str, Any]] = []
        self.last_audit = datetime(2026, 10, 1, 8, 0, 0)
        self._run_initial_audit()

    def _run_initial_audit(self):
        checks = [
            ("aws", "ec2_instance", "i-0a1b2c3d", "Public IP on production instance", "high", "warning"),
            ("aws", "s3_bucket", "s3-bucket-data", "Bucket public ACL enabled", "high", "critical"),
            ("aws", "rds_instance", "rds-prod-db", "No encryption at rest", "high", "warning"),
            ("aws", "iam_role", "role-admin-full", "Wildcard policy on IAM role", "medium", "warning"),
            ("gcp", "gce_instance", "gce-prod-api-03", "Firewall allows 0.0.0.0/0:22", "high", "warning"),
            ("gcp", "gcs_bucket", "gcs-data-lake", "IAM inherited from project", "low", "pass"),
            ("gcp", "bigquery", "bq-analytics", "No row-level security", "medium", "warning"),
            ("azure", "vm", "vm-data-warehouse-01", "No disk encryption", "high", "warning"),
            ("azure", "storage_account", "stg-prod-001", "Blob public access enabled", "high", "critical"),
            ("azure", "sql_database", "sql-crm-01", "No customer-managed key", "medium", "warning"),
        ]
        for provider, rtype, rid, desc, severity, status in checks:
            self.findings.append({
                "id": f"finding-{uuid.uuid4().hex[:8]}",
                "provider": provider,
                "resource_type": rtype,
                "resource_id": rid,
                "check": desc,
                "severity": severity,
                "status": status,
                "detected_at": self.last_audit,
            })

    def get_audit(self) -> Dict[str, Any]:
        passed = sum(1 for f in self.findings if f["status"] == "pass")
        warnings = sum(1 for f in self.findings if f["status"] == "warning")
        critical = sum(1 for f in self.findings if f["status"] == "critical")
        return {
            "total_checks": len(self.findings),
            "passed": passed,
            "warnings": warnings,
            "critical": critical,
            "findings": sorted(self.findings, key=lambda f: (0 if f["status"] == "critical" else 1, f["severity"])),
            "last_audit": self.last_audit,
        }

audit_engine = AuditEngine()
