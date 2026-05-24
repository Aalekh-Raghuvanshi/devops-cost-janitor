# Submission — DevOps Engineer Assignment
**Candidate name:** Aalekh Raghuvanshi

**Email:** aalekhraghuvanshi01@gmail.com

**Date submitted:** 24th May 2026

**Hours spent (approximate):** 15 - 20 hours

## Deliverables checklist
- [x] Part A: Terraform code under /terraform applies cleanly on LocalStack
- [x] Part A: `terraform validate` and `terraform fmt -check` both pass
- [x] Part B: Janitor script runs in --dry-run mode and produces report.json
- [x] Part B: GitHub Actions workflow runs green on a fresh PR
- [x] Part B: --delete mode respects Protected=true tag
- [x] Part C: DESIGN.md is present and within 2 pages
- [x] Walkthrough video link below is accessible (unlisted is fine)

## Walkthrough video
Link (Loom / YouTube unlisted / Google Drive): https://www.youtube.com/watch?v=2AI0GlkwyX4&t=1s

Length: 4 minutes

## Sample report
Sample reports are available at:

```text
samples/report.example.json
samples/report.example.md
```

## Known limitations
- LocalStack does not perfectly emulate all AWS APIs and lifecycle behaviors.
- Stopped EC2 age tracking uses LaunchTime as a simplified approximation.
- Cost estimation uses static pricing constants instead of real AWS pricing APIs.
- The implementation focuses on AWS-compatible infrastructure and does not include production-ready GCP/Azure adapters.
- Delete mode intentionally includes strong safety restrictions and is not designed for production-scale unattended cleanup workflows.
- Elastic IP simulation behavior in LocalStack may differ from real AWS in some edge cases.

## AI usage disclosure
AI tools were used during development as productivity and learning aids.

Tools used:
- ChatGPT
- GitHub Copilot

AI assistance included:
- Terraform structure guidance
- boto3 debugging support
- CI/CD workflow refinement
- Documentation review and formatting

All generated code and configurations were manually reviewed, validated, and adjusted to ensure they matched assignment requirements and actual runtime behavior.

One incorrect AI suggestion encountered during development:
- An earlier Terraform provider configuration used unsupported LocalStack endpoint behavior for newer provider versions and required manual correction after validation and runtime testing.

Critical logic, architecture decisions, debugging, and assignment alignment were verified manually.