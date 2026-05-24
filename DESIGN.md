# DESIGN.md

# Cost Janitor — Production Design Considerations

## 1. Multi-cloud architecture

The current implementation focuses on AWS-compatible infrastructure using LocalStack. However, real-world FinOps environments are increasingly multi-cloud, with organizations commonly operating across AWS, GCP, and Azure simultaneously.

To support future multi-cloud expansion, the Cost Janitor should be restructured around a provider abstraction model rather than embedding AWS-specific logic directly into the core scanning engine.

### Proposed architecture

```text
                    ┌────────────────────┐
                    │  Core Scan Engine  │
                    └─────────┬──────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│  AWS Adapter   │ │  GCP Adapter   │ │ Azure Adapter  │
│ boto3/localstack│ │ google-cloud   │ │ azure-sdk      │
└────────────────┘ └────────────────┘ └────────────────┘
```

The core engine should:
- define a common finding schema
- handle reporting
- enforce policies
- generate metrics
- manage deletion workflows

Cloud-specific adapters should:
- authenticate to cloud providers
- enumerate resources
- normalize resource metadata
- return findings in a provider-independent structure

This approach reduces coupling and allows future cloud providers to be added without rewriting the core scanning logic.

---

## 2. IAM permissions

The Cost Janitor should operate under the principle of least privilege.

### Dry-run mode permissions

Dry-run mode only requires read-only access because it scans infrastructure without modifying resources.

Example required permissions:
- `ec2:DescribeInstances`
- `ec2:DescribeVolumes`
- `ec2:DescribeAddresses`
- `s3:ListAllMyBuckets`
- `s3:GetBucketTagging`

### Delete mode permissions

Delete mode additionally requires:
- `ec2:DeleteVolume`
- `ec2:TerminateInstances`
- `ec2:ReleaseAddress`

Delete permissions should be isolated into a separate IAM role with restricted usage and approval controls.

### Example minimal read-only IAM policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:DescribeVolumes",
        "ec2:DescribeAddresses",
        "s3:ListAllMyBuckets",
        "s3:GetBucketTagging"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## 3. Failure modes of auto deletion

### Failure mode 1 — Deleting temporarily stopped production systems

An EC2 instance may appear unused because it has been stopped for several days, but it may actually be part of:
- disaster recovery infrastructure
- scheduled workloads
- temporary maintenance windows

Accidental termination could create production outages or destroy recovery environments.

### Failure mode 2 — Deleting shared infrastructure resources

An unattached EBS volume may contain:
- database backups
- migration snapshots
- forensic investigation data

Naïve deletion logic based only on attachment state could cause permanent data loss.

---

## 4. Safety guardrails

Several guardrails should exist before destructive actions are allowed.

### Protected resource tagging

Resources tagged:

```text
Protected=true
```

must never be auto-deleted.

### Dry-run default

The Janitor defaults to dry-run mode to prioritize visibility before destructive automation.

### Environment restrictions

Production environments should require:
- explicit approvals
- change windows
- deletion allowlists

### Human approval workflows

Delete mode should ideally integrate with:
- GitHub approvals
- Slack approvals
- ServiceNow/Jira workflows

before executing destructive actions.

### Resource age thresholds

Deletion should only occur after configurable grace periods to reduce accidental removals.

---

## 5. Observability metrics

The following metrics should be published to CloudWatch, Prometheus, Datadog, or another monitoring platform.

| Metric | Source | Alert Threshold |
|---|---|---|
| orphan_resource_count | Janitor scan results | > 10 |
| estimated_monthly_waste_usd | Cost Janitor report | > $500 |
| deletion_failures | Delete operations | > 0 |
| scan_duration_seconds | Workflow runtime | > 300s |
| missing_tag_resources | Tag compliance checks | > 5 |

These metrics allow FinOps and platform teams to:
- track waste trends
- identify governance issues
- monitor automation health
- detect abnormal infrastructure growth

---

## 6. What I intentionally did not build

This implementation intentionally prioritizes assignment completeness, reproducibility, and safe local execution over enterprise-scale functionality.

The following items were consciously excluded:
- Multi-account AWS Organizations support
- Real AWS pricing API integration
- Parallelized resource scanning
- CloudTrail-based historical analysis
- Full unit/integration test coverage
- Kubernetes resource scanning
- Cross-region aggregation
- Real approval workflows
- Persistent databases for findings history

These features would significantly improve production readiness but were intentionally scoped out to keep the solution focused, locally reproducible, and achievable within the assignment time constraints.