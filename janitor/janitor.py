import argparse
import json
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError

from constants import (
    DEFAULT_ACCOUNT_ID,
    DEFAULT_ENDPOINT_URL,
    DEFAULT_REGION,
    DEFAULT_STOPPED_DAYS,
    EBS_GB_MONTH_USD,
    MISSING_TAG_COST_USD,
    REPORT_JSON_PATH,
    REPORT_MARKDOWN_PATH,
    REQUIRED_TAGS,
    STOPPED_EC2_MONTHLY_ESTIMATE_USD,
    UNUSED_EIP_MONTHLY_ESTIMATE_USD,
)


Finding = Dict[str, Any]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Cost Janitor: detect orphaned AWS resources using boto3."
    )

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Scan and report findings without deleting anything. This is the default.",
    )
    mode.add_argument(
        "--delete",
        action="store_true",
        help="Delete safe orphaned resources. Protected=true resources are skipped.",
    )

    parser.add_argument(
        "--region",
        default=DEFAULT_REGION,
        help="AWS region to scan. Defaults to us-east-1.",
    )

    parser.add_argument(
        "--endpoint-url",
        default=DEFAULT_ENDPOINT_URL,
        help="LocalStack endpoint URL. Defaults to http://localhost:4566.",
    )

    parser.add_argument(
        "--stopped-days",
        type=int,
        default=DEFAULT_STOPPED_DAYS,
        help="Stopped EC2 instances older than this many days are treated as orphans.",
    )

    parser.add_argument(
        "--report-json",
        default=REPORT_JSON_PATH,
        help="Path for JSON report output.",
    )

    parser.add_argument(
        "--report-md",
        default=REPORT_MARKDOWN_PATH,
        help="Path for Markdown report output.",
    )

    args = parser.parse_args()
    if args.delete:
        args.dry_run = False

    return args


