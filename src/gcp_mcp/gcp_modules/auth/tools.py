"""
Google Cloud Platform Authentication tools.
"""
import os
import json
from typing import Dict, Any, Optional, List
import webbrowser
import tempfile
from pathlib import Path

def register_tools(mcp):
    """Register all authentication tools with the MCP server."""
    
    # Global variable to store the current project ID
    _current_project_id = None
    
    @mcp.tool()
    def auth_login(project_id: str = "") -> str:
        """
        Authenticate with Google Cloud Platform using browser-based OAuth flow.
        
        Args:
            project_id: Optional project ID to set as default after login
        
        Returns:
            Status message indicating whether authentication was successful
        """
        nonlocal _current_project_id
        
        try:
            from google.auth.transport.requests import Request
            from google.auth.exceptions import DefaultCredentialsError
            from google_auth_oauthlib.flow import InstalledAppFlow
            import google.auth
            
            # First, attempt to use existing credentials to see if we're already authenticated
            try:
                credentials, project = google.auth.default()
                
                # Test if credentials are valid
                if hasattr(credentials, 'refresh'):
                    credentials.refresh(Request())
                
                # If we get here, credentials are valid
                if project_id:
                    # Update global project ID
                    _current_project_id = project_id
                    
                    # Create a credential configuration file for the project
                    _set_project_id_in_config(project_id)
                    return f"Using existing credentials. Project set to {project_id}."
                else:
                    return f"Using existing credentials. Current project: {project or 'Not set'}"
                    
            except (DefaultCredentialsError, Exception) as e:
                # If we can't use existing credentials, proceed with login
                pass
            
            # Set up the OAuth flow
            print("Opening browser for authentication...")
            
            # Create a temporary client_secrets.json file for OAuth flow
            client_secrets = {
                "installed": {
                    "client_id": "764086051850-6qr4p6gpi6hn506pt8ejuq83di341hur.apps.googleusercontent.com",
                    "project_id": "gcp-mcp",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_secret": "d-FL95Q19q7MQmFpd7hHD0Ty",
                    "redirect_uris": ["http://localhost", "urn:ietf:wg:oauth:2.0:oob"]
                }
            }
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp:
                temp_client_secrets_path = temp.name
                json.dump(client_secrets, temp)
                
            try:
                # Create the OAuth flow
                flow = InstalledAppFlow.from_client_secrets_file(
                    temp_client_secrets_path,
                    scopes=['https://www.googleapis.com/auth/cloud-platform']
                )
                
                # Run the flow
                creds = flow.run_local_server(port=0)
                
                # Save the credentials as application default credentials
                adc_path = _get_adc_path()
                os.makedirs(os.path.dirname(adc_path), exist_ok=True)
                
                # Write credentials to ADC file
                with open(adc_path, 'w') as f:
                    creds_data = {
                        "client_id": creds.client_id,
                        "client_secret": creds.client_secret,
                        "refresh_token": creds.refresh_token,
                        "type": "authorized_user"
                    }
                    json.dump(creds_data, f)
                
                # Set project if specified
                if project_id:
                    _current_project_id = project_id
                    _set_project_id_in_config(project_id)
                
                success_msg = "Authentication successful!"
                
                if project_id:
                    success_msg += f" Default project set to {project_id}."
                
                # Test by listing accessible projects
                try:
                    from google.cloud import resourcemanager_v3
                    
                    # Get fresh credentials after login
                    credentials, _ = google.auth.default()
                    client = resourcemanager_v3.ProjectsClient(credentials=credentials)
                    request = resourcemanager_v3.ListProjectsRequest()
                    projects = list(client.list_projects(request=request))
                    
                    project_count = len(projects)
                    if project_count > 0:
                        project_list = "\n".join([f"- {project.display_name} (ID: {project.project_id})" for project in projects[:5]])
                        if project_count > 5:
                            project_list += f"\n... and {project_count - 5} more"
                        
                        success_msg += f"\n\nFound {project_count} accessible projects:\n{project_list}"
                except Exception as e:
                    # Don't fail if we can't list projects
                    pass
                
                return success_msg
            
            finally:
                # Clean up the temporary file
                try:
                    os.unlink(temp_client_secrets_path)
                except:
                    pass
                
        except Exception as e:
            return f"Authentication error: {str(e)}"
    
    @mcp.tool()
    def auth_list() -> str:
        """
        List active Google Cloud credentials.
        
        Returns:
            List of active credentials and the current default account
        """
        try:
            import google.auth
            
            # Check application default credentials
            try:
                credentials, project = google.auth.default()
                
                # Try to get email from credentials
                email = None
                if hasattr(credentials, 'service_account_email'):
                    email = credentials.service_account_email
                elif hasattr(credentials, 'refresh_token') and credentials.refresh_token:
                    # This is a user credential
                    adc_path = _get_adc_path()
                    if os.path.exists(adc_path):
                        try:
                            with open(adc_path, 'r') as f:
                                data = json.load(f)
                                if 'refresh_token' in data:
                                    # This is a user auth, but we can't get the email directly
                                    email = "User account (ADC)"
                        except:
                            pass
                
                credential_type = type(credentials).__name__
                
                output = "Active Credentials:\n"
                if email:
                    output += f"- {email} (Application Default Credentials, type: {credential_type})\n"
                else:
                    output += f"- Application Default Credentials (type: {credential_type})\n"
                
                if project:
                    output += f"\nCurrent Project: {project}\n"
                else:
                    output += "\nNo project set in default credentials.\n"
                
                # Check for other credentials in well-known locations
                credentials_dir = os.path.expanduser("~/.config/gcloud/credentials")
                if os.path.isdir(credentials_dir):
                    cred_files = [f for f in os.listdir(credentials_dir) if f.endswith('.json')]
                    if cred_files:
                        output += "\nOther available credentials:\n"
                        for cred_file in cred_files:
                            try:
                                with open(os.path.join(credentials_dir, cred_file), 'r') as f:
                                    data = json.load(f)
                                    if 'client_id' in data:
                                        output += f"- User account ({cred_file})\n"
                                    elif 'private_key_id' in data:
                                        output += f"- Service account: {data.get('client_email', 'Unknown')} ({cred_file})\n"
                            except:
                                output += f"- Unknown credential type ({cred_file})\n"
                
                return output
            except Exception as e:
                return f"No active credentials found. Please run auth_login() to authenticate.\nError: {str(e)}"
                
        except Exception as e:
            return f"Error listing credentials: {str(e)}"
    
    @mcp.tool()
    def auth_revoke() -> str:
        """
        Revoke Google Cloud credentials.
        
        Returns:
            Status message indicating whether the credentials were revoked
        """
        try:
            import google.auth
            from google.auth.transport.requests import Request
            
            # Check if we have application default credentials
            try:
                credentials, _ = google.auth.default()
                
                # If credentials have a revoke method, use it
                if hasattr(credentials, 'revoke'):
                    credentials.revoke(Request())
                
                # Remove the application default credentials file
                adc_path = _get_adc_path()
                if os.path.exists(adc_path):
                    os.remove(adc_path)
                    return "Application default credentials have been revoked and removed."
                else:
                    return "No application default credentials file found to remove."
            
            except Exception as e:
                return f"No active credentials found or failed to revoke: {str(e)}"
                
        except Exception as e:
            return f"Error revoking credentials: {str(e)}"
    
    @mcp.tool()
    def config_set_project(project_id: str) -> str:
        """
        Set the default Google Cloud project.
        
        Args:
            project_id: The ID of the project to set as default
        
        Returns:
            Status message indicating whether the project was set
        """
        nonlocal _current_project_id
        
        try:
            # Update global project ID
            _current_project_id = project_id
            
            # Create or update the config file
            _set_project_id_in_config(project_id)
            
            # Verify the project exists
            try:
                from google.cloud import resourcemanager_v3
                import google.auth
                
                credentials, _ = google.auth.default()
                client = resourcemanager_v3.ProjectsClient(credentials=credentials)
                name = f"projects/{project_id}"
                
                try:
                    project = client.get_project(name=name)
                    return f"Default project set to {project_id} ({project.display_name})."
                except Exception:
                    # Project might not exist or user might not have access
                    return f"Default project set to {project_id}. Note: Could not verify if this project exists or if you have access to it."
            
            except Exception as e:
                # Don't fail if we can't verify the project
                return f"Default project set to {project_id}."
                
        except Exception as e:
            return f"Error setting project: {str(e)}"
            
    @mcp.tool()
    def config_list() -> str:
        """
        List the current Google Cloud configuration.
        
        Returns:
            Current configuration settings
        """
        try:
            # Get project ID from config
            project_id = _get_project_id_from_config()
            
            # Get project ID from global variable if set
            if _current_project_id:
                project_id = _current_project_id
            
            output = "Current Configuration:\n"
            
            if project_id:
                output += f"- Project ID: {project_id}\n"
            else:
                output += "- Project ID: Not set\n"
            
            # Check if we have active credentials
            try:
                import google.auth
                
                credentials, default_project = google.auth.default()
                
                if hasattr(credentials, 'service_account_email'):
                    output += f"- Authenticated as: {credentials.service_account_email} (Service Account)\n"
                else:
                    output += "- Authenticated as: User Account\n"
                
                if default_project and default_project != project_id:
                    output += f"- Default Project in Credentials: {default_project}\n"
            except Exception:
                output += "- Authentication: Not authenticated or credentials not found\n"
            
            # Get additional configuration
            config_file = os.path.join(_get_config_path(), 'configurations', 'config_default')
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r') as f:
                        config_lines = f.readlines()
                    
                    if config_lines:
                        output += "\nAdditional Configuration Settings:\n"
                        for line in config_lines:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                key, value = line.split('=', 1)
                                key = key.strip()
                                value = value.strip()
                                
                                # Skip project since we already displayed it
                                if key != 'project':
                                    output += f"- {key}: {value}\n"
                except:
                    pass
            
            return output
            
        except Exception as e:
            return f"Error listing configuration: {str(e)}"
    
    # Helper functions
    def _get_adc_path() -> str:
        """Get the path to the application default credentials file."""
        # Standard ADC paths by platform
        if os.name == 'nt':  # Windows
            return os.path.join(os.environ.get('APPDATA', ''), 'gcloud', 'application_default_credentials.json')
        else:  # Linux/Mac
            return os.path.expanduser('~/.config/gcloud/application_default_credentials.json')
    
    def _get_config_path() -> str:
        """Get the path to the configuration directory."""
        if os.name == 'nt':  # Windows
            return os.path.join(os.environ.get('APPDATA', ''), 'gcloud')
        else:  # Linux/Mac
            return os.path.expanduser('~/.config/gcloud')
            
    def _set_project_id_in_config(project_id: str) -> None:
        """Set the project ID in the configuration file."""
        config_dir = _get_config_path()
        os.makedirs(config_dir, exist_ok=True)
        
        config_file = os.path.join(config_dir, 'configurations', 'config_default')
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        # Read existing config if it exists
        config_data = {}
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            config_data[key.strip()] = value.strip()
            except:
                pass
        
        # Update project
        config_data['project'] = project_id
        
        # Write back config
        with open(config_file, 'w') as f:
            for key, value in config_data.items():
                f.write(f"{key} = {value}\n")
    
    def _get_project_id_from_config() -> Optional[str]:
        """Get the project ID from the configuration file."""
        config_file = os.path.join(_get_config_path(), 'configurations', 'config_default')
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    for line in f:
                        if line.strip().startswith('project ='):
                            return line.split('=', 1)[1].strip()
            except:
                pass
        
        return None