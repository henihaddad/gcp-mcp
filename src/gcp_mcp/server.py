from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Import all modules
from .gcp_modules.resource_management import tools as resource_tools
from .gcp_modules.iam import tools as iam_tools
from .gcp_modules.compute import tools as compute_tools
from .gcp_modules.storage import tools as storage_tools
from .gcp_modules.billing import tools as billing_tools
from .gcp_modules.networking import tools as networking_tools
from .gcp_modules.kubernetes import tools as kubernetes_tools
from .gcp_modules.monitoring import tools as monitoring_tools
from .gcp_modules.databases import tools as databases_tools
from .gcp_modules.deployment import tools as deployment_tools
from .gcp_modules.auth import tools as auth_tools

# Initialize FastMCP server
mcp = FastMCP("gcp")

# A simple test function
@mcp.tool()
async def say_hello(name: str) -> str:
    """Say hello to a person."""
    return f"Hello, {name}!"

# Register all module tools
def register_tools():
    # Register authentication tools (placed first for visibility)
    auth_tools.register_tools(mcp)
    
    # Register resource management tools
    resource_tools.register_tools(mcp)
    
    # Register IAM tools
    iam_tools.register_tools(mcp)
    
    # Register compute tools
    compute_tools.register_tools(mcp)
    
    # Register storage tools
    storage_tools.register_tools(mcp)
    
    # Register billing tools
    billing_tools.register_tools(mcp)
    
    # Register networking tools
    networking_tools.register_tools(mcp)
    
    # Register kubernetes tools
    kubernetes_tools.register_tools(mcp)
    
    # Register monitoring tools
    monitoring_tools.register_tools(mcp)
    
    # Register databases tools
    databases_tools.register_tools(mcp)
    
    # Register deployment tools
    deployment_tools.register_tools(mcp)

# Register all tools
register_tools()

# if __name__ == "__main__":
#     mcp.run(transport='stdio')