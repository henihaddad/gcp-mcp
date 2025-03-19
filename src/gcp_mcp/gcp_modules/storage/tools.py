"""
Google Cloud Platform Storage tools.
"""
from typing import List, Dict, Any, Optional

def register_tools(mcp):
    """Register all storage tools with the MCP server."""
    
    @mcp.tool()
    def list_storage_buckets(project_id: str) -> str:
        """
        List Cloud Storage buckets in a GCP project.
        
        Args:
            project_id: The ID of the GCP project to list buckets for
        
        Returns:
            List of Cloud Storage buckets in the specified GCP project
        """
        try:
            from google.cloud import storage
            
            # Initialize the Storage client
            client = storage.Client(project=project_id)
            
            # List buckets
            buckets = client.list_buckets()
            
            # Format the response
            buckets_list = []
            for bucket in buckets:
                location = bucket.location or "Unknown"
                storage_class = bucket.storage_class or "Unknown"
                created = bucket.time_created.strftime("%Y-%m-%d %H:%M:%S UTC") if bucket.time_created else "Unknown"
                buckets_list.append(f"- {bucket.name} (Location: {location}, Class: {storage_class}, Created: {created})")
            
            if not buckets_list:
                return f"No Cloud Storage buckets found in project {project_id}."
            
            buckets_str = "\n".join(buckets_list)
            
            return f"""
Cloud Storage Buckets in GCP Project {project_id}:
{buckets_str}
"""
        except Exception as e:
            return f"Error listing Cloud Storage buckets: {str(e)}"
    
    @mcp.tool()
    def get_bucket_details(project_id: str, bucket_name: str) -> str:
        """
        Get detailed information about a specific Cloud Storage bucket.
        
        Args:
            project_id: The ID of the GCP project
            bucket_name: The name of the bucket to get details for
        
        Returns:
            Detailed information about the specified Cloud Storage bucket
        """
        try:
            from google.cloud import storage
            
            # Initialize the Storage client
            client = storage.Client(project=project_id)
            
            # Get the bucket
            bucket = client.get_bucket(bucket_name)
            
            # Format the response
            details = []
            details.append(f"Name: {bucket.name}")
            details.append(f"Project: {project_id}")
            details.append(f"Location: {bucket.location or 'Unknown'}")
            details.append(f"Storage Class: {bucket.storage_class or 'Unknown'}")
            details.append(f"Created: {bucket.time_created.strftime('%Y-%m-%d %H:%M:%S UTC') if bucket.time_created else 'Unknown'}")
            details.append(f"Versioning Enabled: {bucket.versioning_enabled}")
            details.append(f"Requester Pays: {bucket.requester_pays}")
            details.append(f"Lifecycle Rules: {len(bucket.lifecycle_rules) if bucket.lifecycle_rules else 0} rules defined")
            details.append(f"Labels: {bucket.labels or 'None'}")
            details.append(f"CORS: {bucket.cors or 'None'}")
            
            details_str = "\n".join(details)
            
            return f"""
Cloud Storage Bucket Details:
{details_str}
"""
        except Exception as e:
            return f"Error getting bucket details: {str(e)}"
    
    @mcp.tool()
    def list_objects(project_id: str, bucket_name: str, prefix: Optional[str] = None, limit: int = 100) -> str:
        """
        List objects in a Cloud Storage bucket.
        
        Args:
            project_id: The ID of the GCP project
            bucket_name: The name of the bucket to list objects from
            prefix: Optional prefix to filter objects by
            limit: Maximum number of objects to list (default: 100)
        
        Returns:
            List of objects in the specified Cloud Storage bucket
        """
        try:
            from google.cloud import storage
            
            # Initialize the Storage client
            client = storage.Client(project=project_id)
            
            # Get the bucket
            bucket = client.get_bucket(bucket_name)
            
            # List blobs
            blobs = bucket.list_blobs(prefix=prefix, max_results=limit)
            
            # Format the response
            objects_list = []
            for blob in blobs:
                size_mb = blob.size / (1024 * 1024)
                updated = blob.updated.strftime("%Y-%m-%d %H:%M:%S UTC") if blob.updated else "Unknown"
                objects_list.append(f"- {blob.name} (Size: {size_mb:.2f} MB, Updated: {updated}, Content-Type: {blob.content_type})")
            
            if not objects_list:
                return f"No objects found in bucket {bucket_name}{' with prefix ' + prefix if prefix else ''}."
            
            objects_str = "\n".join(objects_list)
            
            return f"""
Objects in Cloud Storage Bucket {bucket_name}{' with prefix ' + prefix if prefix else ''}:
{objects_str}
"""
        except Exception as e:
            return f"Error listing objects: {str(e)}"
    
    @mcp.tool()
    def upload_object(project_id: str, bucket_name: str, source_file_path: str, destination_blob_name: Optional[str] = None, content_type: Optional[str] = None) -> str:
        """
        Upload a file to a Cloud Storage bucket.
        
        Args:
            project_id: The ID of the GCP project
            bucket_name: The name of the bucket to upload to
            source_file_path: The local file path to upload
            destination_blob_name: The name to give the file in GCS (default: filename from source)
            content_type: The content type of the file (default: auto-detect)
        
        Returns:
            Result of the upload operation
        """
        try:
            import os
            from google.cloud import storage
            
            # Initialize the Storage client
            client = storage.Client(project=project_id)
            
            # Get the bucket
            bucket = client.get_bucket(bucket_name)
            
            # If no destination name is provided, use the source filename
            if not destination_blob_name:
                destination_blob_name = os.path.basename(source_file_path)
            
            # Create a blob object
            blob = bucket.blob(destination_blob_name)
            
            # Upload the file
            blob.upload_from_filename(source_file_path, content_type=content_type)
            
            return f"""
File successfully uploaded:
- Source: {source_file_path}
- Destination: gs://{bucket_name}/{destination_blob_name}
- Size: {blob.size / (1024 * 1024):.2f} MB
- Content-Type: {blob.content_type}
"""
        except Exception as e:
            return f"Error uploading file: {str(e)}"
    
    @mcp.tool()
    def download_object(project_id: str, bucket_name: str, source_blob_name: str, destination_file_path: str) -> str:
        """
        Download a file from a Cloud Storage bucket.
        
        Args:
            project_id: The ID of the GCP project
            bucket_name: The name of the bucket to download from
            source_blob_name: The name of the file in the bucket
            destination_file_path: The local path to save the file to
        
        Returns:
            Result of the download operation
        """
        try:
            from google.cloud import storage
            
            # Initialize the Storage client
            client = storage.Client(project=project_id)
            
            # Get the bucket
            bucket = client.get_bucket(bucket_name)
            
            # Get the blob
            blob = bucket.blob(source_blob_name)
            
            # Download the file
            blob.download_to_filename(destination_file_path)
            
            return f"""
File successfully downloaded:
- Source: gs://{bucket_name}/{source_blob_name}
- Destination: {destination_file_path}
- Size: {blob.size / (1024 * 1024):.2f} MB
- Content-Type: {blob.content_type}
"""
        except Exception as e:
            return f"Error downloading file: {str(e)}"
    
    @mcp.tool()
    def delete_object(project_id: str, bucket_name: str, blob_name: str) -> str:
        """
        Delete an object from a Cloud Storage bucket.
        
        Args:
            project_id: The ID of the GCP project
            bucket_name: The name of the bucket to delete from
            blob_name: The name of the file to delete
        
        Returns:
            Result of the delete operation
        """
        try:
            from google.cloud import storage
            
            # Initialize the Storage client
            client = storage.Client(project=project_id)
            
            # Get the bucket
            bucket = client.get_bucket(bucket_name)
            
            # Delete the blob
            blob = bucket.blob(blob_name)
            blob.delete()
            
            return f"Object gs://{bucket_name}/{blob_name} has been successfully deleted."
        except Exception as e:
            return f"Error deleting object: {str(e)}"