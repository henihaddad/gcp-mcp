"""
Google Cloud Platform Database tools.
"""
from typing import List, Dict, Any, Optional

def register_tools(mcp):
    """Register all database tools with the MCP server."""
    
    @mcp.tool()
    def list_cloud_sql_instances(project_id: str) -> str:
        """
        List Cloud SQL instances in a GCP project.
        
        Args:
            project_id: The ID of the GCP project to list Cloud SQL instances for
        
        Returns:
            List of Cloud SQL instances in the specified GCP project
        """
        try:
            from googleapiclient import discovery
            
            # Initialize the Cloud SQL Admin API client
            service = discovery.build('sqladmin', 'v1')
            
            # List SQL instances
            request = service.instances().list(project=project_id)
            response = request.execute()
            
            # Format the response
            instances_list = []
            
            if 'items' in response:
                for instance in response['items']:
                    name = instance.get('name', 'Unknown')
                    db_version = instance.get('databaseVersion', 'Unknown')
                    state = instance.get('state', 'Unknown')
                    region = instance.get('region', 'Unknown')
                    tier = instance.get('settings', {}).get('tier', 'Unknown')
                    storage_size = instance.get('settings', {}).get('dataDiskSizeGb', 'Unknown')
                    
                    instances_list.append(f"- {name} (Type: {db_version}, Region: {region}, Tier: {tier}, Storage: {storage_size}GB, State: {state})")
            
            if not instances_list:
                return f"No Cloud SQL instances found in project {project_id}."
            
            instances_str = "\n".join(instances_list)
            
            return f"""
Cloud SQL Instances in GCP Project {project_id}:
{instances_str}
"""
        except Exception as e:
            return f"Error listing Cloud SQL instances: {str(e)}"
    
    @mcp.tool()
    def get_sql_instance_details(project_id: str, instance_id: str) -> str:
        """
        Get detailed information about a specific Cloud SQL instance.
        
        Args:
            project_id: The ID of the GCP project
            instance_id: The ID of the Cloud SQL instance
        
        Returns:
            Detailed information about the specified Cloud SQL instance
        """
        try:
            from googleapiclient import discovery
            
            # Initialize the Cloud SQL Admin API client
            service = discovery.build('sqladmin', 'v1')
            
            # Get instance details
            request = service.instances().get(project=project_id, instance=instance_id)
            instance = request.execute()
            
            # Format the response
            details = []
            details.append(f"Name: {instance.get('name', 'Unknown')}")
            details.append(f"Self Link: {instance.get('selfLink', 'Unknown')}")
            details.append(f"Database Version: {instance.get('databaseVersion', 'Unknown')}")
            details.append(f"State: {instance.get('state', 'Unknown')}")
            details.append(f"Region: {instance.get('region', 'Unknown')}")
            
            # Settings information
            if 'settings' in instance:
                settings = instance['settings']
                details.append(f"Tier: {settings.get('tier', 'Unknown')}")
                details.append(f"Storage Size: {settings.get('dataDiskSizeGb', 'Unknown')}GB")
                details.append(f"Availability Type: {settings.get('availabilityType', 'Unknown')}")
                
                # Backup configuration
                if 'backupConfiguration' in settings:
                    backup = settings['backupConfiguration']
                    enabled = backup.get('enabled', False)
                    details.append(f"Automated Backups: {'Enabled' if enabled else 'Disabled'}")
                    if enabled:
                        details.append(f"Backup Start Time: {backup.get('startTime', 'Unknown')}")
                        details.append(f"Binary Log Enabled: {backup.get('binaryLogEnabled', False)}")
                
                # IP configuration
                if 'ipConfiguration' in settings:
                    ip_config = settings['ipConfiguration']
                    public_ip = "Enabled" if not ip_config.get('privateNetwork') else "Disabled"
                    details.append(f"Public IP: {public_ip}")
                    
                    if 'authorizedNetworks' in ip_config:
                        networks = []
                        for network in ip_config['authorizedNetworks']:
                            name = network.get('name', 'Unnamed')
                            value = network.get('value', 'Unknown')
                            networks.append(f"    - {name}: {value}")
                        
                        if networks:
                            details.append("Authorized Networks:")
                            details.extend(networks)
            
            # IP Addresses
            if 'ipAddresses' in instance:
                ip_addresses = []
                for ip in instance['ipAddresses']:
                    ip_type = ip.get('type', 'Unknown')
                    ip_address = ip.get('ipAddress', 'Unknown')
                    ip_addresses.append(f"    - {ip_type}: {ip_address}")
                
                if ip_addresses:
                    details.append("IP Addresses:")
                    details.extend(ip_addresses)
            
            details_str = "\n".join(details)
            
            return f"""
Cloud SQL Instance Details:
{details_str}
"""
        except Exception as e:
            return f"Error getting SQL instance details: {str(e)}"
    
    @mcp.tool()
    def list_databases(project_id: str, instance_id: str) -> str:
        """
        List databases in a Cloud SQL instance.
        
        Args:
            project_id: The ID of the GCP project
            instance_id: The ID of the Cloud SQL instance
        
        Returns:
            List of databases in the specified Cloud SQL instance
        """
        try:
            from googleapiclient import discovery
            
            # Initialize the Cloud SQL Admin API client
            service = discovery.build('sqladmin', 'v1')
            
            # List databases
            request = service.databases().list(project=project_id, instance=instance_id)
            response = request.execute()
            
            # Format the response
            databases_list = []
            
            if 'items' in response:
                for database in response['items']:
                    name = database.get('name', 'Unknown')
                    charset = database.get('charset', 'Unknown')
                    collation = database.get('collation', 'Unknown')
                    
                    databases_list.append(f"- {name} (Charset: {charset}, Collation: {collation})")
            
            if not databases_list:
                return f"No databases found in Cloud SQL instance {instance_id}."
            
            databases_str = "\n".join(databases_list)
            
            return f"""
Databases in Cloud SQL Instance {instance_id}:
{databases_str}
"""
        except Exception as e:
            return f"Error listing databases: {str(e)}"
    
    @mcp.tool()
    def create_backup(project_id: str, instance_id: str, description: Optional[str] = None) -> str:
        """
        Create a backup for a Cloud SQL instance.
        
        Args:
            project_id: The ID of the GCP project
            instance_id: The ID of the Cloud SQL instance
            description: Optional description for the backup
        
        Returns:
            Result of the backup operation
        """
        try:
            from googleapiclient import discovery
            
            # Initialize the Cloud SQL Admin API client
            service = discovery.build('sqladmin', 'v1')
            
            # Create backup
            backup_run_body = {}
            if description:
                backup_run_body['description'] = description
            
            request = service.backupRuns().insert(project=project_id, instance=instance_id, body=backup_run_body)
            operation = request.execute()
            
            # Get operation ID and status
            operation_id = operation.get('name', 'Unknown')
            status = operation.get('status', 'Unknown')
            
            return f"""
Backup operation initiated:
- Instance: {instance_id}
- Project: {project_id}
- Description: {description or 'None provided'}

Operation ID: {operation_id}
Status: {status}

The backup process may take some time to complete. You can check the status of the backup using the Cloud SQL Admin API or Google Cloud Console.
"""
        except Exception as e:
            return f"Error creating backup: {str(e)}"
    
    @mcp.tool()
    def list_firestore_databases(project_id: str) -> str:
        """
        List Firestore databases in a GCP project.
        
        Args:
            project_id: The ID of the GCP project to list Firestore databases for
        
        Returns:
            List of Firestore databases in the specified GCP project
        """
        try:
            from google.cloud import firestore_admin_v1
            
            # Initialize the Firestore Admin client
            client = firestore_admin_v1.FirestoreAdminClient()
            
            # List databases
            parent = f"projects/{project_id}"
            databases = client.list_databases(parent=parent)
            
            # Format the response
            databases_list = []
            
            for database in databases:
                name = database.name.split('/')[-1]
                db_type = "Firestore Native" if database.type_ == firestore_admin_v1.Database.DatabaseType.FIRESTORE_NATIVE else "Datastore Mode"
                location = database.location_id
                
                databases_list.append(f"- {name} (Type: {db_type}, Location: {location})")
            
            if not databases_list:
                return f"No Firestore databases found in project {project_id}."
            
            databases_str = "\n".join(databases_list)
            
            return f"""
Firestore Databases in GCP Project {project_id}:
{databases_str}
"""
        except Exception as e:
            return f"Error listing Firestore databases: {str(e)}"
    
    @mcp.tool()
    def list_firestore_collections(project_id: str, database_id: str = "(default)") -> str:
        """
        List collections in a Firestore database.
        
        Args:
            project_id: The ID of the GCP project
            database_id: The ID of the Firestore database (default is "(default)")
        
        Returns:
            List of collections in the specified Firestore database
        """
        try:
            from google.cloud import firestore
            
            # Initialize the Firestore client
            client = firestore.Client(project=project_id, database=database_id)
            
            # List collections
            collections = client.collections()
            
            # Format the response
            collections_list = []
            
            for collection in collections:
                collections_list.append(f"- {collection.id}")
            
            if not collections_list:
                return f"No collections found in Firestore database {database_id}."
            
            collections_str = "\n".join(collections_list)
            
            return f"""
Collections in Firestore Database {database_id} (Project: {project_id}):
{collections_str}
"""
        except Exception as e:
            return f"Error listing Firestore collections: {str(e)}"