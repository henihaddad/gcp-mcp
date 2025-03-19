"""
Google Cloud Platform Billing tools.
"""
from typing import List, Dict, Any, Optional

def register_tools(mcp):
    """Register all billing tools with the MCP server."""
    
    @mcp.tool()
    def get_billing_info(project_id: str) -> str:
        """
        Get billing information for a GCP project.
        
        Args:
            project_id: The ID of the GCP project to get billing information for
        
        Returns:
            Billing information for the specified GCP project
        """
        try:
            try:
                from google.cloud import billing_v1
            except ImportError:
                return "Error: The Google Cloud billing library is not installed. Please install it with 'pip install google-cloud-billing'."
            
            # Initialize the Cloud Billing client
            billing_client = billing_v1.CloudBillingClient()
            
            # Get the billing account for the project
            project_name = f"projects/{project_id}"
            billing_info = billing_client.get_project_billing_info(name=project_name)
            
            # If billing is enabled, get more details about the billing account
            if billing_info.billing_account_name:
                billing_account = billing_client.get_billing_account(
                    name=billing_info.billing_account_name
                )
                
                # Initialize the Cloud Catalog client to get pricing information
                catalog_client = billing_v1.CloudCatalogClient()
                
                # Format the response
                return f"""
Billing Information for GCP Project {project_id}:

Billing Enabled: {billing_info.billing_enabled}
Billing Account: {billing_info.billing_account_name}
Display Name: {billing_account.display_name}
Open: {billing_account.open}
"""
            else:
                return f"Billing is not enabled for project {project_id}."
        except Exception as e:
            return f"Error getting billing information: {str(e)}"