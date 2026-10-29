import logging, json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone

from app.providers.base import CloudProvider

logger = logging.getLogger(__name__)


class AWSProvider(CloudProvider):

    def __init__(self, credentials: Dict[str, str]):
        super().__init__("aws", credentials)
        self.access_key = credentials.get("aws_access_key_id", "")
        self.secret_key = credentials.get("aws_secret_access_key", "")
        self.region = credentials.get("aws_default_region", "us-east-1")
        self._boto3 = None

    def _client(self, service: str):
        if self._boto3 is None:
            import boto3
            self._boto3 = boto3
        return self._boto3.client(service, region_name=self.region,
                                  aws_access_key_id=self.access_key,
                                  aws_secret_access_key=self.secret_key)

    def list_resources(self, resource_type: Optional[str] = None) -> List[Dict[str, Any]]:
        if not self.is_configured():
            return self._mock_resources(resource_type)
        resources = []
        try:
            ec2 = self._client("ec2")
            for reservation in ec2.describe_instances().get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    resources.append({
                        "id": instance["InstanceId"],
                        "provider": "aws",
                        "resource_type": "ec2_instance",
                        "name": self._tag(instance, "Name"),
                        "region": instance.get("Placement", {}).get("Region", self.region),
                        "status": instance.get("State", {}).get("Name", "unknown"),
                        "created_at": instance.get("LaunchTime", datetime.now(timezone.utc)),
                        "monthly_cost": 0.0,
                        "utilization": {},
                    })
            s3 = self._client("s3")
            for bucket in s3.list_buckets().get("Buckets", []):
                resources.append({
                    "id": bucket["Name"],
                    "provider": "aws",
                    "resource_type": "s3_bucket",
                    "name": bucket["Name"],
                    "region": self.region,
                    "status": "active",
                    "created_at": bucket.get("CreationDate", datetime.now(timezone.utc)),
                    "monthly_cost": 0.0,
                    "utilization": {},
                })
            rds = self._client("rds")
            for db in rds.describe_db_instances().get("DBInstances", []):
                resources.append({
                    "id": db["DBInstanceIdentifier"],
                    "provider": "aws",
                    "resource_type": "rds_instance",
                    "name": db["DBInstanceIdentifier"],
                    "region": db.get("DBInstanceArn", self.region).split(":")[3],
                    "status": db.get("DBInstanceStatus", "unknown"),
                    "created_at": db.get("InstanceCreateTime", datetime.now(timezone.utc)),
                    "monthly_cost": 0.0,
                    "utilization": {},
                })
        except Exception as e:
            logger.error("AWS resource listing failed: %s", e)
        if resource_type:
            resources = [r for r in resources if r["resource_type"] == resource_type]
        return resources

    def get_cost_data(self, days: int = 30) -> List[Dict[str, Any]]:
        costs = []
        try:
            ce = self._client("ce")
            end = datetime.now(timezone.utc)
            start = end - timedelta(days=days)
            resp = ce.get_cost_and_usage(
                TimePeriod={"Start": start.strftime("%Y-%m-%d"), "End": end.strftime("%Y-%m-%d")},
                Granularity="DAILY",
                Metrics=["UnblendedCost"],
                GroupBy=[{"Type": "SERVICE"}],
            )
            for result in resp.get("ResultsByTime", []):
                date_str = result["TimePeriod"]["Start"]
                for group in result.get("Groups", []):
                    service = group.get("Keys", ["unknown"])[0]
                    amount = float(group.get("Metrics", {}).get("UnblendedCost", {}).get("Amount", 0))
                    costs.append({"date": date_str, "provider": "aws", "service": service, "cost": amount})
        except Exception as e:
            logger.error("AWS cost data failed: %s", e)
        return costs

    def get_security_config(self) -> Dict[str, Any]:
        config = {"provider": "aws", "checks": []}
        try:
            iam = self._client("iam")
            for role in iam.list_roles().get("Roles", [])[:10]:
                config["checks"].append({"type": "iam_role", "name": role["RoleName"], "status": "review"})
            ec2 = self._client("ec2")
            sg = ec2.describe_security_groups().get("SecurityGroups", [])
            for group in sg[:10]:
                has_open_0_0 = any(
                    sg_rule.get("CidrIp") == "0.0.0.0/0" and sg_rule.get("FromPort") == 22
                    for sg_rule in group.get("IpPermissions", [])
                )
                config["checks"].append({
                    "type": "security_group", "name": group["GroupName"],
                    "status": "warning" if has_open_0_0 else "pass"
                })
        except Exception as e:
            logger.error("AWS security config failed: %s", e)
        return config

    def get_utilization(self) -> Dict[str, Any]:
        util = {"provider": "aws", "cpu": 0.0, "memory": 0.0, "storage": 0.0, "resources": 0}
        try:
            cw = self._client("cloudwatch")
            now = datetime.now(timezone.utc)
            start = now - timedelta(hours=1)
            resp = cw.get_metric_statistics(
                Namespace="AWS/EC2", MetricName="CPUUtilization",
                Dimensions=[{"Name": "InstanceId", "Value": "*"}],
                StartTime=start, EndTime=now, Period=3600, Statistic="Average",
            )
            datapoints = resp.get("Datapoints", [])
            if datapoints:
                util["cpu"] = sum(d["Average"] for d in datapoints) / len(datapoints)
            util["resources"] = len(datapoints)
        except Exception as e:
            logger.error("AWS utilization failed: %s", e)
        return util

    def _tag(self, instance: Dict, key: str) -> str:
        for tag in instance.get("Tags", []):
            if tag.get("Key") == key:
                return tag.get("Value", "")
        return instance.get("InstanceId", "unknown")

    def _mock_resources(self, resource_type: Optional[str] = None) -> List[Dict[str, Any]]:
        mock = [
            {
                "id": "i-0a1b2c3d4e5f67890",
                "provider": "aws",
                "resource_type": "ec2_instance",
                "name": "prod-web-01",
                "region": "us-east-1",
                "status": "running",
                "created_at": datetime.now(timezone.utc),
                "monthly_cost": 73.00,
                "utilization": {"cpu": 45.2, "memory": 62.1},
            },
            {
                "id": "i-0b2c3d4e5f6789012",
                "provider": "aws",
                "resource_type": "ec2_instance",
                "name": "prod-api-02",
                "region": "us-east-1",
                "status": "running",
                "created_at": datetime.now(timezone.utc),
                "monthly_cost": 146.00,
                "utilization": {"cpu": 78.5, "memory": 82.3},
            },
            {
                "id": "s3-data-lake-prod",
                "provider": "aws",
                "resource_type": "s3_bucket",
                "name": "data-lake-prod",
                "region": "us-east-1",
                "status": "active",
                "created_at": datetime.now(timezone.utc),
                "monthly_cost": 234.50,
                "utilization": {"storage": 67.0},
            },
            {
                "id": "rds-prod-db-01",
                "provider": "aws",
                "resource_type": "rds_instance",
                "name": "prod-db-01",
                "region": "us-east-1",
                "status": "available",
                "created_at": datetime.now(timezone.utc),
                "monthly_cost": 445.00,
                "utilization": {"cpu": 34.7, "memory": 71.2, "storage": 45.0},
            },
        ]
        if resource_type:
            mock = [r for r in mock if r["resource_type"] == resource_type]
        return mock
