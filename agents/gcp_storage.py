"""
Google Cloud Storage integration for The Elidoras Codex.
Handles storage and retrieval of files using Google Cloud Storage.
"""
import os
import logging
from typing import Dict, Any, Optional, BinaryIO
from datetime import datetime

from google.cloud import storage
from google.oauth2 import service_account
from .base_agent import BaseAgent

class GCPStorageAgent(BaseAgent):
    """
    GCPStorageAgent handles interactions with Google Cloud Storage.
    It uploads, downloads, and manages files in GCP buckets.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        super().__init__("GCPStorageAgent", config_path)
        self.logger.info("GCPStorageAgent initialized")
        
        # Initialize GCP credentials
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.bucket_name = os.getenv("GCP_BUCKET_NAME")
        
        if not self.project_id:
            self.logger.warning("GCP Project ID not found in environment variables")
        
        if not self.bucket_name:
            self.logger.warning("GCP Bucket Name not found in environment variables")
        
        # Initialize GCP client
        self.storage_client = None
        self.bucket = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize the Google Cloud Storage client."""
        try:
            # Check if GOOGLE_APPLICATION_CREDENTIALS is set
            if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
                self.logger.warning("GOOGLE_APPLICATION_CREDENTIALS not set. Using default authentication.")
            
            # Initialize the client
            self.storage_client = storage.Client(project=self.project_id)
            
            # Get or create the bucket
            try:
                self.bucket = self.storage_client.get_bucket(self.bucket_name)
                self.logger.info(f"Connected to bucket: {self.bucket_name}")
            except Exception as e:
                self.logger.error(f"Failed to get bucket: {e}")
                self.bucket = None
                
        except Exception as e:
            self.logger.error(f"Failed to initialize GCP storage client: {e}")
            self.storage_client = None
    
    def upload_file(self, file_path: str, destination_blob_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload a file to GCP Storage.
        
        Args:
            file_path: Path to the local file
            destination_blob_name: Name of the blob in GCP (if None, uses file name)
            
        Returns:
            Dictionary with upload status and URL
        """
        if not self.bucket:
            self.logger.error("Bucket not initialized")
            return {"success": False, "error": "Bucket not initialized"}
        
        try:
            # If no destination name provided, use the file name
            if not destination_blob_name:
                destination_blob_name = os.path.basename(file_path)
            
            # Create a blob and upload
            blob = self.bucket.blob(destination_blob_name)
            blob.upload_from_filename(file_path)
            
            # Generate a URL for the file
            url = f"https://storage.googleapis.com/{self.bucket_name}/{destination_blob_name}"
            
            self.logger.info(f"File {file_path} uploaded to {destination_blob_name}")
            return {
                "success": True,
                "url": url,
                "blob_name": destination_blob_name
            }
            
        except Exception as e:
            self.logger.error(f"Failed to upload file {file_path}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def download_file(self, blob_name: str, destination_file_path: str) -> Dict[str, Any]:
        """
        Download a file from GCP Storage.
        
        Args:
            blob_name: Name of the blob in GCP
            destination_file_path: Local path to save the file
            
        Returns:
            Dictionary with download status
        """
        if not self.bucket:
            self.logger.error("Bucket not initialized")
            return {"success": False, "error": "Bucket not initialized"}
        
        try:
            # Create a blob and download
            blob = self.bucket.blob(blob_name)
            blob.download_to_filename(destination_file_path)
            
            self.logger.info(f"Blob {blob_name} downloaded to {destination_file_path}")
            return {
                "success": True,
                "file_path": destination_file_path
            }
            
        except Exception as e:
            self.logger.error(f"Failed to download blob {blob_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_files(self, prefix: Optional[str] = None) -> Dict[str, Any]:
        """
        List files in the GCP bucket.
        
        Args:
            prefix: Optional prefix to filter files
            
        Returns:
            Dictionary with list of files
        """
        if not self.bucket:
            self.logger.error("Bucket not initialized")
            return {"success": False, "error": "Bucket not initialized"}
        
        try:
            blobs = list(self.bucket.list_blobs(prefix=prefix))
            file_list = [
                {"name": blob.name, 
                 "size": blob.size, 
                 "updated": blob.updated.isoformat() if blob.updated else None} 
                for blob in blobs
            ]
            
            self.logger.info(f"Listed {len(file_list)} files in bucket {self.bucket_name}")
            return {
                "success": True,
                "files": file_list
            }
            
        except Exception as e:
            self.logger.error(f"Failed to list files: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def backup_wordpress_data(self, content_data: Dict[str, Any], backup_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Backup WordPress post data to GCP Storage.
        
        Args:
            content_data: Dictionary of WordPress post data
            backup_name: Optional custom backup name
            
        Returns:
            Dictionary with backup status and URL
        """
        try:
            import json
            import tempfile
            
            # Create a temporary file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if not backup_name:
                backup_name = f"wp_backup_{timestamp}.json"
            else:
                if not backup_name.endswith('.json'):
                    backup_name += '.json'
            
            # Write the data to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json') as temp_file:
                json.dump(content_data, temp_file, indent=2)
                temp_path = temp_file.name
            
            # Upload the file
            result = self.upload_file(temp_path, f"backups/{backup_name}")
            
            # Delete the temporary file
            os.unlink(temp_path)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to backup WordPress data: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def run(self) -> Dict[str, Any]:
        """
        Run the agent's main logic.
        
        Returns:
            Dictionary with agent execution results
        """
        self.logger.info("Running GCPStorageAgent")
        
        if not self.bucket:
            return {
                "status": "error",
                "message": "GCP Storage not initialized properly"
            }
        
        results = {
            "status": "success",
            "files_count": 0,
            "bucket_name": self.bucket_name
        }
        
        try:
            # List files as a test
            file_list_result = self.list_files()
            if file_list_result["success"]:
                results["files_count"] = len(file_list_result["files"])
                self.logger.info(f"Found {results['files_count']} files in bucket")
            else:
                results["status"] = "warning"
                results["message"] = "Failed to list files"
            
        except Exception as e:
            self.logger.error(f"Error in GCPStorageAgent run: {e}")
            results["status"] = "error"
            results["message"] = str(e)
        
        return results

if __name__ == "__main__":
    # Create and run the agent
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                               "config", "config.yaml")
    agent = GCPStorageAgent(config_path)
    results = agent.run()
    
    print(f"GCPStorageAgent execution completed with status: {results['status']}")
    print(f"Files in bucket: {results.get('files_count', 'unknown')}")