def create_ec2_client(region: str, endpoint_url: str):
    return boto3.client(
        "ec2",
        region_name=region,
        endpoint_url=endpoint_url,
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return now_utc().replace(microsecond=0).isoformat().replace("+00:00", "Z")


def tags_to_dict(tags: Optional[List[Dict[str, str]]]) -> Dict[str, Optional[str]]:
    if not tags:
        return {}

    return {tag.get("Key"): tag.get("Value") for tag in tags if tag.get("Key")}


def is_protected(tags: Dict[str, Optional[str]]) -> bool:
    return str(tags.get("Protected", "")).lower() == "true"


def missing_required_tags(tags: Dict[str, Optional[str]]) -> List[str]:
    missing = []

    for tag in REQUIRED_TAGS:
        if not tags.get(tag):
            missing.append(tag)

    return missing


def calculate_age_days(created_at: Optional[datetime]) -> int:
    if not created_at:
        return 0

    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    return max((now_utc() - created_at).days, 0)


def make_finding(
    resource_id: str,
    resource_type: str,
    reason: str,
    age_days: int,
    estimated_monthly_cost_usd: float,
    tags: Dict[str, Optional[str]],
    suggested_action: str,
    safe_to_auto_delete: bool,
) -> Finding:
    return {
        "resource_id": resource_id,
        "resource_type": resource_type,
        "reason": reason,
        "age_days": age_days,
        "estimated_monthly_cost_usd": round(float(estimated_monthly_cost_usd), 2),
        "tags": tags,
        "suggested_action": suggested_action,
        "safe_to_auto_delete": safe_to_auto_delete,
    }


def paginate(ec2_client, operation_name: str) -> List[Dict[str, Any]]:
    paginator = ec2_client.get_paginator(operation_name)
    return list(paginator.paginate())


def find_unattached_ebs_volumes(ec2_client) -> List[Finding]:
    findings: List[Finding] = []

    for page in paginate(ec2_client, "describe_volumes"):
        for volume in page.get("Volumes", []):
            volume_id = volume.get("VolumeId", "unknown")
            state = volume.get("State")
            tags = tags_to_dict(volume.get("Tags"))
            age_days = calculate_age_days(volume.get("CreateTime"))

            if state == "available":
                size_gb = volume.get("Size", 0)
                estimated_cost = size_gb * EBS_GB_MONTH_USD
                protected = is_protected(tags)

                findings.append(
                    make_finding(
                        resource_id=volume_id,
                        resource_type="ebs_volume",
                        reason="unattached",
                        age_days=age_days,
                        estimated_monthly_cost_usd=estimated_cost,
                        tags=tags,
                        suggested_action="delete",
                        safe_to_auto_delete=not protected,
                    )
                )

    return findings


def find_stopped_ec2_instances(ec2_client, stopped_days: int) -> List[Finding]:
    findings: List[Finding] = []

    for page in paginate(ec2_client, "describe_instances"):
        for reservation in page.get("Reservations", []):
            for instance in reservation.get("Instances", []):
                instance_id = instance.get("InstanceId", "unknown")
                state = instance.get("State", {}).get("Name")
                tags = tags_to_dict(instance.get("Tags"))
                age_days = calculate_age_days(instance.get("LaunchTime"))

                if state == "stopped" and age_days > stopped_days:
                    protected = is_protected(tags)

                    findings.append(
                        make_finding(
                            resource_id=instance_id,
                            resource_type="ec2_instance",
                            reason=f"stopped_more_than_{stopped_days}_days",
                            age_days=age_days,
                            estimated_monthly_cost_usd=STOPPED_EC2_MONTHLY_ESTIMATE_USD,
                            tags=tags,
                            suggested_action="terminate",
                            safe_to_auto_delete=not protected,
                        )
                    )

    return findings


def find_unused_elastic_ips(ec2_client) -> List[Finding]:
    findings: List[Finding] = []

    try:
        response = ec2_client.describe_addresses()
    except ClientError as exc:
        print(f"Warning: could not describe Elastic IPs: {exc}", file=sys.stderr)
        return findings

    for address in response.get("Addresses", []):
        allocation_id = address.get("AllocationId")
        public_ip = address.get("PublicIp", "unknown")
        association_id = address.get("AssociationId")
        tags = tags_to_dict(address.get("Tags"))

        resource_id = allocation_id or public_ip

        if not association_id:
            protected = is_protected(tags)

            findings.append(
                make_finding(
                    resource_id=resource_id,
                    resource_type="elastic_ip",
                    reason="unassociated",
                    age_days=0,
                    estimated_monthly_cost_usd=UNUSED_EIP_MONTHLY_ESTIMATE_USD,
                    tags=tags,
                    suggested_action="release",
                    safe_to_auto_delete=not protected,
                )
            )

    return findings


def find_missing_tags(ec2_client) -> List[Finding]:
    findings: List[Finding] = []
    for page in paginate(ec2_client, "describe_instances"):
        for reservation in page.get("Reservations", []):
            for instance in reservation.get("Instances", []):
                instance_id = instance.get("InstanceId", "unknown")
                tags = tags_to_dict(instance.get("Tags"))
                missing = missing_required_tags(tags)

                if missing:
                    findings.append(
                        make_finding(
                            resource_id=instance_id,
                            resource_type="ec2_instance",
                            reason=f"missing_required_tags:{','.join(missing)}",
                            age_days=calculate_age_days(instance.get("LaunchTime")),
                            estimated_monthly_cost_usd=MISSING_TAG_COST_USD,
                            tags={tag: tags.get(tag) for tag in REQUIRED_TAGS},
                            suggested_action="tag",
                            safe_to_auto_delete=False,
                        )
                    )
    for page in paginate(ec2_client, "describe_volumes"):
        for volume in page.get("Volumes", []):
            volume_id = volume.get("VolumeId", "unknown")
            tags = tags_to_dict(volume.get("Tags"))
            missing = missing_required_tags(tags)

            if missing:
                findings.append(
                    make_finding(
                        resource_id=volume_id,
                        resource_type="ebs_volume",
                        reason=f"missing_required_tags:{','.join(missing)}",
                        age_days=calculate_age_days(volume.get("CreateTime")),
                        estimated_monthly_cost_usd=MISSING_TAG_COST_USD,
                        tags={tag: tags.get(tag) for tag in REQUIRED_TAGS},
                        suggested_action="tag",
                        safe_to_auto_delete=False,
                    )
                )
    try:
        addresses = ec2_client.describe_addresses().get("Addresses", [])
    except ClientError:
        addresses = []

    for address in addresses:
        allocation_id = address.get("AllocationId")
        public_ip = address.get("PublicIp", "unknown")
        resource_id = allocation_id or public_ip
        tags = tags_to_dict(address.get("Tags"))
        missing = missing_required_tags(tags)

        if missing:
            findings.append(
                make_finding(
                    resource_id=resource_id,
                    resource_type="elastic_ip",
                    reason=f"missing_required_tags:{','.join(missing)}",
                    age_days=0,
                    estimated_monthly_cost_usd=MISSING_TAG_COST_USD,
                    tags={tag: tags.get(tag) for tag in REQUIRED_TAGS},
                    suggested_action="tag",
                    safe_to_auto_delete=False,
                )
            )

    return findings


def delete_finding(ec2_client, finding: Finding) -> bool:
    resource_type = finding["resource_type"]
    resource_id = finding["resource_id"]
    suggested_action = finding["suggested_action"]

    try:
        if resource_type == "ebs_volume" and suggested_action == "delete":
            ec2_client.delete_volume(VolumeId=resource_id)
            return True

        if resource_type == "ec2_instance" and suggested_action == "terminate":
            ec2_client.terminate_instances(InstanceIds=[resource_id])
            return True

        if resource_type == "elastic_ip" and suggested_action == "release":
            if resource_id.startswith("eipalloc-"):
                ec2_client.release_address(AllocationId=resource_id)
            else:
                ec2_client.release_address(PublicIp=resource_id)
            return True

    except ClientError as exc:
        print(f"Warning: failed to delete {resource_type} {resource_id}: {exc}", file=sys.stderr)
        return False

    return False


def apply_deletions(ec2_client, findings: List[Finding]) -> None:
    for finding in findings:
        tags = finding.get("tags", {})

        if is_protected(tags):
            finding["delete_status"] = "skipped_protected"
            continue

        if not finding.get("safe_to_auto_delete"):
            finding["delete_status"] = "skipped_not_safe"
            continue

        deleted = delete_finding(ec2_client, finding)
        finding["delete_status"] = "deleted" if deleted else "delete_failed"


def build_report(region: str, findings: List[Finding]) -> Dict[str, Any]:
    total_waste = sum(finding["estimated_monthly_cost_usd"] for finding in findings)

    return {
        "scan_timestamp": iso_now(),
        "account_id": DEFAULT_ACCOUNT_ID,
        "region": region,
        "summary": {
            "total_orphans": len(findings),
            "estimated_monthly_waste_usd": round(total_waste, 2),
        },
        "findings": findings,
    }


def write_json_report(report: Dict[str, Any], path: str) -> None:
    with open(path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)


def write_markdown_report(report: Dict[str, Any], path: str, dry_run: bool) -> None:
    summary = report["summary"]
    findings = report["findings"]
    mode = "dry-run" if dry_run else "delete"

    lines = [
        "# Cost Janitor Report",
        "",
        f"**Scan timestamp:** {report['scan_timestamp']}",
        f"**Account ID:** {report['account_id']}",
        f"**Region:** {report['region']}",
        f"**Mode:** {mode}",
        "",
        "## Summary",
        "",
        f"- Total orphans: {summary['total_orphans']}",
        f"- Estimated monthly waste USD: ${summary['estimated_monthly_waste_usd']:.2f}",
        "",
        "## Findings",
        "",
    ]

    if not findings:
        lines.append("No orphaned or non-compliant resources found.")
    else:
        lines.extend(
            [
                "| Resource ID | Type | Reason | Age Days | Est. Monthly Cost | Suggested Action | Safe to Auto Delete |",
                "|---|---|---|---:|---:|---|---|",
            ]
        )

        for finding in findings:
            lines.append(
                "| {resource_id} | {resource_type} | {reason} | {age_days} | ${cost:.2f} | {action} | {safe} |".format(
                    resource_id=finding["resource_id"],
                    resource_type=finding["resource_type"],
                    reason=finding["reason"],
                    age_days=finding["age_days"],
                    cost=finding["estimated_monthly_cost_usd"],
                    action=finding["suggested_action"],
                    safe=finding["safe_to_auto_delete"],
                )
            )

    lines.append("")

    with open(path, "w", encoding="utf-8") as file:
        file.write("\n".join(lines))


def scan(ec2_client, stopped_days: int) -> List[Finding]:
    findings: List[Finding] = []

    findings.extend(find_unattached_ebs_volumes(ec2_client))
    findings.extend(find_stopped_ec2_instances(ec2_client, stopped_days))
    findings.extend(find_unused_elastic_ips(ec2_client))
    findings.extend(find_missing_tags(ec2_client))

    return findings


def main() -> int:
    args = parse_args()

    ec2_client = create_ec2_client(
        region=args.region,
        endpoint_url=args.endpoint_url,
    )

    findings = scan(ec2_client, args.stopped_days)

    if args.delete:
        apply_deletions(ec2_client, findings)

    report = build_report(args.region, findings)

    write_json_report(report, args.report_json)
    write_markdown_report(report, args.report_md, dry_run=args.dry_run)

    print(f"Wrote JSON report: {args.report_json}")
    print(f"Wrote Markdown report: {args.report_md}")
    print(f"Total findings: {report['summary']['total_orphans']}")
    if args.dry_run and findings:
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())