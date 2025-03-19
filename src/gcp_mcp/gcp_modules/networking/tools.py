"""
Google Cloud Platform Networking tools.
"""
from typing import List, Dict, Any, Optional

def register_tools(mcp):
    """Register all networking tools with the MCP server."""
    
    @mcp.tool()
    def list_vpc_networks(project_id: str) -> str:
        """
        List Virtual Private Cloud (VPC) networks in a GCP project.
        
        Args:
            project_id: The ID of the GCP project to list VPC networks for
        
        Returns:
            List of VPC networks in the specified GCP project
        """
        try:
            from google.cloud import compute_v1
            
            # Initialize the Compute Engine client for networks
            client = compute_v1.NetworksClient()
            
            # List networks
            request = compute_v1.ListNetworksRequest(project=project_id)
            networks = client.list(request=request)
            
            # Format the response
            networks_list = []
            for network in networks:
                subnet_mode = "Auto" if network.auto_create_subnetworks else "Custom"
                creation_time = network.creation_timestamp if network.creation_timestamp else "Unknown"
                
                # Get subnet information if available
                subnets = []
                if not network.auto_create_subnetworks and network.subnetworks:
                    for subnet_url in network.subnetworks:
                        subnet_name = subnet_url.split('/')[-1]
                        subnet_region = subnet_url.split('/')[-3]
                        subnets.append(f"    - {subnet_name} (Region: {subnet_region})")
                
                network_info = f"- {network.name} (Mode: {subnet_mode}, Created: {creation_time})"
                if subnets:
                    network_info += "\n  Subnets:\n" + "\n".join(subnets)
                    
                networks_list.append(network_info)
            
            if not networks_list:
                return f"No VPC networks found in project {project_id}."
            
            networks_str = "\n".join(networks_list)
            
            return f"""
VPC Networks in GCP Project {project_id}:
{networks_str}
"""
        except Exception as e:
            return f"Error listing VPC networks: {str(e)}"
    
    @mcp.tool()
    def get_vpc_details(project_id: str, network_name: str) -> str:
        """
        Get detailed information about a specific VPC network.
        
        Args:
            project_id: The ID of the GCP project
            network_name: The name of the VPC network
        
        Returns:
            Detailed information about the specified VPC network
        """
        try:
            from google.cloud import compute_v1
            
            # Initialize the Compute Engine client for networks
            network_client = compute_v1.NetworksClient()
            subnet_client = compute_v1.SubnetworksClient()
            
            # Get network details
            network = network_client.get(project=project_id, network=network_name)
            
            # Format the response
            details = []
            details.append(f"Name: {network.name}")
            details.append(f"ID: {network.id}")
            details.append(f"Description: {network.description or 'None'}")
            details.append(f"Self Link: {network.self_link}")
            details.append(f"Creation Time: {network.creation_timestamp}")
            details.append(f"Subnet Mode: {'Auto' if network.auto_create_subnetworks else 'Custom'}")
            details.append(f"Routing Mode: {network.routing_config.routing_mode if network.routing_config else 'Unknown'}")
            details.append(f"MTU: {network.mtu}")
            
            # If it's a custom subnet mode network, get all subnets
            if not network.auto_create_subnetworks:
                # List all subnets in this network
                request = compute_v1.ListSubnetworksRequest(project=project_id)
                subnets = []
                
                for item in subnet_client.list(request=request):
                    # Check if the subnet belongs to this network
                    if network.name in item.network:
                        cidr = item.ip_cidr_range
                        region = item.region.split('/')[-1]
                        purpose = f", Purpose: {item.purpose}" if item.purpose else ""
                        private_ip = ", Private Google Access: Enabled" if item.private_ip_google_access else ""
                        subnets.append(f"  - {item.name} (Region: {region}, CIDR: {cidr}{purpose}{private_ip})")
                
                if subnets:
                    details.append(f"Subnets ({len(subnets)}):\n" + "\n".join(subnets))
            
            # List peering connections if any
            if network.peerings:
                peerings = []
                for peering in network.peerings:
                    state = peering.state
                    network_name = peering.network.split('/')[-1]
                    peerings.append(f"  - {network_name} (State: {state})")
                
                if peerings:
                    details.append(f"Peerings ({len(peerings)}):\n" + "\n".join(peerings))
            
            details_str = "\n".join(details)
            
            return f"""
VPC Network Details:
{details_str}
"""
        except Exception as e:
            return f"Error getting VPC network details: {str(e)}"
    
    @mcp.tool()
    def list_subnets(project_id: str, region: Optional[str] = None) -> str:
        """
        List subnets in a GCP project, optionally filtered by region.
        
        Args:
            project_id: The ID of the GCP project
            region: Optional region to filter subnets by
        
        Returns:
            List of subnets in the specified GCP project
        """
        try:
            from google.cloud import compute_v1
            
            # Initialize the Compute Engine client for subnets
            client = compute_v1.SubnetworksClient()
            
            # List subnets
            request = compute_v1.ListSubnetworksRequest(project=project_id, region=region) if region else compute_v1.ListSubnetworksRequest(project=project_id)
            subnets = client.list(request=request)
            
            # Format the response
            subnets_list = []
            for subnet in subnets:
                network_name = subnet.network.split('/')[-1]
                region_name = subnet.region.split('/')[-1]
                cidr = subnet.ip_cidr_range
                purpose = f", Purpose: {subnet.purpose}" if subnet.purpose else ""
                private_ip = ", Private Google Access: Enabled" if subnet.private_ip_google_access else ""
                
                subnet_info = f"- {subnet.name} (Network: {network_name}, Region: {region_name}, CIDR: {cidr}{purpose}{private_ip})"
                subnets_list.append(subnet_info)
            
            if not subnets_list:
                return f"No subnets found in project {project_id}{' for region ' + region if region else ''}."
            
            subnets_str = "\n".join(subnets_list)
            
            return f"""
Subnets in GCP Project {project_id}{' for region ' + region if region else ''}:
{subnets_str}
"""
        except Exception as e:
            return f"Error listing subnets: {str(e)}"
    
    @mcp.tool()
    def create_firewall_rule(project_id: str, name: str, network: str, direction: str, priority: int, 
                           source_ranges: Optional[List[str]] = None, destination_ranges: Optional[List[str]] = None,
                           allowed_protocols: Optional[List[Dict[str, Any]]] = None, denied_protocols: Optional[List[Dict[str, Any]]] = None,
                           target_tags: Optional[List[str]] = None, source_tags: Optional[List[str]] = None, 
                           description: Optional[str] = None) -> str:
        """
        Create a firewall rule in a GCP project.
        
        Args:
            project_id: The ID of the GCP project
            name: The name of the firewall rule
            network: The name of the network to create the firewall rule for
            direction: The direction of traffic to match ('INGRESS' or 'EGRESS')
            priority: The priority of the rule (lower number = higher priority, 0-65535)
            source_ranges: Optional list of source IP ranges (for INGRESS)
            destination_ranges: Optional list of destination IP ranges (for EGRESS)
            allowed_protocols: Optional list of allowed protocols, e.g. [{"IPProtocol": "tcp", "ports": ["80", "443"]}]
            denied_protocols: Optional list of denied protocols, e.g. [{"IPProtocol": "tcp", "ports": ["22"]}]
            target_tags: Optional list of target instance tags
            source_tags: Optional list of source instance tags (for INGRESS)
            description: Optional description for the firewall rule
        
        Returns:
            Result of the firewall rule creation
        """
        try:
            from google.cloud import compute_v1
            
            # Initialize the Compute Engine client for firewall
            client = compute_v1.FirewallsClient()
            
            # Create the firewall resource
            firewall = compute_v1.Firewall()
            firewall.name = name
            firewall.network = f"projects/{project_id}/global/networks/{network}"
            firewall.direction = direction
            firewall.priority = priority
            
            if description:
                firewall.description = description
            
            # Set source/destination ranges based on direction
            if direction == "INGRESS" and source_ranges:
                firewall.source_ranges = source_ranges
            elif direction == "EGRESS" and destination_ranges:
                firewall.destination_ranges = destination_ranges
            
            # Set allowed protocols
            if allowed_protocols:
                firewall.allowed = []
                for protocol in allowed_protocols:
                    allowed = compute_v1.Allowed()
                    allowed.I_p_protocol = protocol["IPProtocol"]
                    if "ports" in protocol:
                        allowed.ports = protocol["ports"]
                    firewall.allowed.append(allowed)
            
            # Set denied protocols
            if denied_protocols:
                firewall.denied = []
                for protocol in denied_protocols:
                    denied = compute_v1.Denied()
                    denied.I_p_protocol = protocol["IPProtocol"]
                    if "ports" in protocol:
                        denied.ports = protocol["ports"]
                    firewall.denied.append(denied)
            
            # Set target tags
            if target_tags:
                firewall.target_tags = target_tags
            
            # Set source tags
            if source_tags and direction == "INGRESS":
                firewall.source_tags = source_tags
            
            # Create the firewall rule
            operation = client.insert(project=project_id, firewall_resource=firewall)
            
            return f"""
Firewall rule creation initiated:
- Name: {name}
- Network: {network}
- Direction: {direction}
- Priority: {priority}
- Description: {description or 'None'}
- Source Ranges: {source_ranges or 'None'}
- Destination Ranges: {destination_ranges or 'None'}
- Allowed Protocols: {allowed_protocols or 'None'}
- Denied Protocols: {denied_protocols or 'None'}
- Target Tags: {target_tags or 'None'}
- Source Tags: {source_tags or 'None'}

Operation ID: {operation.id}
Status: {operation.status}
"""
        except Exception as e:
            return f"Error creating firewall rule: {str(e)}"
    
    @mcp.tool()
    def list_firewall_rules(project_id: str, network: Optional[str] = None) -> str:
        """
        List firewall rules in a GCP project, optionally filtered by network.
        
        Args:
            project_id: The ID of the GCP project
            network: Optional network name to filter firewall rules by
        
        Returns:
            List of firewall rules in the specified GCP project
        """
        try:
            from google.cloud import compute_v1
            
            # Initialize the Compute Engine client for firewall
            client = compute_v1.FirewallsClient()
            
            # List firewall rules
            request = compute_v1.ListFirewallsRequest(project=project_id)
            firewalls = client.list(request=request)
            
            # Format the response
            firewalls_list = []
            for firewall in firewalls:
                # If network filter is applied, skip firewalls not in that network
                if network and network not in firewall.network:
                    continue
                
                # Get network name from the full URL
                network_name = firewall.network.split('/')[-1]
                
                # Get allowed/denied protocols
                allowed = []
                for allow in firewall.allowed:
                    ports = f":{','.join(allow.ports)}" if allow.ports else ""
                    allowed.append(f"{allow.I_p_protocol}{ports}")
                
                denied = []
                for deny in firewall.denied:
                    ports = f":{','.join(deny.ports)}" if deny.ports else ""
                    denied.append(f"{deny.I_p_protocol}{ports}")
                
                # Format sources/destinations based on direction
                if firewall.direction == "INGRESS":
                    sources = firewall.source_ranges or firewall.source_tags or ["Any"]
                    destinations = ["Any"]
                else:  # EGRESS
                    sources = ["Any"]
                    destinations = firewall.destination_ranges or ["Any"]
                
                # Create the firewall rule info string
                rule_info = [
                    f"- {firewall.name}",
                    f"  Network: {network_name}",
                    f"  Direction: {firewall.direction}",
                    f"  Priority: {firewall.priority}",
                    f"  Action: {'Allow' if firewall.allowed else 'Deny'}"
                ]
                
                if allowed:
                    rule_info.append(f"  Allowed: {', '.join(allowed)}")
                if denied:
                    rule_info.append(f"  Denied: {', '.join(denied)}")
                
                rule_info.append(f"  Sources: {', '.join(sources)}")
                rule_info.append(f"  Destinations: {', '.join(destinations)}")
                
                if firewall.target_tags:
                    rule_info.append(f"  Target Tags: {', '.join(firewall.target_tags)}")
                
                firewalls_list.append("\n".join(rule_info))
            
            if not firewalls_list:
                return f"No firewall rules found in project {project_id}{' for network ' + network if network else ''}."
            
            firewalls_str = "\n".join(firewalls_list)
            
            return f"""
Firewall Rules in GCP Project {project_id}{' for network ' + network if network else ''}:
{firewalls_str}
"""
        except Exception as e:
            return f"Error listing firewall rules: {str(e)}"
    
    @mcp.tool()
    def list_gcp_services(project_id: str) -> str:
        """
        List enabled services/APIs in a GCP project.
        
        Args:
            project_id: The ID of the GCP project to list services for
        
        Returns:
            List of enabled services in the specified GCP project
        """
        try:
            try:
                from google.cloud import service_usage
            except ImportError:
                return "Error: The Google Cloud service usage library is not installed. Please install it with 'pip install google-cloud-service-usage'."
            
            # Initialize the Service Usage client
            client = service_usage.ServiceUsageClient()
            
            # Create the request
            request = service_usage.ListServicesRequest(
                parent=f"projects/{project_id}",
                filter="state:ENABLED"
            )
            
            # List enabled services
            services = client.list_services(request=request)
            
            # Format the response
            services_list = []
            for service in services:
                name = service.name.split('/')[-1] if service.name else "Unknown"
                title = service.config.title if service.config else "Unknown"
                services_list.append(f"- {name}: {title}")
            
            if not services_list:
                return f"No services are enabled in project {project_id}."
            
            services_str = "\n".join(services_list)
            
            return f"""
Enabled Services in GCP Project {project_id}:
{services_str}
"""
        except Exception as e:
            return f"Error listing GCP services: {str(e)}"