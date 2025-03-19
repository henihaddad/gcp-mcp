"""
Google Cloud Platform Compute Engine tools.
"""
from typing import List, Dict, Any, Optional

def register_tools(mcp):
    """Register all compute tools with the MCP server."""
    
    @mcp.tool()
    def list_compute_instances(project_id: str, zone: str = "") -> str:
        """
        List Compute Engine instances in a GCP project.
        
        Args:
            project_id: The ID of the GCP project to list instances for
            zone: Optional zone to filter instances (e.g., "us-central1-a")
        
        Returns:
            List of Compute Engine instances in the specified GCP project
        """
        try:
            from google.cloud import compute_v1
            
            # Initialize the Compute Engine client
            client = compute_v1.InstancesClient()
            
            instances_list = []
            
            if zone:
                # List instances in the specified zone
                request = compute_v1.ListInstancesRequest(
                    project=project_id,
                    zone=zone
                )
                instances = client.list(request=request)
                
                for instance in instances:
                    machine_type = instance.machine_type.split('/')[-1] if instance.machine_type else "Unknown"
                    status = instance.status
                    ext_ip = "None"
                    int_ip = "None"
                    
                    # Get IP addresses
                    if instance.network_interfaces:
                        int_ip = instance.network_interfaces[0].network_i_p
                        if instance.network_interfaces[0].access_configs:
                            ext_ip = instance.network_interfaces[0].access_configs[0].nat_i_p or "None"
                    
                    instances_list.append(f"- {instance.name} (Zone: {zone}, Type: {machine_type}, Internal IP: {int_ip}, External IP: {ext_ip}, Status: {status})")
            else:
                # List instances in all zones
                zones_client = compute_v1.ZonesClient()
                zones_request = compute_v1.ListZonesRequest(project=project_id)
                zones = zones_client.list(request=zones_request)
                
                for zone_item in zones:
                    zone_name = zone_item.name
                    request = compute_v1.ListInstancesRequest(
                        project=project_id,
                        zone=zone_name
                    )
                    try:
                        instances = client.list(request=request)
                        
                        for instance in instances:
                            machine_type = instance.machine_type.split('/')[-1] if instance.machine_type else "Unknown"
                            status = instance.status
                            ext_ip = "None"
                            int_ip = "None"
                            
                            # Get IP addresses
                            if instance.network_interfaces:
                                int_ip = instance.network_interfaces[0].network_i_p
                                if instance.network_interfaces[0].access_configs:
                                    ext_ip = instance.network_interfaces[0].access_configs[0].nat_i_p or "None"
                            
                            instances_list.append(f"- {instance.name} (Zone: {zone_name}, Type: {machine_type}, Internal IP: {int_ip}, External IP: {ext_ip}, Status: {status})")
                    except Exception:
                        # Skip zones where we can't list instances
                        continue
            
            if not instances_list:
                zone_msg = f" in zone {zone}" if zone else ""
                return f"No Compute Engine instances found{zone_msg} for project {project_id}."
            
            instances_str = "\n".join(instances_list)
            zone_msg = f" in zone {zone}" if zone else ""
            
            return f"""
Compute Engine Instances{zone_msg} in GCP Project {project_id}:
{instances_str}
"""
        except Exception as e:
            return f"Error listing Compute Engine instances: {str(e)}"
    
    @mcp.tool()
    def get_instance_details(project_id: str, zone: str, instance_name: str) -> str:
        """
        Get detailed information about a specific Compute Engine instance.
        
        Args:
            project_id: The ID of the GCP project
            zone: The zone where the instance is located (e.g., "us-central1-a")
            instance_name: The name of the instance to get details for
        
        Returns:
            Detailed information about the specified Compute Engine instance
        """
        try:
            from google.cloud import compute_v1
            
            # Initialize the Compute Engine client
            client = compute_v1.InstancesClient()
            
            # Get the instance details
            instance = client.get(project=project_id, zone=zone, instance=instance_name)
            
            # Format machine type
            machine_type = instance.machine_type.split('/')[-1] if instance.machine_type else "Unknown"
            
            # Format creation timestamp
            creation_timestamp = instance.creation_timestamp if instance.creation_timestamp else "Unknown"
            
            # Format boot disk
            boot_disk = "None"
            if instance.disks:
                for disk in instance.disks:
                    if disk.boot:
                        boot_disk = disk.source.split('/')[-1] if disk.source else "Unknown"
                        break
            
            # Get IP addresses
            network_interfaces = []
            if instance.network_interfaces:
                for i, iface in enumerate(instance.network_interfaces):
                    network = iface.network.split('/')[-1] if iface.network else "Unknown"
                    subnetwork = iface.subnetwork.split('/')[-1] if iface.subnetwork else "Unknown"
                    internal_ip = iface.network_i_p or "None"
                    
                    # Check for external IP
                    external_ip = "None"
                    if iface.access_configs:
                        external_ip = iface.access_configs[0].nat_i_p or "None"
                    
                    network_interfaces.append(f"  Interface {i}:\n    Network: {network}\n    Subnetwork: {subnetwork}\n    Internal IP: {internal_ip}\n    External IP: {external_ip}")
            
            networks_str = "\n".join(network_interfaces) if network_interfaces else "  None"
            
            # Get attached disks
            disks = []
            if instance.disks:
                for i, disk in enumerate(instance.disks):
                    disk_name = disk.source.split('/')[-1] if disk.source else "Unknown"
                    disk_type = "Boot" if disk.boot else "Data"
                    auto_delete = "Yes" if disk.auto_delete else "No"
                    mode = disk.mode if disk.mode else "Unknown"
                    
                    disks.append(f"  Disk {i}:\n    Name: {disk_name}\n    Type: {disk_type}\n    Mode: {mode}\n    Auto-delete: {auto_delete}")
            
            disks_str = "\n".join(disks) if disks else "  None"
            
            # Get labels
            labels = []
            if instance.labels:
                for key, value in instance.labels.items():
                    labels.append(f"  {key}: {value}")
            
            labels_str = "\n".join(labels) if labels else "  None"
            
            # Get metadata
            metadata_items = []
            if instance.metadata and instance.metadata.items:
                for item in instance.metadata.items:
                    metadata_items.append(f"  {item.key}: {item.value}")
            
            metadata_str = "\n".join(metadata_items) if metadata_items else "  None"
            
            return f"""
Compute Engine Instance Details for {instance_name}:

Project: {project_id}
Zone: {zone}
Machine Type: {machine_type}
Status: {instance.status}
Creation Time: {creation_timestamp}
CPU Platform: {instance.cpu_platform}
Boot Disk: {boot_disk}

Network Interfaces:
{networks_str}

Disks:
{disks_str}

Labels:
{labels_str}

Metadata:
{metadata_str}

Service Accounts: {"Yes" if instance.service_accounts else "None"}
"""
        except Exception as e:
            return f"Error getting instance details: {str(e)}"
    
    @mcp.tool()
    def start_instance(project_id: str, zone: str, instance_name: str) -> str:
        """
        Start a Compute Engine instance.
        
        Args:
            project_id: The ID of the GCP project
            zone: The zone where the instance is located (e.g., "us-central1-a")
            instance_name: The name of the instance to start
        
        Returns:
            Status message indicating whether the instance was started successfully
        """
        try:
            from google.cloud import compute_v1
            
            # Initialize the Compute Engine client
            client = compute_v1.InstancesClient()
            
            # Start the instance
            operation = client.start(project=project_id, zone=zone, instance=instance_name)
            
            # Wait for the operation to complete
            operation_client = compute_v1.ZoneOperationsClient()
            
            # This is a synchronous call that will wait until the operation is complete
            while operation.status != compute_v1.Operation.Status.DONE:
                operation = operation_client.get(project=project_id, zone=zone, operation=operation.name.split('/')[-1])
                import time
                time.sleep(1)
            
            if operation.error:
                return f"Error starting instance {instance_name}: {operation.error.errors[0].message}"
            
            return f"Instance {instance_name} in zone {zone} started successfully."
        except Exception as e:
            return f"Error starting instance: {str(e)}"
    
    @mcp.tool()
    def stop_instance(project_id: str, zone: str, instance_name: str) -> str:
        """
        Stop a Compute Engine instance.
        
        Args:
            project_id: The ID of the GCP project
            zone: The zone where the instance is located (e.g., "us-central1-a")
            instance_name: The name of the instance to stop
        
        Returns:
            Status message indicating whether the instance was stopped successfully
        """
        try:
            from google.cloud import compute_v1
            
            # Initialize the Compute Engine client
            client = compute_v1.InstancesClient()
            
            # Stop the instance
            operation = client.stop(project=project_id, zone=zone, instance=instance_name)
            
            # Wait for the operation to complete
            operation_client = compute_v1.ZoneOperationsClient()
            
            # This is a synchronous call that will wait until the operation is complete
            while operation.status != compute_v1.Operation.Status.DONE:
                operation = operation_client.get(project=project_id, zone=zone, operation=operation.name.split('/')[-1])
                import time
                time.sleep(1)
            
            if operation.error:
                return f"Error stopping instance {instance_name}: {operation.error.errors[0].message}"
            
            return f"Instance {instance_name} in zone {zone} stopped successfully."
        except Exception as e:
            return f"Error stopping instance: {str(e)}"
    
    @mcp.tool()
    def list_machine_types(project_id: str, zone: str) -> str:
        """
        List available machine types in a specific zone.
        
        Args:
            project_id: The ID of the GCP project
            zone: The zone to check machine types in (e.g., "us-central1-a")
        
        Returns:
            List of available machine types in the specified zone
        """
        try:
            from google.cloud import compute_v1
            
            # Initialize the Machine Types client
            client = compute_v1.MachineTypesClient()
            
            # List machine types
            request = compute_v1.ListMachineTypesRequest(
                project=project_id,
                zone=zone
            )
            machine_types = client.list(request=request)
            
            # Format the response
            types_list = []
            
            # Group by series
            series = {}
            for mt in machine_types:
                # Determine series (e.g., e2, n1, c2)
                name = mt.name
                series_name = "custom" if name.startswith("custom") else name.split("-")[0]
                
                if series_name not in series:
                    series[series_name] = []
                
                # Format the machine type details
                vcpus = mt.guest_cpus
                memory_gb = mt.memory_mb / 1024  # Convert MB to GB
                
                series[series_name].append(f"    {name}: {vcpus} vCPUs, {memory_gb:.1f} GB RAM")
            
            # Create formatted output by series
            for s_name in sorted(series.keys()):
                types_list.append(f"  {s_name} series:")
                types_list.extend(sorted(series[s_name]))
            
            if not types_list:
                return f"No machine types found in zone {zone} for project {project_id}."
            
            types_str = "\n".join(types_list)
            
            return f"""
Available Machine Types in Zone {zone} for Project {project_id}:
{types_str}
"""
        except Exception as e:
            return f"Error listing machine types: {str(e)}"
    
    @mcp.tool()
    def list_disks(project_id: str, zone: str = "") -> str:
        """
        List Compute Engine persistent disks in a GCP project.
        
        Args:
            project_id: The ID of the GCP project to list disks for
            zone: Optional zone to filter disks (e.g., "us-central1-a")
        
        Returns:
            List of persistent disks in the specified GCP project
        """
        try:
            from google.cloud import compute_v1
            
            # Initialize the Disks client
            client = compute_v1.DisksClient()
            
            disks_list = []
            
            if zone:
                # List disks in the specified zone
                request = compute_v1.ListDisksRequest(
                    project=project_id,
                    zone=zone
                )
                disks = client.list(request=request)
                
                for disk in disks:
                    size_gb = disk.size_gb
                    disk_type = disk.type.split('/')[-1] if disk.type else "Unknown"
                    status = disk.status
                    users = len(disk.users) if disk.users else 0
                    users_str = f"Attached to {users} instance(s)" if users > 0 else "Not attached"
                    
                    disks_list.append(f"- {disk.name} (Zone: {zone}, Type: {disk_type}, Size: {size_gb} GB, Status: {status}, {users_str})")
            else:
                # List disks in all zones
                zones_client = compute_v1.ZonesClient()
                zones_request = compute_v1.ListZonesRequest(project=project_id)
                zones = zones_client.list(request=zones_request)
                
                for zone_item in zones:
                    zone_name = zone_item.name
                    request = compute_v1.ListDisksRequest(
                        project=project_id,
                        zone=zone_name
                    )
                    try:
                        disks = client.list(request=request)
                        
                        for disk in disks:
                            size_gb = disk.size_gb
                            disk_type = disk.type.split('/')[-1] if disk.type else "Unknown"
                            status = disk.status
                            users = len(disk.users) if disk.users else 0
                            users_str = f"Attached to {users} instance(s)" if users > 0 else "Not attached"
                            
                            disks_list.append(f"- {disk.name} (Zone: {zone_name}, Type: {disk_type}, Size: {size_gb} GB, Status: {status}, {users_str})")
                    except Exception:
                        # Skip zones where we can't list disks
                        continue
            
            if not disks_list:
                zone_msg = f" in zone {zone}" if zone else ""
                return f"No persistent disks found{zone_msg} for project {project_id}."
            
            disks_str = "\n".join(disks_list)
            zone_msg = f" in zone {zone}" if zone else ""
            
            return f"""
Persistent Disks{zone_msg} in GCP Project {project_id}:
{disks_str}
"""
        except Exception as e:
            return f"Error listing persistent disks: {str(e)}"
    
    @mcp.tool()
    def create_instance(project_id: str, zone: str, instance_name: str, machine_type: str, 
                      source_image: str, boot_disk_size_gb: int = 10, 
                      network: str = "default", subnet: str = "", 
                      external_ip: bool = True) -> str:
        """
        Create a new Compute Engine instance.
        
        Args:
            project_id: The ID of the GCP project
            zone: The zone to create the instance in (e.g., "us-central1-a")
            instance_name: The name for the new instance
            machine_type: The machine type (e.g., "e2-medium")
            source_image: The source image for the boot disk (e.g., "projects/debian-cloud/global/images/family/debian-11")
            boot_disk_size_gb: The size of the boot disk in GB (default: 10)
            network: The network to connect to (default: "default")
            subnet: The subnetwork to connect to (optional)
            external_ip: Whether to allocate an external IP (default: True)
        
        Returns:
            Status message indicating whether the instance was created successfully
        """
        try:
            from google.cloud import compute_v1
            
            # Initialize the clients
            instances_client = compute_v1.InstancesClient()
            
            # Format the machine type
            machine_type_url = f"projects/{project_id}/zones/{zone}/machineTypes/{machine_type}"
            
            # Create the disk configuration
            boot_disk = compute_v1.AttachedDisk()
            boot_disk.boot = True
            initialize_params = compute_v1.AttachedDiskInitializeParams()
            initialize_params.source_image = source_image
            initialize_params.disk_size_gb = boot_disk_size_gb
            boot_disk.initialize_params = initialize_params
            boot_disk.auto_delete = True
            
            # Create the network configuration
            network_interface = compute_v1.NetworkInterface()
            if network.startswith("projects/"):
                network_interface.network = network
            else:
                network_interface.network = f"projects/{project_id}/global/networks/{network}"
            
            if subnet:
                if subnet.startswith("projects/"):
                    network_interface.subnetwork = subnet
                else:
                    network_interface.subnetwork = f"projects/{project_id}/regions/{zone.rsplit('-', 1)[0]}/subnetworks/{subnet}"
            
            if external_ip:
                access_config = compute_v1.AccessConfig()
                access_config.name = "External NAT"
                access_config.type_ = "ONE_TO_ONE_NAT"
                access_config.network_tier = "PREMIUM"
                network_interface.access_configs = [access_config]
            
            # Create the instance
            instance = compute_v1.Instance()
            instance.name = instance_name
            instance.machine_type = machine_type_url
            instance.disks = [boot_disk]
            instance.network_interfaces = [network_interface]
            
            # Create a default service account for the instance
            service_account = compute_v1.ServiceAccount()
            service_account.email = "default"
            service_account.scopes = ["https://www.googleapis.com/auth/cloud-platform"]
            instance.service_accounts = [service_account]
            
            # Create the instance
            operation = instances_client.insert(
                project=project_id,
                zone=zone,
                instance_resource=instance
            )
            
            # Wait for the create operation to complete
            operation_client = compute_v1.ZoneOperationsClient()
            
            # This is a synchronous call that will wait until the operation is complete
            while operation.status != compute_v1.Operation.Status.DONE:
                operation = operation_client.get(project=project_id, zone=zone, operation=operation.name.split('/')[-1])
                import time
                time.sleep(1)
            
            if operation.error:
                return f"Error creating instance {instance_name}: {operation.error.errors[0].message}"
            
            # Get the created instance to return its details
            created_instance = instances_client.get(project=project_id, zone=zone, instance=instance_name)
            
            # Get the instance IP addresses
            internal_ip = "None"
            external_ip = "None"
            
            if created_instance.network_interfaces:
                internal_ip = created_instance.network_interfaces[0].network_i_p or "None"
                if created_instance.network_interfaces[0].access_configs:
                    external_ip = created_instance.network_interfaces[0].access_configs[0].nat_i_p or "None"
            
            return f"""
Instance {instance_name} created successfully in zone {zone}.

Details:
- Machine Type: {machine_type}
- Internal IP: {internal_ip}
- External IP: {external_ip}
- Status: {created_instance.status}
"""
        except Exception as e:
            return f"Error creating instance: {str(e)}"
    
    @mcp.tool()
    def delete_instance(project_id: str, zone: str, instance_name: str) -> str:
        """
        Delete a Compute Engine instance.
        
        Args:
            project_id: The ID of the GCP project
            zone: The zone where the instance is located (e.g., "us-central1-a")
            instance_name: The name of the instance to delete
        
        Returns:
            Status message indicating whether the instance was deleted successfully
        """
        try:
            from google.cloud import compute_v1
            
            # Initialize the Compute Engine client
            client = compute_v1.InstancesClient()
            
            # Delete the instance
            operation = client.delete(project=project_id, zone=zone, instance=instance_name)
            
            # Wait for the operation to complete
            operation_client = compute_v1.ZoneOperationsClient()
            
            # This is a synchronous call that will wait until the operation is complete
            while operation.status != compute_v1.Operation.Status.DONE:
                operation = operation_client.get(project=project_id, zone=zone, operation=operation.name.split('/')[-1])
                import time
                time.sleep(1)
            
            if operation.error:
                return f"Error deleting instance {instance_name}: {operation.error.errors[0].message}"
            
            return f"Instance {instance_name} in zone {zone} deleted successfully."
        except Exception as e:
            return f"Error deleting instance: {str(e)}"
    
    @mcp.tool()
    def create_snapshot(project_id: str, zone: str, disk_name: str, snapshot_name: str, description: str = "") -> str:
        """
        Create a snapshot of a Compute Engine disk.
        
        Args:
            project_id: The ID of the GCP project
            zone: The zone where the disk is located (e.g., "us-central1-a")
            disk_name: The name of the disk to snapshot
            snapshot_name: The name for the new snapshot
            description: Optional description for the snapshot
        
        Returns:
            Status message indicating whether the snapshot was created successfully
        """
        try:
            from google.cloud import compute_v1
            
            # Initialize the Disks client
            disks_client = compute_v1.DisksClient()
            
            # Create the snapshot request
            snapshot = compute_v1.Snapshot()
            snapshot.name = snapshot_name
            if description:
                snapshot.description = description
            
            # Create the snapshot
            operation = disks_client.create_snapshot(
                project=project_id,
                zone=zone,
                disk=disk_name,
                snapshot_resource=snapshot
            )
            
            # Wait for the operation to complete
            operation_client = compute_v1.ZoneOperationsClient()
            
            # This is a synchronous call that will wait until the operation is complete
            while operation.status != compute_v1.Operation.Status.DONE:
                operation = operation_client.get(project=project_id, zone=zone, operation=operation.name.split('/')[-1])
                import time
                time.sleep(1)
            
            if operation.error:
                return f"Error creating snapshot {snapshot_name}: {operation.error.errors[0].message}"
            
            return f"Snapshot {snapshot_name} of disk {disk_name} in zone {zone} created successfully."
        except Exception as e:
            return f"Error creating snapshot: {str(e)}"
    
    @mcp.tool()
    def list_snapshots(project_id: str) -> str:
        """
        List disk snapshots in a GCP project.
        
        Args:
            project_id: The ID of the GCP project to list snapshots for
        
        Returns:
            List of disk snapshots in the specified GCP project
        """
        try:
            from google.cloud import compute_v1
            
            # Initialize the Snapshots client
            client = compute_v1.SnapshotsClient()
            
            # List snapshots
            request = compute_v1.ListSnapshotsRequest(project=project_id)
            snapshots = client.list(request=request)
            
            # Format the response
            snapshots_list = []
            for snapshot in snapshots:
                size_gb = snapshot.disk_size_gb
                status = snapshot.status
                source_disk = snapshot.source_disk.split('/')[-1] if snapshot.source_disk else "Unknown"
                creation_time = snapshot.creation_timestamp if snapshot.creation_timestamp else "Unknown"
                
                snapshots_list.append(f"- {snapshot.name} (Source: {source_disk}, Size: {size_gb} GB, Status: {status}, Created: {creation_time})")
            
            if not snapshots_list:
                return f"No snapshots found for project {project_id}."
            
            snapshots_str = "\n".join(snapshots_list)
            
            return f"""
Disk Snapshots in GCP Project {project_id}:
{snapshots_str}
"""
        except Exception as e:
            return f"Error listing snapshots: {str(e)}"