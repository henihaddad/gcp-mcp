import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the Python path so we can import the mock modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the functions to test from the mock modules
from tests.mock_gcp import (
    list_gcp_projects,
    get_gcp_project_details,
    list_gcp_services,
    list_compute_instances,
    check_iam_permissions,
    list_storage_buckets,
    get_billing_info
)


class TestGCPFunctions:
    """Test class for GCP-related functions."""

    def test_list_gcp_projects(self):
        """Test the list_gcp_projects function."""
        # Call the function
        result = list_gcp_projects()
        
        # Assertions
        assert isinstance(result, list)
        assert "test-project-1" in result
        assert "test-project-2" in result
        assert "test-project-3" in result
        assert len(result) == 3

    def test_get_gcp_project_details(self):
        """Test the get_gcp_project_details function."""
        # Call the function
        result = get_gcp_project_details("test-project-id")
        
        # Assertions
        assert isinstance(result, str)
        assert "Test Project" in result
        assert "2023-01-01T00:00:00Z" in result
        assert "ACTIVE" in result
        assert "env: test" in result
        assert "department: engineering" in result

    def test_list_gcp_services(self):
        """Test the list_gcp_services function."""
        # Call the function
        result = list_gcp_services("test-project")
        
        # Assertions
        assert isinstance(result, str)
        assert "compute.googleapis.com: Compute Engine API" in result
        assert "storage.googleapis.com: Cloud Storage API" in result
        assert "iam.googleapis.com: Identity and Access Management (IAM) API" in result

    def test_list_compute_instances_with_zone(self):
        """Test the list_compute_instances function with a specified zone."""
        # Call the function with a specified zone
        result = list_compute_instances("test-project", "us-central1-a")
        
        # Assertions
        assert isinstance(result, str)
        assert "instance-1" in result
        assert "instance-2" in result
        assert "n1-standard-1" in result
        assert "n1-standard-2" in result
        assert "RUNNING" in result
        assert "STOPPED" in result
        assert "us-central1-a" in result

    def test_check_iam_permissions(self):
        """Test the check_iam_permissions function."""
        # Call the function
        result = check_iam_permissions("test-project")
        
        # Assertions
        assert isinstance(result, str)
        assert "roles/viewer" in result
        assert "roles/editor" in result
        assert "test-user@example.com" in result

    def test_list_storage_buckets(self):
        """Test the list_storage_buckets function."""
        # Call the function
        result = list_storage_buckets("test-project")
        
        # Assertions
        assert isinstance(result, str)
        assert "test-bucket-1" in result
        assert "test-bucket-2" in result
        assert "us-central1" in result
        assert "us-east1" in result
        assert "STANDARD" in result
        assert "NEARLINE" in result
        assert "2023-01-01 00:00:00 UTC" in result
        assert "2023-02-01 00:00:00 UTC" in result

    def test_get_billing_info(self):
        """Test the get_billing_info function."""
        # Call the function
        result = get_billing_info("test-project")
        
        # Assertions
        assert isinstance(result, str)
        assert "123456-ABCDEF-123456" in result
        assert "My Billing Account" in result
        assert "Open" in result
        assert "Yes" in result  # billing_enabled
        assert "USD" in result 