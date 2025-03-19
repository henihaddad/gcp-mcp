# GCP MCP Application

This application provides a comprehensive set of tools for interacting with Google Cloud Platform (GCP) services through the MCP (Model Calling Protocol) interface. It's designed to be used with AI assistants like Claude to provide a natural language interface to GCP services.

## Features

The application is organized into modules that cover different aspects of GCP:

### Resource Management
- List GCP projects
- Get detailed information about a GCP project
- List all assets in a GCP project using Cloud Asset Inventory
- Set a quota project for Google Cloud API requests

### IAM (Identity and Access Management)
- Check IAM permissions in a GCP project

### Compute Engine
- List Compute Engine instances in a GCP project
- Get detailed information about a specific instance
- Start/stop/delete instances
- List available machine types in a zone
- List persistent disks
- Create new instances
- Create and list disk snapshots

### Storage
- List Cloud Storage buckets in a GCP project

### Billing
- Get billing information for a GCP project

### Networking
- List VPC networks in a GCP project
- Get VPC network details
- List subnets
- Create and list firewall rules
- List enabled services/APIs in a GCP project

### Kubernetes Engine (GKE)
- List Kubernetes clusters in a GCP project

### Monitoring
- List available monitoring metrics
- Get active monitoring alerts
- Create alert policies
- List uptime checks

### Databases
- List Cloud SQL instances
- Get SQL instance details
- List databases
- Create backups
- List Firestore databases and collections

### Deployment (Coming Soon)
- Deployment manager and infrastructure as code

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-directory>
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install the package and its dependencies:
```bash
pip install -e .
```

## GCP Authentication

This application provides authentication tools that work similarly to the `gcloud` command line tools. No custom paths or special setup required - everything uses the standard Google Cloud credentials storage mechanisms.

### Authentication Commands

```python
# Login to Google Cloud (opens browser automatically)
auth_login()

# Login and set a specific project as default
auth_login(project_id="my-project-id")

# List active accounts
auth_list()

# Revoke credentials
auth_revoke()

# Set or change the default project
config_set_project(project_id="my-project-id")

# View current configuration
config_list()

# List all accessible projects
list_accessible_projects()
```

The authentication system uses the standard Google Cloud authentication patterns and credential storage locations, but doesn't require the gcloud CLI to be installed.

## Usage

Run the application:
```bash
uvicorn app:mcp --port 8080
```

This will start the MCP server, which can be used to interact with the GCP functions. The MCP server exposes functions organized by module:

### Authentication
- `auth_login(project_id)`: Authenticate with Google Cloud Platform using browser-based OAuth flow
- `auth_list()`: List active Google Cloud credentials
- `auth_revoke()`: Revoke Google Cloud credentials
- `config_set_project(project_id)`: Set the default Google Cloud project
- `config_list()`: List Google Cloud configuration properties
- `list_accessible_projects()`: List all GCP projects accessible to the authenticated user

### Resource Management
- `list_gcp_projects()`: List all available GCP projects
- `get_gcp_project_details(project_id)`: Get detailed information about a GCP project
- `list_assets(project_id, asset_types, page_size)`: List all assets in a GCP project using Cloud Asset Inventory
- `set_quota_project(project_id)`: Set a quota project for Google Cloud API requests

### IAM (Identity and Access Management)
- `check_iam_permissions(project_id)`: Check IAM permissions for the current user

### Compute Engine
- `list_compute_instances(project_id, zone)`: List Compute Engine instances (optionally filtered by zone)
- `get_instance_details(project_id, zone, instance_name)`: Get detailed information about a specific instance
- `start_instance(project_id, zone, instance_name)`: Start a stopped instance
- `stop_instance(project_id, zone, instance_name)`: Stop a running instance
- `delete_instance(project_id, zone, instance_name)`: Delete an instance
- `list_machine_types(project_id, zone)`: List available machine types in a zone
- `list_disks(project_id, zone)`: List persistent disks (optionally filtered by zone)
- `create_instance(project_id, zone, instance_name, machine_type, source_image, ...)`: Create a new instance
- `create_snapshot(project_id, zone, disk_name, snapshot_name, description)`: Create a disk snapshot
- `list_snapshots(project_id)`: List all disk snapshots in a project

