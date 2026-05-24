# Cost Janitor Report

**Scan timestamp:** 2026-01-15T10:00:00Z  
**Account ID:** 000000000000  
**Region:** us-east-1  
**Mode:** dry-run

## Summary

- Total orphans: 4
- Estimated monthly waste USD: $17.60

## Findings

| Resource ID | Type | Reason | Age Days | Est. Monthly Cost | Suggested Action | Safe to Auto Delete |
|---|---|---|---:|---:|---|---|
| vol-0abc123def4567890 | ebs_volume | unattached | 21 | $8.00 | delete | true |
| i-0123456789abcdef0 | ec2_instance | stopped_more_than_14_days | 18 | $3.00 | terminate | true |
| eipalloc-0a1b2c3d4e5f67890 | elastic_ip | unassociated | 9 | $3.60 | release | true |
| vol-0987654321fedcba0 | ebs_volume | missing_required_tags:Environment,Owner | 12 | $3.00 | tag | false |