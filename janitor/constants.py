"""
Constants for the Cost Janitor.

Pricing values are simplified static estimates for assignment/demo purposes.
In production, use AWS Pricing API or CUR/Athena-based cost data.
"""

REQUIRED_TAGS = ["Project", "Environment", "Owner"]

DEFAULT_REGION = "us-east-1"
DEFAULT_ACCOUNT_ID = "000000000000"
DEFAULT_STOPPED_DAYS = 14
DEFAULT_ENDPOINT_URL = "http://localhost:4566"

REPORT_JSON_PATH = "report.json"
REPORT_MARKDOWN_PATH = "report.md"

# Static monthly cost estimates.
# Source to cite in README/DESIGN:
# AWS EBS pricing example: gp3/gp2 storage is commonly priced per GB-month.
# For assignment simplicity, this uses $0.08 per GB-month as suggested in the brief.
EBS_GB_MONTH_USD = 0.08

# Simplified estimate for stopped EC2 waste.
# Stopped EC2 compute is not billed, but attached EBS volumes and public IPs may still cost money.
STOPPED_EC2_MONTHLY_ESTIMATE_USD = 3.00

# Simplified estimate for idle Elastic IP.
UNUSED_EIP_MONTHLY_ESTIMATE_USD = 3.60

# Missing tags do not directly cost money, but create governance and cleanup risk.
MISSING_TAG_COST_USD = 0.00