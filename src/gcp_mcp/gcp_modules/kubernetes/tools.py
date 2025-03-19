"""
Google Cloud Platform Kubernetes Engine (GKE) tools.
"""
from typing import List, Dict, Any, Optional

def register_tools(mcp):
    """Register all kubernetes tools with the MCP server."""
    
    @mcp.tool()
    def list_gke_clusters(project_id: str, region: str = "") -> str:
        """
        List Google Kubernetes Engine (GKE) clusters in a GCP project.
        
        Args:
            project_id: The ID of the GCP project to list GKE clusters for
            region: Optional region to filter clusters (e.g., "us-central1")
        
        Returns:
            List of GKE clusters in the specified GCP project
        """
        try:
            from google.cloud import container_v1
            
            # Initialize the GKE client
            client = container_v1.ClusterManagerClient()
            
            clusters_list = []
            
            if region:
                # List clusters in the specified region
                parent = f"projects/{project_id}/locations/{region}"
                response = client.list_clusters(parent=parent)
                
                for cluster in response.clusters:
                    version = cluster.current_master_version
                    node_count = sum(pool.initial_node_count for pool in cluster.node_pools)
                    status = "Running" if cluster.status == container_v1.Cluster.Status.RUNNING else cluster.status.name
                    clusters_list.append(f"- {cluster.name} (Region: {region}, Version: {version}, Nodes: {node_count}, Status: {status})")
            else:
                # List clusters in all regions
                from google.cloud import compute_v1
                
                # Get all regions
                regions_client = compute_v1.RegionsClient()
                regions_request = compute_v1.ListRegionsRequest(project=project_id)
                regions = regions_client.list(request=regions_request)
                
                for region_item in regions:
                    region_name = region_item.name
                    parent = f"projects/{project_id}/locations/{region_name}"
                    try:
                        response = client.list_clusters(parent=parent)
                        
                        for cluster in response.clusters:
                            version = cluster.current_master_version
                            node_count = sum(pool.initial_node_count for pool in cluster.node_pools)
                            status = "Running" if cluster.status == container_v1.Cluster.Status.RUNNING else cluster.status.name
                            clusters_list.append(f"- {cluster.name} (Region: {region_name}, Version: {version}, Nodes: {node_count}, Status: {status})")
                    except Exception:
                        # Skip regions where we can't list clusters
                        continue
                    
                # Also check zonal clusters
                zones_client = compute_v1.ZonesClient()
                zones_request = compute_v1.ListZonesRequest(project=project_id)
                zones = zones_client.list(request=zones_request)
                
                for zone_item in zones:
                    zone_name = zone_item.name
                    parent = f"projects/{project_id}/locations/{zone_name}"
                    try:
                        response = client.list_clusters(parent=parent)
                        
                        for cluster in response.clusters:
                            version = cluster.current_master_version
                            node_count = sum(pool.initial_node_count for pool in cluster.node_pools)
                            status = "Running" if cluster.status == container_v1.Cluster.Status.RUNNING else cluster.status.name
                            clusters_list.append(f"- {cluster.name} (Zone: {zone_name}, Version: {version}, Nodes: {node_count}, Status: {status})")
                    except Exception:
                        # Skip zones where we can't list clusters
                        continue
            
            if not clusters_list:
                region_msg = f" in region {region}" if region else ""
                return f"No GKE clusters found{region_msg} for project {project_id}."
            
            clusters_str = "\n".join(clusters_list)
            region_msg = f" in region {region}" if region else ""
            
            return f"""
Google Kubernetes Engine (GKE) Clusters{region_msg} in GCP Project {project_id}:
{clusters_str}
"""
        except Exception as e:
            return f"Error listing GKE clusters: {str(e)}"
    
    @mcp.tool()
    def get_cluster_details(project_id: str, cluster_name: str, location: str) -> str:
        """
        Get detailed information about a specific GKE cluster.
        
        Args:
            project_id: The ID of the GCP project
            cluster_name: The name of the GKE cluster
            location: The location (region or zone) of the cluster
        
        Returns:
            Detailed information about the specified GKE cluster
        """
        try:
            from google.cloud import container_v1
            
            # Initialize the GKE client
            client = container_v1.ClusterManagerClient()
            
            # Get cluster details
            cluster_path = f"projects/{project_id}/locations/{location}/clusters/{cluster_name}"
            cluster = client.get_cluster(name=cluster_path)
            
            # Format the response
            details = []
            details.append(f"Name: {cluster.name}")
            details.append(f"Description: {cluster.description or 'None'}")
            details.append(f"Location: {location}")
            details.append(f"Location Type: {'Regional' if '-' not in location else 'Zonal'}")
            details.append(f"Status: {'Running' if cluster.status == container_v1.Cluster.Status.RUNNING else cluster.status.name}")
            details.append(f"Kubernetes Version: {cluster.current_master_version}")
            details.append(f"Network: {cluster.network}")
            details.append(f"Subnetwork: {cluster.subnetwork}")
            details.append(f"Cluster CIDR: {cluster.cluster_ipv4_cidr}")
            details.append(f"Services CIDR: {cluster.services_ipv4_cidr}")
            details.append(f"Endpoint: {cluster.endpoint}")
            
            # Add Node Pools information
            node_pools = []
            for pool in cluster.node_pools:
                machine_type = pool.config.machine_type
                disk_size_gb = pool.config.disk_size_gb
                autoscaling = "Enabled" if pool.autoscaling and pool.autoscaling.enabled else "Disabled"
                min_nodes = pool.autoscaling.min_node_count if pool.autoscaling and pool.autoscaling.enabled else "N/A"
                max_nodes = pool.autoscaling.max_node_count if pool.autoscaling and pool.autoscaling.enabled else "N/A"
                initial_nodes = pool.initial_node_count
                
                node_pools.append(f"  - {pool.name} (Machine: {machine_type}, Disk: {disk_size_gb}GB, Initial Nodes: {initial_nodes})")
                if autoscaling == "Enabled":
                    node_pools.append(f"    Autoscaling: {autoscaling} (Min: {min_nodes}, Max: {max_nodes})")
            
            if node_pools:
                details.append(f"Node Pools ({len(cluster.node_pools)}):\n" + "\n".join(node_pools))
            
            # Add Addons information
            addons = []
            if cluster.addons_config:
                config = cluster.addons_config
                addons.append(f"  - HTTP Load Balancing: {'Enabled' if not config.http_load_balancing or not config.http_load_balancing.disabled else 'Disabled'}")
                addons.append(f"  - Horizontal Pod Autoscaling: {'Enabled' if not config.horizontal_pod_autoscaling or not config.horizontal_pod_autoscaling.disabled else 'Disabled'}")
                addons.append(f"  - Kubernetes Dashboard: {'Enabled' if not config.kubernetes_dashboard or not config.kubernetes_dashboard.disabled else 'Disabled'}")
                addons.append(f"  - Network Policy: {'Enabled' if config.network_policy_config and not config.network_policy_config.disabled else 'Disabled'}")
            
            if addons:
                details.append(f"Addons:\n" + "\n".join(addons))
            
            details_str = "\n".join(details)
            
            return f"""
GKE Cluster Details:
{details_str}
"""
        except Exception as e:
            return f"Error getting cluster details: {str(e)}"
    
    @mcp.tool()
    def list_node_pools(project_id: str, cluster_name: str, location: str) -> str:
        """
        List node pools in a GKE cluster.
        
        Args:
            project_id: The ID of the GCP project
            cluster_name: The name of the GKE cluster
            location: The location (region or zone) of the cluster
        
        Returns:
            List of node pools in the specified GKE cluster
        """
        try:
            from google.cloud import container_v1
            
            # Initialize the GKE client
            client = container_v1.ClusterManagerClient()
            
            # List node pools
            cluster_path = f"projects/{project_id}/locations/{location}/clusters/{cluster_name}"
            node_pools = client.list_node_pools(parent=cluster_path)
            
            # Format the response
            pools_list = []
            for pool in node_pools.node_pools:
                machine_type = pool.config.machine_type
                disk_size_gb = pool.config.disk_size_gb
                autoscaling = "Enabled" if pool.autoscaling and pool.autoscaling.enabled else "Disabled"
                min_nodes = pool.autoscaling.min_node_count if pool.autoscaling and pool.autoscaling.enabled else "N/A"
                max_nodes = pool.autoscaling.max_node_count if pool.autoscaling and pool.autoscaling.enabled else "N/A"
                initial_nodes = pool.initial_node_count
                
                pool_info = [
                    f"- {pool.name}:",
                    f"  Machine Type: {machine_type}",
                    f"  Disk Size: {disk_size_gb}GB",
                    f"  Initial Node Count: {initial_nodes}",
                    f"  Autoscaling: {autoscaling}"
                ]
                
                if autoscaling == "Enabled":
                    pool_info.append(f"  Min Nodes: {min_nodes}")
                    pool_info.append(f"  Max Nodes: {max_nodes}")
                
                if pool.config.labels:
                    labels = [f"{k}: {v}" for k, v in pool.config.labels.items()]
                    pool_info.append(f"  Labels: {', '.join(labels)}")
                
                pools_list.append("\n".join(pool_info))
            
            if not pools_list:
                return f"No node pools found in GKE cluster {cluster_name} in location {location}."
            
            pools_str = "\n".join(pools_list)
            
            return f"""
Node Pools in GKE Cluster {cluster_name} (Location: {location}):
{pools_str}
"""
        except Exception as e:
            return f"Error listing node pools: {str(e)}"
    
    @mcp.tool()
    def resize_node_pool(project_id: str, cluster_name: str, location: str, node_pool_name: str, node_count: int) -> str:
        """
        Resize a node pool in a GKE cluster.
        
        Args:
            project_id: The ID of the GCP project
            cluster_name: The name of the GKE cluster
            location: The location (region or zone) of the cluster
            node_pool_name: The name of the node pool to resize
            node_count: The new node count for the pool
        
        Returns:
            Result of the node pool resize operation
        """
        try:
            from google.cloud import container_v1
            
            # Initialize the GKE client
            client = container_v1.ClusterManagerClient()
            
            # Create the node pool path
            node_pool_path = f"projects/{project_id}/locations/{location}/clusters/{cluster_name}/nodePools/{node_pool_name}"
            
            # Get the current node pool
            node_pool = client.get_node_pool(name=node_pool_path)
            current_node_count = node_pool.initial_node_count
            
            # Check if autoscaling is enabled
            if node_pool.autoscaling and node_pool.autoscaling.enabled:
                return f"""
Cannot resize node pool {node_pool_name} because autoscaling is enabled.
To manually set the node count, you must first disable autoscaling for this node pool.
Current autoscaling settings:
- Min nodes: {node_pool.autoscaling.min_node_count}
- Max nodes: {node_pool.autoscaling.max_node_count}
"""
            
            # Resize the node pool
            request = container_v1.SetNodePoolSizeRequest(
                name=node_pool_path,
                node_count=node_count
            )
            operation = client.set_node_pool_size(request=request)
            
            return f"""
Node pool resize operation initiated:
- Cluster: {cluster_name}
- Location: {location}
- Node Pool: {node_pool_name}
- Current Node Count: {current_node_count}
- New Node Count: {node_count}

Operation ID: {operation.name}
Status: {operation.status.name if hasattr(operation.status, 'name') else operation.status}
"""
        except Exception as e:
            return f"Error resizing node pool: {str(e)}"