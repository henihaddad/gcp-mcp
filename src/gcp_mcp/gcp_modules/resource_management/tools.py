"""
Google Cloud Platform Resource Management tools.
"""
from typing import List, Dict, Any, Optional

def register_tools(mcp):
    """Register all resource management tools with the MCP server."""
    
    @mcp.tool()
    def list_gcp_projects():
        """
        List all available GCP projects for the authenticated user.
        
        Returns:
            List of project IDs
        """
        try:
            from google.cloud import resourcemanager_v3
            client = resourcemanager_v3.ProjectsClient()
            request = resourcemanager_v3.SearchProjectsRequest()
            response = client.search_projects(request=request)
            return [project.project_id for project in response]
        except Exception as e:
            return [f"Error listing GCP projects: {str(e)}"]

    @mcp.tool()
    def get_gcp_project_details(project_id: str) -> str:
        """
        Get detailed information about a specific GCP project.
        
        Args:
            project_id: The ID of the GCP project to get details for
        
        Returns:
            Detailed information about the specified GCP project
        """
        try:
            from google.cloud import resourcemanager_v3
            
            # Initialize the Resource Manager client
            client = resourcemanager_v3.ProjectsClient()
            
            # Get the project details
            name = f"projects/{project_id}"
            project = client.get_project(name=name)
            
            # Format the response
            project_number = project.name.split('/')[-1] if project.name else "N/A"
            display_name = project.display_name or "N/A"
            create_time = project.create_time.isoformat() if project.create_time else "N/A"
            state = project.state.name if project.state else "N/A"
            
            labels = dict(project.labels) if project.labels else {}
            labels_str = "\n".join([f"  {k}: {v}" for k, v in labels.items()]) if labels else "  None"
            
            return f"""
GCP Project Details for {project_id}:
Project Number: {project_number}
Name: {display_name}
Creation Time: {create_time}
State: {state}
Labels:
{labels_str}
"""
        except Exception as e:
            return f"Error getting GCP project details: {str(e)}"

    @mcp.tool()
    def list_assets(project_id: str, asset_types: Optional[List[str]] = None, page_size: int = 50) -> str:
        """
        List assets in a GCP project using Cloud Asset Inventory API.
        
        Args:
            project_id: The ID of the GCP project to list assets for
            asset_types: Optional list of asset types to filter by (e.g., ["compute.googleapis.com/Instance"])
            page_size: Number of assets to return per page (default: 50, max: 1000)
        
        Returns:
            List of assets in the specified GCP project
        """
        try:
            try:
                from google.cloud import asset_v1
            except ImportError:
                return "Error: The Google Cloud Asset Inventory library is not installed. Please install it with 'pip install google-cloud-asset'."
            
            # Initialize the Asset client
            client = asset_v1.AssetServiceClient()
            
            # Format the parent resource
            parent = f"projects/{project_id}"
            
            # Create the request
            request = asset_v1.ListAssetsRequest(
                parent=parent,
                content_type=asset_v1.ContentType.RESOURCE,
                page_size=min(page_size, 1000)  # API limit is 1000
            )
            
            # Add asset types filter if provided
            if asset_types:
                request.asset_types = asset_types
            
            # List assets
            response = client.list_assets(request=request)
            
            # Format the response
            assets_list = []
            for asset in response:
                asset_type = asset.asset_type
                name = asset.name
                display_name = asset.display_name if hasattr(asset, 'display_name') and asset.display_name else name.split('/')[-1]
                
                # Extract location if available
                location = "global"
                if hasattr(asset.resource, 'location') and asset.resource.location:
                    location = asset.resource.location
                
                assets_list.append(f"- {display_name} ({asset_type})\n  Location: {location}\n  Name: {name}")
            
            if not assets_list:
                filter_msg = f" with types {asset_types}" if asset_types else ""
                return f"No assets found{filter_msg} in project {project_id}."
            
            # Add pagination info if there's a next page token
            pagination_info = ""
            if hasattr(response, 'next_page_token') and response.next_page_token:
                pagination_info = "\n\nMore assets are available. Refine your search or increase page_size to see more."
            
            return f"Assets in GCP Project {project_id}:\n\n" + "\n\n".join(assets_list) + pagination_info
        except Exception as e:
            return f"Error listing assets: {str(e)}"

    @mcp.tool()
    def set_quota_project(project_id: str) -> str:
        """
        Set a quota project for Google Cloud API requests.
        
        This helps resolve the warning: "Your application has authenticated using end user credentials 
        from Google Cloud SDK without a quota project."
        
        Args:
            project_id: The ID of the GCP project to use for quota attribution
        
        Returns:
            Confirmation message if successful, error message otherwise
        """
        try:
            try:
                import google.auth
                from google.auth import exceptions
                import os
            except ImportError:
                return "Error: Required libraries not installed. Please install with 'pip install google-auth'."
            
            # Set the quota project in the environment variable
            os.environ["GOOGLE_CLOUD_QUOTA_PROJECT"] = project_id
            
            # Try to get credentials with the quota project
            try:
                # Get the current credentials
                credentials, project = google.auth.default()
                
                # Set the quota project on the credentials if supported
                if hasattr(credentials, "with_quota_project"):
                    credentials = credentials.with_quota_project(project_id)
                    
                    # Save the credentials back (this depends on the credential type)
                    # This is a best-effort approach
                    try:
                        if hasattr(google.auth, "_default_credentials"):
                            google.auth._default_credentials = credentials
                    except:
                        pass
                    
                    return f"Successfully set quota project to '{project_id}'. New API requests will use this project for quota attribution."
                else:
                    return f"Set environment variable GOOGLE_CLOUD_QUOTA_PROJECT={project_id}, but your credential type doesn't support quota projects directly."
            except exceptions.GoogleAuthError as e:
                return f"Error setting quota project: {str(e)}"
        except Exception as e:
            return f"Error setting quota project: {str(e)}"