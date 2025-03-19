"""
Mock functions for testing GCP functionality.
"""

def list_gcp_projects():
    """Mock function to list GCP projects."""
    return ["test-project-1", "test-project-2", "test-project-3"]

def get_gcp_project_details(project_id):
    """Mock function to get details of a GCP project."""
    return f"""
Project ID: {project_id}
Name: Test Project
Created: 2023-01-01T00:00:00Z
Status: ACTIVE
Labels:
  - env: test
  - department: engineering
"""

def list_gcp_services(project_id):
    """Mock function to list enabled services in a GCP project."""
    return f"""
Enabled services in project {project_id}:
  - compute.googleapis.com: Compute Engine API
  - storage.googleapis.com: Cloud Storage API
  - iam.googleapis.com: Identity and Access Management (IAM) API
"""

def list_compute_instances(project_id, zone=None):
    """Mock function to list Compute Engine instances."""
    zone_str = f" in zone {zone}" if zone else ""
    return f"""
Compute Engine instances in project {project_id}{zone_str}:
  - instance-1 (n1-standard-1): RUNNING
    Zone: us-central1-a
    Created: 2023-01-01 00:00:00 UTC
    
  - instance-2 (n1-standard-2): STOPPED
    Zone: us-central1-a
    Created: 2023-02-01 00:00:00 UTC
"""

def check_iam_permissions(project_id):
    """Mock function to check IAM permissions in a GCP project."""
    return f"""
IAM permissions in project {project_id}:
  - roles/viewer: test-user@example.com
  - roles/editor: test-user@example.com
"""

def list_storage_buckets(project_id):
    """Mock function to list Cloud Storage buckets in a GCP project."""
    return f"""
Cloud Storage buckets in project {project_id}:
  - test-bucket-1
    Location: us-central1
    Storage class: STANDARD
    Created: 2023-01-01 00:00:00 UTC
    
  - test-bucket-2
    Location: us-east1
    Storage class: NEARLINE
    Created: 2023-02-01 00:00:00 UTC
"""

def get_billing_info(project_id):
    """Mock function to get billing information for a GCP project."""
    return f"""
Billing information for project {project_id}:
  - Billing account: 123456-ABCDEF-123456
  - Billing account name: My Billing Account
  - Billing account status: Open
  - Billing enabled: Yes
  - Currency: USD
""" 