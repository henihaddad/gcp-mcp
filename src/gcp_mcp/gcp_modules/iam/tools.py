"""
Google Cloud Platform IAM tools.
"""
from typing import List, Dict, Any, Optional

def register_tools(mcp):
    """Register all IAM tools with the MCP server."""
    
    @mcp.tool()
    def check_iam_permissions(project_id: str) -> str:
        """
        Check IAM permissions for the current user in a GCP project.
        
        Args:
            project_id: The ID of the GCP project to check permissions for
        
        Returns:
            List of IAM permissions for the current user in the specified GCP project
        """
        try:
            from google.cloud import resourcemanager_v3
            from google.iam.v1 import iam_policy_pb2
            
            # Initialize the Resource Manager client
            client = resourcemanager_v3.ProjectsClient()
            
            # Get the IAM policy for the project
            request = iam_policy_pb2.GetIamPolicyRequest(
                resource=f"projects/{project_id}"
            )
            policy = client.get_iam_policy(request=request)
            
            # Get the current user
            import google.auth
            credentials, _ = google.auth.default()
            user = credentials.service_account_email if hasattr(credentials, 'service_account_email') else "current user"
            
            # Check which roles the user has
            user_bindings = []
            for binding in policy.bindings:
                role = binding.role
                members = binding.members
                
                # Check if the current user is in the members list
                for member in members:
                    if member == f"user:{user}" or member == "serviceAccount:{user}" or member == "allUsers" or member == "allAuthenticatedUsers":
                        user_bindings.append(f"- {role}")
                        break
            
            if not user_bindings:
                return f"No explicit IAM permissions found for {user} in project {project_id}."
            
            user_bindings_str = "\n".join(user_bindings)
            
            return f"""
IAM Permissions for {user} in GCP Project {project_id}:
{user_bindings_str}
"""
        except Exception as e:
            return f"Error checking IAM permissions: {str(e)}"
    
    @mcp.tool()
    def list_roles(project_id: Optional[str] = None) -> str:
        """
        List IAM roles (predefined or custom).
        
        Args:
            project_id: Optional project ID for listing custom roles. If not provided, lists predefined roles.
        
        Returns:
            List of IAM roles
        """
        try:
            from google.cloud import iam_v1
            
            # Initialize the IAM client
            client = iam_v1.IAMClient()
            
            roles_list = []
            
            if project_id:
                # List custom roles for the project
                request = iam_v1.ListRolesRequest(
                    parent=f"projects/{project_id}",
                    view=iam_v1.ListRolesRequest.RoleView.FULL
                )
                roles = client.list_roles(request=request)
                
                for role in roles:
                    description = role.description or "No description"
                    roles_list.append(f"- {role.name} - {description}")
                
                if not roles_list:
                    return f"No custom IAM roles found in project {project_id}."
                
                return f"""
Custom IAM Roles in GCP Project {project_id}:
{chr(10).join(roles_list)}
"""
            else:
                # List predefined roles
                request = iam_v1.ListRolesRequest(
                    view=iam_v1.ListRolesRequest.RoleView.BASIC
                )
                roles = client.list_roles(request=request)
                
                for role in roles:
                    if role.name.startswith("roles/"):
                        description = role.description or "No description"
                        roles_list.append(f"- {role.name} - {description}")
                
                if not roles_list:
                    return "No predefined IAM roles found."
                
                return f"""
Predefined IAM Roles in GCP:
{chr(10).join(roles_list[:100])}
(Limited to 100 roles. To see more specific roles, narrow your search criteria.)
"""
        except Exception as e:
            return f"Error listing IAM roles: {str(e)}"
    
    @mcp.tool()
    def get_role_permissions(role_name: str, project_id: Optional[str] = None) -> str:
        """
        Get detailed information about an IAM role, including its permissions.
        
        Args:
            role_name: The name of the role (e.g., "roles/compute.admin" or "projects/my-project/roles/myCustomRole")
            project_id: Optional project ID for custom roles. Not needed if role_name is fully qualified.
        
        Returns:
            Detailed information about the IAM role
        """
        try:
            from google.cloud import iam_v1
            
            # Initialize the IAM client
            client = iam_v1.IAMClient()
            
            # If project_id is provided and role_name doesn't include it, create fully qualified role name
            if project_id and not role_name.startswith("projects/") and not role_name.startswith("roles/"):
                role_name = f"projects/{project_id}/roles/{role_name}"
            elif not role_name.startswith("projects/") and not role_name.startswith("roles/"):
                role_name = f"roles/{role_name}"
            
            # Get role details
            request = iam_v1.GetRoleRequest(name=role_name)
            role = client.get_role(request=request)
            
            details = []
            details.append(f"Name: {role.name}")
            details.append(f"Title: {role.title}")
            details.append(f"Description: {role.description or 'No description'}")
            
            if role.included_permissions:
                permissions_str = "\n".join([f"- {permission}" for permission in role.included_permissions])
                details.append(f"Permissions ({len(role.included_permissions)}):\n{permissions_str}")
            else:
                details.append("Permissions: None")
            
            if hasattr(role, 'stage'):
                details.append(f"Stage: {role.stage}")
            
            if hasattr(role, 'etag'):
                details.append(f"ETag: {role.etag}")
            
            return f"""
IAM Role Details for {role.name}:
{chr(10).join(details)}
"""
        except Exception as e:
            return f"Error getting role permissions: {str(e)}"
    
    @mcp.tool()
    def list_service_accounts(project_id: str) -> str:
        """
        List service accounts in a GCP project.
        
        Args:
            project_id: The ID of the GCP project
        
        Returns:
            List of service accounts in the project
        """
        try:
            from google.cloud import iam_v1
            
            # Initialize the IAM client
            client = iam_v1.IAMClient()
            
            # List service accounts
            request = iam_v1.ListServiceAccountsRequest(
                name=f"projects/{project_id}"
            )
            service_accounts = client.list_service_accounts(request=request)
            
            accounts_list = []
            for account in service_accounts:
                display_name = account.display_name or "No display name"
                accounts_list.append(f"- {account.email} ({display_name})")
            
            if not accounts_list:
                return f"No service accounts found in project {project_id}."
            
            accounts_str = "\n".join(accounts_list)
            
            return f"""
Service Accounts in GCP Project {project_id}:
{accounts_str}
"""
        except Exception as e:
            return f"Error listing service accounts: {str(e)}"
    
    @mcp.tool()
    def create_service_account(project_id: str, account_id: str, display_name: str, description: Optional[str] = None) -> str:
        """
        Create a new service account in a GCP project.
        
        Args:
            project_id: The ID of the GCP project
            account_id: The ID for the service account (must be between 6 and 30 characters)
            display_name: A user-friendly name for the service account
            description: Optional description for the service account
        
        Returns:
            Result of the service account creation
        """
        try:
            from google.cloud import iam_v1
            
            # Initialize the IAM client
            client = iam_v1.IAMClient()
            
            # Create service account
            request = iam_v1.CreateServiceAccountRequest(
                name=f"projects/{project_id}",
                account_id=account_id,
                service_account=iam_v1.ServiceAccount(
                    display_name=display_name,
                    description=description
                )
            )
            service_account = client.create_service_account(request=request)
            
            return f"""
Service Account created successfully:
- Email: {service_account.email}
- Name: {service_account.name}
- Display Name: {service_account.display_name}
- Description: {service_account.description or 'None'}
"""
        except Exception as e:
            return f"Error creating service account: {str(e)}"
    
    @mcp.tool()
    def add_iam_policy_binding(project_id: str, role: str, member: str) -> str:
        """
        Add an IAM policy binding to a GCP project.
        
        Args:
            project_id: The ID of the GCP project
            role: The role to grant (e.g., "roles/compute.admin")
            member: The member to grant the role to (e.g., "user:email@example.com", "serviceAccount:name@project.iam.gserviceaccount.com")
        
        Returns:
            Result of the policy binding operation
        """
        try:
            from google.cloud import resourcemanager_v3
            from google.iam.v1 import iam_policy_pb2, policy_pb2
            
            # Initialize the Resource Manager client
            client = resourcemanager_v3.ProjectsClient()
            
            # Get the current IAM policy
            get_request = iam_policy_pb2.GetIamPolicyRequest(
                resource=f"projects/{project_id}"
            )
            policy = client.get_iam_policy(request=get_request)
            
            # Check if the binding already exists
            binding_exists = False
            for binding in policy.bindings:
                if binding.role == role and member in binding.members:
                    binding_exists = True
                    break
            
            if binding_exists:
                return f"IAM policy binding already exists: {member} already has role {role} in project {project_id}."
            
            # Add the new binding
            binding = policy_pb2.Binding()
            binding.role = role
            binding.members.append(member)
            policy.bindings.append(binding)
            
            # Set the updated IAM policy
            set_request = iam_policy_pb2.SetIamPolicyRequest(
                resource=f"projects/{project_id}",
                policy=policy
            )
            updated_policy = client.set_iam_policy(request=set_request)
            
            return f"""
IAM policy binding added successfully:
- Project: {project_id}
- Role: {role}
- Member: {member}
"""
        except Exception as e:
            return f"Error adding IAM policy binding: {str(e)}"