### Storage
- `list_storage_buckets(project_id)`: List Cloud Storage buckets in a project

### Billing
- `get_billing_info(project_id)`: Get billing information for a project

### Networking
- `list_vpc_networks(project_id)`: List VPC networks in a project
- `get_vpc_details(project_id, network_name)`: Get detailed information about a VPC network
- `list_subnets(project_id, region)`: List subnets (optionally filtered by region)
- `create_firewall_rule(project_id, name, network, ...)`: Create a firewall rule
- `list_firewall_rules(project_id, network)`: List firewall rules (optionally filtered by network)
- `list_gcp_services(project_id)`: List enabled services/APIs in a project

### Kubernetes Engine (GKE)
- `list_gke_clusters(project_id, region)`: List GKE clusters (optionally filtered by region)

### Monitoring
- `list_monitoring_metrics(project_id, filter_str)`: List available monitoring metrics
- `get_monitoring_alerts(project_id)`: Get active monitoring alerts
- `create_alert_policy(project_id, display_name, metric_type, ...)`: Create an alert policy
- `list_uptime_checks(project_id)`: List uptime checks

### Databases
- `list_cloud_sql_instances(project_id)`: List Cloud SQL instances
- `get_sql_instance_details(project_id, instance_id)`: Get detailed information about a SQL instance
- `list_databases(project_id, instance_id)`: List databases in a SQL instance
- `create_backup(project_id, instance_id, description)`: Create a backup of a SQL instance
- `list_firestore_databases(project_id)`: List Firestore databases
- `list_firestore_collections(project_id, database_id)`: List collections in a Firestore database

### Utility Functions
- `say_hello(name)`: Simple greeting function
- `test_monitoring_imports()`: Test if the monitoring libraries are properly installed

## Examples

### Setting a Quota Project

```python
# Set the quota project to avoid the warning about end user credentials without a quota project
set_quota_project(project_id="your-project-id")
```

### Listing Assets

```python
# List all assets in a project
list_assets(project_id="your-project-id")

# List only Compute Engine instances
list_assets(
    project_id="your-project-id", 
    asset_types=["compute.googleapis.com/Instance"]
)

# List more assets per page
list_assets(
    project_id="your-project-id",
    page_size=100
)
```

### Listing Monitoring Metrics

```python
# List all metrics in a project
list_monitoring_metrics(project_id="your-project-id")

# List only compute-related metrics
list_monitoring_metrics(
    project_id="your-project-id", 
    filter_str="metric.type = starts_with(\"compute.googleapis.com\")"
)
```

### Getting Active Alerts

```python
# Get all active alerts in a project
get_monitoring_alerts(project_id="your-project-id")
```

### Creating an Alert Policy

```python
# Create a CPU utilization alert
create_alert_policy(
    project_id="your-project-id",
    display_name="High CPU Alert",
    metric_type="compute.googleapis.com/instance/cpu/utilization",
    filter_str="resource.type = \"gce_instance\"",
    duration_seconds=300,
    threshold_value=0.8,
    comparison="COMPARISON_GT"
)
```

## Testing

This project uses pytest for testing. To run the tests:

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=gcp_modules tests/

