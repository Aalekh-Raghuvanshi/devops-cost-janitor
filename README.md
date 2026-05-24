# NimbusKart Cost Hygiene & Automation

## Overview

This repository contains a local-first DevOps and FinOps automation solution built for the Code & Conscience DevOps Engineer assignment. The project provisions a simulated AWS environment using Terraform and LocalStack, then runs a Python-based “Cost Janitor” automation tool that detects orphaned and non-compliant cloud resources.

The goal of the project is to demonstrate practical Infrastructure-as-Code, cloud cost governance, automation safety, and CI/CD integration without requiring a real AWS account or generating cloud charges.

The solution includes:
- Terraform infrastructure provisioning
- Reusable Terraform network module
- LocalStack-based AWS simulation
- Python boto3 automation
- Cost hygiene reporting
- GitHub Actions CI/CD workflow
- Automated PR feedback through Markdown reporting

---

## How to run locally

### Prerequisites

Install the following tools:

- Docker
- Python 3.10+
- Terraform
- AWS CLI
- pip

---

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd <YOUR_REPOSITORY_NAME>
```

---

### 2. Start LocalStack

```bash
docker run --rm -d \
  --name localstack-main \
  -p 4566:4566 \
  -e DEBUG=1 \
  -e SERVICES=ec2,s3 \
  -e AWS_DEFAULT_REGION=us-east-1 \
  localstack/localstack:3.0
```

Verify LocalStack health:

```bash
curl http://localhost:4566/_localstack/health
```

---

### 3. Configure local AWS environment variables

```bash
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1
```

---

### 4. Install Terraform Local wrapper

```bash
pip install terraform-local
```

---

### 5. Apply Terraform infrastructure

```bash
cd terraform

terraform init
terraform fmt -recursive
terraform validate

tflocal init
tflocal apply -auto-approve
```

This creates:
- VPC
- public subnets
- security group
- EC2 instances
- S3 bucket
- unattached EBS volume

against LocalStack instead of real AWS.

---

### 6. Install Python dependencies

```bash
cd ../janitor

pip install -r requirements.txt
```

---

### 7. Run Cost Janitor in dry-run mode

```bash
python janitor.py --dry-run
```

Expected outputs:
- `report.json`
- `report.md`

The script exits with a non-zero exit code if orphaned resources are detected.

---

### 8. Run Cost Janitor in delete mode

```bash
python janitor.py --delete
```

Resources tagged:

```text
Protected=true
```

are skipped automatically.

---

### 9. Destroy infrastructure

```bash
cd ../terraform

tflocal destroy -auto-approve
```

---

## Architecture

```text
                        ┌────────────────────┐
                        │   GitHub Actions   │
                        │   CI/CD Workflow   │
                        └─────────┬──────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │     LocalStack AWS      │
                    │  (Fake AWS APIs Local)  │
                    └─────────┬───────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│   Terraform    │  │     boto3      │  │   AWS CLI      │
│ Infrastructure │  │ Cost Janitor   │  │ Manual Testing │
└────────┬───────┘  └────────┬───────┘  └────────────────┘
         │                   │
         ▼                   ▼
┌─────────────────────────────────────────────┐
│         Simulated AWS Resources             │
│                                             │
│ - VPC                                       │
│ - Public Subnets                            │
│ - EC2 Instances                             │
│ - Security Groups                           │
│ - S3 Bucket + Versioning                    │
│ - Unattached EBS Volume                     │
│ - Elastic IPs                               │
└─────────────────────────────────────────────┘
                              │
                              ▼
                 ┌──────────────────────────┐
                 │ report.json / report.md  │
                 └──────────────────────────┘
```

### GitHub Actions workflow

The GitHub Actions pipeline performs the following:

1. Starts LocalStack as a service container
2. Applies Terraform infrastructure
3. Runs the Cost Janitor in dry-run mode
4. Uploads reports as workflow artifacts
5. Posts Markdown findings as a PR comment
6. Fails CI if orphaned resources are detected

This simulates automated cloud governance and FinOps enforcement in CI/CD pipelines.

---

## Decisions & deviations

- SSH access from `0.0.0.0/0` was implemented because it was explicitly required by the assignment, but this is not production-safe and should be restricted to trusted CIDRs, VPNs, bastion hosts, or AWS Systems Manager in real environments.
- LocalStack was used instead of real AWS to ensure zero-cost reproducibility and deterministic local testing.
- The Cost Janitor defaults to `--dry-run` mode to reduce accidental destructive actions during development and CI execution.
- Stopped EC2 age detection uses `LaunchTime` as a simplified proxy because LocalStack does not fully emulate historical EC2 state transition metadata.
- Cost estimates use static pricing constants for deterministic offline evaluation instead of querying real AWS pricing APIs.
- Elastic IP handling is simplified because LocalStack networking behavior differs from real AWS in some edge cases.
- Terraform modules were intentionally separated even though the infrastructure size is small to demonstrate reusable Infrastructure-as-Code patterns.

---

## Trade-offs

This implementation prioritizes clarity, reproducibility, and assignment completeness over production-scale complexity.

With additional time, I would improve:
- Multi-region scanning support
- Multi-account AWS Organizations support
- Real AWS pricing integration using CUR/Athena or AWS Pricing APIs
- Parallelized resource scanning for large environments
- Structured logging and observability
- CloudWatch/OpenTelemetry metrics
- Better stopped-instance age tracking using CloudTrail or AWS Config
- Safer approval workflows before destructive actions
- Unit and integration testing coverage using Moto
- Support for GCP and Azure resource scanners through provider abstraction

The current implementation intentionally focuses on correctness, local reproducibility, and CI/CD integration rather than enterprise-scale optimization.

---

## AI usage disclosure

AI tools were used during the development of this assignment.

Tools used:
- ChatGPT for Terraform structure guidance, boto3 debugging assistance, CI/CD workflow refinement, and documentation review.
- GitHub Copilot for boilerplate generation and repetitive syntax completion.

One incorrect AI suggestion:
- An earlier AI-generated Terraform provider configuration used unsupported LocalStack endpoint behavior for newer AWS provider versions. This was identified during `terraform validate` and LocalStack connectivity testing and corrected manually.

Sections implemented manually:
- The Cost Janitor orphan detection logic and report flow were reviewed and refined manually to ensure the implementation matched the assignment schema and safety requirements exactly.
- The “Decisions & deviations” section was written manually to reflect actual engineering judgment rather than generic AI-generated responses.
