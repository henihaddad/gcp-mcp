"""
Google Cloud Platform Monitoring tools.
"""
from typing import List, Dict, Any, Optional

def register_tools(mcp):
    """Register all monitoring tools with the MCP server."""
    
    @mcp.tool()
    def list_monitoring_metrics(project_id: str, filter_str: str = "") -> str:
        """
        List available monitoring metrics for a GCP project.
        
        Args:
            project_id: The ID of the GCP project to list metrics for
            filter_str: Optional filter string to narrow down the metrics
        
        Returns:
            List of available monitoring metrics in the specified GCP project
        """
        try:
            try:
                from google.cloud import monitoring_v3
            except ImportError:
                return "Error: The Google Cloud monitoring library is not installed. Please install it with 'pip install google-cloud-monitoring'."
            
            # Initialize the Monitoring client
            client = monitoring_v3.MetricServiceClient()
            
            # Format the project name
            project_name = f"projects/{project_id}"
            
            # Create the request object with the filter
            request = monitoring_v3.ListMetricDescriptorsRequest(
                name=project_name
            )
            
            # Add filter if provided
            if filter_str:
                request.filter = filter_str
            
            # List metric descriptors with optional filter
            descriptors = client.list_metric_descriptors(request=request)
            
            # Format the response
            metrics_list = []
            for descriptor in descriptors:
                metric_type = descriptor.type
                display_name = descriptor.display_name or metric_type.split('/')[-1]
                description = descriptor.description or "No description"
                metrics_list.append(f"- {display_name}: {metric_type}\n  {description}")
            
            if not metrics_list:
                filter_msg = f" with filter '{filter_str}'" if filter_str else ""
                return f"No metrics found{filter_msg} for project {project_id}."
            
            # Limit to 50 metrics to avoid overwhelming response
            if len(metrics_list) > 50:
                metrics_str = "\n".join(metrics_list[:50])
                return f"Found {len(metrics_list)} metrics for project {project_id}. Showing first 50:\n\n{metrics_str}\n\nUse a filter to narrow down results."
            else:
                metrics_str = "\n".join(metrics_list)
                return f"Found {len(metrics_list)} metrics for project {project_id}:\n\n{metrics_str}"
        except Exception as e:
            return f"Error listing monitoring metrics: {str(e)}"
    
    @mcp.tool()
    def get_monitoring_alerts(project_id: str) -> str:
        """
        Get active monitoring alerts for a GCP project.
        
        Args:
            project_id: The ID of the GCP project to get alerts for
        
        Returns:
            Active alerts for the specified GCP project
        """
        try:
            from google.cloud import monitoring_v3
            from google.protobuf.json_format import MessageToDict
            
            # Initialize the Alert Policy Service client
            alert_client = monitoring_v3.AlertPolicyServiceClient()
            
            # Format the project name
            project_name = f"projects/{project_id}"
            
            # Create the request object
            request = monitoring_v3.ListAlertPoliciesRequest(
                name=project_name
            )
            
            # List all alert policies
            alert_policies = alert_client.list_alert_policies(request=request)
            
            # Initialize the Metric Service client for metric data
            metric_client = monitoring_v3.MetricServiceClient()
            
            # Format the response
            active_alerts = []
            
            for policy in alert_policies:
                # Check if the policy is enabled
                if not policy.enabled:
                    continue
                
                # Check for active incidents
                filter_str = f'resource.type="alerting_policy" AND metric.type="monitoring.googleapis.com/alert_policy/incident_count" AND metric.label.policy_name="{policy.name.split("/")[-1]}"'
                
                # Create a time interval for the last hour
                import datetime
                from google.protobuf import timestamp_pb2
                
                now = datetime.datetime.utcnow()
                seconds = int(now.timestamp())
                end_time = timestamp_pb2.Timestamp(seconds=seconds)
                
                start_time = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
                seconds = int(start_time.timestamp())
                start_time_proto = timestamp_pb2.Timestamp(seconds=seconds)
                
                # Create the time interval
                interval = monitoring_v3.TimeInterval(
                    start_time=start_time_proto,
                    end_time=end_time
                )
                
                # List the time series
                try:
                    # Create the request object
                    request = monitoring_v3.ListTimeSeriesRequest(
                        name=project_name,
                        filter=filter_str,
                        interval=interval,
                        view=monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL
                    )
                    
                    # List the time series
                    time_series = metric_client.list_time_series(request=request)
                    
                    is_active = False
                    for series in time_series:
                        # Check if there's a non-zero value in the time series
                        for point in series.points:
                            if point.value.int64_value > 0:
                                is_active = True
                                break
                        if is_active:
                            break
                    
                    if is_active:
                        # Format conditions
                        conditions = []
                        for condition in policy.conditions:
                            if condition.display_name:
                                conditions.append(f"    - {condition.display_name}: {condition.condition_threshold.filter}")
                        
                        # Add to active alerts
                        alert_info = [
                            f"- {policy.display_name} (ID: {policy.name.split('/')[-1]})",
                            f"  Description: {policy.documentation.content if policy.documentation else 'No description'}",
                            f"  Severity: {policy.alert_strategy.notification_rate_limit.period.seconds}s between notifications" if policy.alert_strategy.notification_rate_limit else "  No rate limiting"
                        ]
                        
                        if conditions:
                            alert_info.append("  Conditions:")
                            alert_info.extend(conditions)
                        
                        active_alerts.append("\n".join(alert_info))
                except Exception:
                    # Skip if we can't check for active incidents
                    continue
            
            if not active_alerts:
                return f"No active alerts found for project {project_id}."
            
            alerts_str = "\n".join(active_alerts)
            
            return f"""
Active Monitoring Alerts in GCP Project {project_id}:
{alerts_str}
"""
        except Exception as e:
            return f"Error getting monitoring alerts: {str(e)}"
    
    @mcp.tool()
    def create_alert_policy(project_id: str, display_name: str, metric_type: str, 
                          filter_str: str, duration_seconds: int = 60, 
                          threshold_value: float = 0.0, comparison: str = "COMPARISON_GT",
                          notification_channels: Optional[List[str]] = None) -> str:
        """
        Create a new alert policy in a GCP project.
        
        Args:
            project_id: The ID of the GCP project
            display_name: The display name for the alert policy
            metric_type: The metric type to monitor (e.g., "compute.googleapis.com/instance/cpu/utilization")
            filter_str: The filter for the metric data
            duration_seconds: The duration in seconds over which to evaluate the condition (default: 60)
            threshold_value: The threshold value for the condition (default: 0.0)
            comparison: The comparison type (COMPARISON_GT, COMPARISON_LT, etc.) (default: COMPARISON_GT)
            notification_channels: Optional list of notification channel IDs
        
        Returns:
            Result of the alert policy creation
        """
        try:
            from google.cloud import monitoring_v3
            from google.protobuf import duration_pb2
            
            # Initialize the Alert Policy Service client
            client = monitoring_v3.AlertPolicyServiceClient()
            
            # Format the project name
            project_name = f"projects/{project_id}"
            
            # Create a duration object
            duration = duration_pb2.Duration(seconds=duration_seconds)
            
            # Create the alert condition
            condition = monitoring_v3.AlertPolicy.Condition(
                display_name=f"Condition for {display_name}",
                condition_threshold=monitoring_v3.AlertPolicy.Condition.MetricThreshold(
                    filter=filter_str,
                    comparison=getattr(monitoring_v3.ComparisonType, comparison),
                    threshold_value=threshold_value,
                    duration=duration,
                    trigger=monitoring_v3.AlertPolicy.Condition.Trigger(
                        count=1
                    ),
                    aggregations=[
                        monitoring_v3.Aggregation(
                            alignment_period=duration_pb2.Duration(seconds=60),
                            per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_MEAN,
                            cross_series_reducer=monitoring_v3.Aggregation.Reducer.REDUCE_MEAN
                        )
                    ]
                )
            )
            
            # Create the alert policy
            alert_policy = monitoring_v3.AlertPolicy(
                display_name=display_name,
                conditions=[condition],
                combiner=monitoring_v3.AlertPolicy.ConditionCombinerType.OR
            )
            
            # Add notification channels if provided
            if notification_channels:
                alert_policy.notification_channels = [
                    f"projects/{project_id}/notificationChannels/{channel_id}" 
                    for channel_id in notification_channels
                ]
            
            # Create the policy
            policy = client.create_alert_policy(name=project_name, alert_policy=alert_policy)
            
            # Format response
            conditions_str = "\n".join([
                f"- {c.display_name}: {c.condition_threshold.filter}" 
                for c in policy.conditions
            ])
            
            notifications_str = "None"
            if policy.notification_channels:
                notifications_str = "\n".join([
                    f"- {channel.split('/')[-1]}" 
                    for channel in policy.notification_channels
                ])
            
            return f"""
Alert Policy created successfully:
- Name: {policy.display_name}
- Policy ID: {policy.name.split('/')[-1]}
- Combiner: {policy.combiner.name}

Conditions:
{conditions_str}

Notification Channels:
{notifications_str}
"""
        except Exception as e:
            return f"Error creating alert policy: {str(e)}"
    
    @mcp.tool()
    def list_uptime_checks(project_id: str) -> str:
        """
        List Uptime checks in a GCP project.
        
        Args:
            project_id: The ID of the GCP project to list Uptime checks for
        
        Returns:
            List of Uptime checks in the specified GCP project
        """
        try:
            from google.cloud import monitoring_v3
            
            # Initialize the Uptime Check Service client
            client = monitoring_v3.UptimeCheckServiceClient()
            
            # Format the project name
            project_name = f"projects/{project_id}"
            
            # Create the request object
            request = monitoring_v3.ListUptimeCheckConfigsRequest(
                parent=project_name
            )
            
            # List uptime checks
            uptime_checks = client.list_uptime_check_configs(request=request)
            
            # Format the response
            checks_list = []
            
            for check in uptime_checks:
                check_id = check.name.split('/')[-1]
                display_name = check.display_name
                period_seconds = check.period.seconds
                timeout_seconds = check.timeout.seconds
                
                # Get check type and details
                check_details = []
                if check.HasField('http_check'):
                    check_type = "HTTP"
                    url = check.http_check.path
                    if check.resource.HasField('monitored_resource'):
                        host = check.monitored_resource.labels.get('host', 'Unknown')
                        url = f"{host}{url}"
                    elif check.http_check.HasField('host'):
                        url = f"{check.http_check.host}{url}"
                    check_details.append(f"URL: {url}")
                    check_details.append(f"Port: {check.http_check.port}")
                    
                elif check.HasField('tcp_check'):
                    check_type = "TCP"
                    if check.resource.HasField('monitored_resource'):
                        host = check.monitored_resource.labels.get('host', 'Unknown')
                    else:
                        host = check.tcp_check.host
                    check_details.append(f"Host: {host}")
                    check_details.append(f"Port: {check.tcp_check.port}")
                else:
                    check_type = "Unknown"
                
                checks_list.append(f"- {display_name} (ID: {check_id}, Type: {check_type})")
                checks_list.append(f"  Frequency: {period_seconds}s, Timeout: {timeout_seconds}s")
                checks_list.extend([f"  {detail}" for detail in check_details])
            
            if not checks_list:
                return f"No Uptime checks found for project {project_id}."
            
            checks_str = "\n".join(checks_list)
            
            return f"""
Uptime Checks in GCP Project {project_id}:
{checks_str}
"""
        except Exception as e:
            return f"Error listing Uptime checks: {str(e)}"