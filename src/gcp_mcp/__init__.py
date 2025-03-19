from . import server
import asyncio
import os
import sys

def main():
    server.mcp.run(transport='stdio')

__all__ = ['main', 'server']