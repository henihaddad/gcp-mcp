# GCP MCP Application

## Claude Desktop Integration

To enable GCP management capabilities in Claude Desktop, simply add the following configuration to your Claude Desktop MCP configuration:

```json
{
  "gcp-mcp": {
    "command": "uvx",
    "args": [
      "gcp-mcp"
    ]
  }
}
```

That's it! No additional setup or credential manipulation is required. When you first ask Claude to interact with your GCP resources, a browser window will automatically open for you to authenticate and grant access. Once you approve the access, Claude will be able to manage your GCP resources through natural language commands.

Here are some example requests you can make:

Basic Operations:
- "Could you list my GCP projects?"
- "Show me my compute instances"
- "What storage buckets do I have?"

Resource Creation:
- "Please create a compute instance with 2GB RAM and 10GB storage, name it MCP-engine"
- "Create a new storage bucket called my-backup-bucket in us-central1"
- "Set up a new VPC network named prod-network with subnet 10.0.0.0/24"

Resource Management:
- "Stop all compute instances in the dev project"
- "Show me all instances that have been running for more than 24 hours"
- "What's the current CPU usage of my instance named backend-server?"
- "Create a snapshot of my database disk"

Monitoring and Alerts:
- "Set up an alert for when CPU usage goes above 80%"
- "Show me all critical alerts from the last 24 hours"
- "What's the current status of my GKE clusters?"

## Features

The application provides comprehensive coverage of GCP services:

### Resource Management
- Projects and quotas management
- Asset inventory
- IAM permissions

### Compute & Infrastructure
- Compute Engine instances
- Storage buckets and disks
- VPC networks and firewall rules
- Kubernetes Engine (GKE) clusters

### Databases & Storage
- Cloud SQL instances
- Firestore databases
- Cloud Storage
- Database backups

### Monitoring & Billing
- Metrics and alerts
- Billing information
- Uptime monitoring
- Resource usage tracking

### Coming Soon
- Deployment manager and infrastructure as code

## Installation

```bash
pip install gcp-mcp
```

## License

[MIT License](LICENSE) 

Your contributions and issues are welcome !
