"""
ClickUp Agent for The Elidoras Codex.
Handles interactions with the ClickUp API for task management.
"""
import os
import requests
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_agent import BaseAgent

class ClickUpAgent(BaseAgent):
    """
    ClickUpAgent handles interactions with the ClickUp API.
    It retrieves tasks, updates statuses, and manages workflows in ClickUp.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        super().__init__("ClickUpAgent", config_path)
        self.logger.info("ClickUpAgent initialized")
        
        # Initialize ClickUp API credentials
        self.api_token = os.getenv("CLICKUP_API_TOKEN")
        if not self.api_token:
            self.logger.warning("ClickUp API token not found in environment variables.")
        
        self.list_id = os.getenv("CLICKUP_LIST_ID")
        if not self.list_id:
            self.logger.warning("ClickUp List ID not found in environment variables.")
        
        # ClickUp API base URL
        self.api_base_url = "https://api.clickup.com/api/v2"
    
    def get_tasks(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve tasks from ClickUp.
        
        Args:
            status: Optional status filter for tasks
        
        Returns:
            List of tasks from ClickUp
        """
        if not self.api_token or not self.list_id:
            self.logger.error("Cannot get tasks: ClickUp API credentials not configured")
            return []
        
        try:
            # Prepare API request
            url = f"{self.api_base_url}/list/{self.list_id}/task"
            headers = {"Authorization": self.api_token}
            params = {}
            
            if status:
                params["statuses[]"] = status
            
            # Make the API request
            self.logger.info(f"Retrieving tasks from ClickUp list {self.list_id}")
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            tasks = response.json().get("tasks", [])
            self.logger.info(f"Retrieved {len(tasks)} tasks from ClickUp")
            return tasks
        except Exception as e:
            self.logger.error(f"Failed to get tasks from ClickUp: {e}")
            return []
    
    def update_task_status(self, task_id: str, status: str) -> bool:
        """
        Update the status of a task in ClickUp.
        
        Args:
            task_id: ID of the task to update
            status: New status for the task
        
        Returns:
            Boolean indicating success or failure
        """
        if not self.api_token:
            self.logger.error("Cannot update task: ClickUp API token not configured")
            return False
        
        try:
            # Prepare API request
            url = f"{self.api_base_url}/task/{task_id}"
            headers = {
                "Authorization": self.api_token,
                "Content-Type": "application/json"
            }
            data = {"status": status}
            
            # Make the API request
            self.logger.info(f"Updating task {task_id} status to '{status}'")
            response = requests.put(url, headers=headers, json=data)
            response.raise_for_status()
            
            self.logger.info(f"Successfully updated task {task_id} status")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update task {task_id}: {e}")
            return False
    
    def add_comment_to_task(self, task_id: str, comment: str) -> bool:
        """
        Add a comment to a task in ClickUp.
        
        Args:
            task_id: ID of the task
            comment: Comment text to add
        
        Returns:
            Boolean indicating success or failure
        """
        if not self.api_token:
            self.logger.error("Cannot add comment: ClickUp API token not configured")
            return False
        
        try:
            # Prepare API request
            url = f"{self.api_base_url}/task/{task_id}/comment"
            headers = {
                "Authorization": self.api_token,
                "Content-Type": "application/json"
            }
            data = {"comment_text": comment}
            
            # Make the API request
            self.logger.info(f"Adding comment to task {task_id}")
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            self.logger.info(f"Successfully added comment to task {task_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add comment to task {task_id}: {e}")
            return False
    
    def run(self) -> Dict[str, Any]:
        """
        Execute the main ClickUpAgent workflow.
        
        Returns:
            Results of the ClickUpAgent execution
        """
        self.logger.info("Starting ClickUpAgent workflow")
        
        results = {
            "status": "success",
            "tasks_retrieved": 0,
            "errors": []
        }
        
        try:
            # Get tasks from ClickUp
            tasks = self.get_tasks()
            results["tasks_retrieved"] = len(tasks)
            
            # Example processing for demonstration
            for task in tasks:
                task_id = task.get("id")
                title = task.get("name")
                self.logger.info(f"Processing task: {title} ({task_id})")
                
                # Here you would implement your business logic for task processing
                
            self.logger.info("ClickUpAgent workflow completed successfully")
        except Exception as e:
            self.logger.error(f"ClickUpAgent workflow failed: {e}")
            results["status"] = "error"
            results["errors"].append(str(e))
        
        return results

if __name__ == "__main__":
    # Create and run the ClickUpAgent
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                              "config", "config.yaml")
    agent = ClickUpAgent(config_path)
    results = agent.run()
    
    print(f"ClickUpAgent execution completed with status: {results['status']}")
    print(f"Tasks retrieved: {results['tasks_retrieved']}")
    
    if results["errors"]:
        print("Errors encountered:")
        for error in results["errors"]:
            print(f" - {error}")