# Run only GCP function tests
pytest tests/unit/test_gcp_functions.py
```

## Project Structure

The project is organized into modules for better maintainability:

```
gcp-mcp/
├── app.py                 # Main application file
├── pyproject.toml         # Project metadata and dependencies
├── gcp_modules/           # GCP modules directory
│   ├── __init__.py
│   ├── resource_management/ # Resource management module
│   │   ├── __init__.py
│   │   └── tools.py
│   ├── iam/               # IAM module
│   │   ├── __init__.py
│   │   └── tools.py
│   ├── compute/           # Compute Engine module
│   │   ├── __init__.py
│   │   └── tools.py
│   ├── storage/           # Storage module
│   │   ├── __init__.py
│   │   └── tools.py
│   ├── billing/           # Billing module
│   │   ├── __init__.py
│   │   └── tools.py
│   ├── networking/        # Networking module
│   │   ├── __init__.py
│   │   └── tools.py
│   ├── kubernetes/        # Kubernetes module
│   │   ├── __init__.py
│   │   └── tools.py
│   ├── monitoring/        # Monitoring module
│   │   ├── __init__.py
│   │   └── tools.py
│   ├── databases/         # Databases module
│   │   ├── __init__.py
│   │   └── tools.py
│   └── deployment/        # Deployment module (coming soon)
│       ├── __init__.py
│       └── tools.py
├── tests/                 # Tests directory
│   ├── __init__.py
│   ├── conftest.py
│   └── unit/
│       ├── __init__.py
│       └── test_gcp_functions.py
└── README.md
```

## Development

### Dependency Management

This project uses `pyproject.toml` for dependency management. All dependencies are specified in the `dependencies` section of the `pyproject.toml` file.

To add a new dependency:

1. Add it to the `dependencies` list in `pyproject.toml`
2. Reinstall the package with `pip install -e .`

### Adding New Modules and Functions

To add a new GCP function to an existing module:

1. Locate the appropriate module in the `gcp_modules` directory
2. Add your function to the `register_tools` function in the module's `tools.py` file
3. Ensure the function has a descriptive docstring with proper parameters and return types

To add a completely new module:

1. Create a new directory in the `gcp_modules` directory
2. Create `__init__.py` and `tools.py` files in the new directory
3. Implement the `register_tools` function in `tools.py`
4. Add the module import and registration to `app.py`

### Adding New Tests

1. Create a new test file in the `tests/unit/` directory
2. Import the functions you want to test from the appropriate module
3. Write test functions using pytest's conventions
4. Use mocking to avoid making actual API calls during testing

### Running Tests in CI/CD

The tests are configured to run in CI/CD pipelines. The configuration is in the `pytest.ini` file.

## Troubleshooting

### Import Errors

If you encounter import errors like `No module named 'google.cloud.monitoring_v3'` or `No module named 'google.cloud.serviceusage_v1'`, make sure you have installed all the required dependencies:

```bash
pip install -e .
```

Or reinstall the specific package:

```bash
pip install --upgrade google-cloud-monitoring
pip install --upgrade google-cloud-service-usage
```

### Authentication Errors

If you encounter authentication errors, make sure you have set up GCP authentication correctly:

```bash
gcloud auth login
gcloud auth application-default login
```

### Quota Project Warnings

If you see warnings like "Your application has authenticated using end user credentials from Google Cloud SDK without a quota project", use the `set_quota_project` function to set a quota project:

```python
set_quota_project(project_id="your-project-id")
```

This will ensure your API requests are properly attributed for quota purposes.

### Server Startup Issues

If you have issues starting the MCP server, try:

```bash
# Check if the port is already in use
lsof -i :8080

# Use a different port
uvicorn app:mcp --port 8081
```

## Dependencies

The project dependencies are listed in the `pyproject.toml` file. You can install them using:

```bash
pip install -e .
```

## Summary

This project demonstrates:

1. **GCP API Integration**: Implementation of Google Cloud Platform services organized into logical modules covering different aspects of GCP.

2. **Modular Architecture**: A clean, modular design that allows for easy extension and maintenance.

3. **MCP Integration**: Integration with the Model Calling Protocol to allow AI assistants to interact with GCP.

4. **Best Practices**:
   - Proper error handling
   - Asynchronous programming where appropriate
   - Modular code organization
   - Comprehensive docstrings and typing

## License

[MIT License](LICENSE)