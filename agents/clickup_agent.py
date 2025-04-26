"""
ClickUp Agent for The Elidoras Codex.
Handles interactions with the ClickUp API for task management and AI-driven automation.
"""
import os
import requests
import logging
import json
import time
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from .base_agent import BaseAgent

class ClickUpAgent(BaseAgent):
    """
    ClickUpAgent handles interactions with the ClickUp API.
    It retrieves tasks, updates statuses, and manages workflows in ClickUp.
    Implements advanced AI-driven automation for The Elidoras Codex project.
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
        
        # Workspace ID
        self.workspace_id = os.getenv("CLICKUP_WORKSPACE_ID")
        if not self.workspace_id:
            self.logger.warning("ClickUp Workspace ID not found in environment variables.")
        
        # Load TEC-specific configurations
        self._load_tec_config()
    
    def _load_tec_config(self):
        """
        Load TEC-specific configurations from the config file.
        """
        try:
            # Custom field IDs
            self.custom_fields = {
                "task_sentiment": self.config.get("clickup", {}).get("custom_fields", {}).get("task_sentiment"),
                "ai_task_brief": self.config.get("clickup", {}).get("custom_fields", {}).get("ai_task_brief"),
                "airth_actions": self.config.get("clickup", {}).get("custom_fields", {}).get("airth_actions")
            }
            
            # Status mappings
            self.statuses = {
                "open": self.config.get("clickup", {}).get("statuses", {}).get("open"),
                "ai_analysis": self.config.get("clickup", {}).get("statuses", {}).get("ai_analysis"),
                "subtasks_pending": self.config.get("clickup", {}).get("statuses", {}).get("subtasks_pending"),
                "checklist_pending": self.config.get("clickup", {}).get("statuses", {}).get("checklist_pending"),
                "tec_data_drop": self.config.get("clickup", {}).get("statuses", {}).get("tec_data_drop"),
                "polkin_pre_deploy": self.config.get("clickup", {}).get("statuses", {}).get("polkin_pre_deploy")
            }
            
            # Trigger tags
            self.trigger_tags = self.config.get("clickup", {}).get("trigger_tags", [
                "ai-alpha-commence-assessment",
                "1st drop",
                "content",
                "automation",
                "ai-collab"
            ])
            
            # Team members
            self.team_members = self.config.get("clickup", {}).get("team_members", {})
            
            self.logger.info("TEC-specific configuration loaded")
        except Exception as e:
            self.logger.error(f"Failed to load TEC configuration: {e}")
    
    def get_tasks(self, status: Optional[str] = None, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Retrieve tasks from ClickUp.
        
        Args:
            status: Optional status filter for tasks
            tags: Optional list of tags to filter by
        
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
            
            if tags:
                for tag in tags:
                    params["tags[]"] = tag
            
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
    
    def update_custom_field(self, task_id: str, field_id: str, field_value: Any) -> bool:
        """
        Update a custom field value for a task in ClickUp.
        
        Args:
            task_id: ID of the task
            field_id: ID of the custom field
            field_value: New value for the custom field
            
        Returns:
            Boolean indicating success or failure
        """
        if not self.api_token:
            self.logger.error("Cannot update custom field: ClickUp API token not configured")
            return False
        
        try:
            # Prepare API request
            url = f"{self.api_base_url}/task/{task_id}/field/{field_id}"
            headers = {
                "Authorization": self.api_token,
                "Content-Type": "application/json"
            }
            data = {"value": field_value}
            
            # Make the API request
            self.logger.info(f"Updating custom field {field_id} for task {task_id}")
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            self.logger.info(f"Successfully updated custom field for task {task_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update custom field for task {task_id}: {e}")
            return False
    
    def create_subtask(self, parent_id: str, name: str, description: str = "", 
                       assignees: List[str] = None, status: str = None) -> Optional[str]:
        """
        Create a subtask for a parent task in ClickUp.
        
        Args:
            parent_id: ID of the parent task
            name: Name of the subtask
            description: Description of the subtask
            assignees: List of user IDs to assign to the task
            status: Status of the task
        
        Returns:
            ID of the created subtask if successful, None otherwise
        """
        if not self.api_token:
            self.logger.error("Cannot create subtask: ClickUp API token not configured")
            return None
        
        try:
            # Prepare API request
            url = f"{self.api_base_url}/list/{self.list_id}/task"
            headers = {
                "Authorization": self.api_token,
                "Content-Type": "application/json"
            }
            
            data = {
                "name": name,
                "description": description,
                "parent": parent_id
            }
            
            if assignees:
                data["assignees"] = assignees
            
            if status:
                data["status"] = status
            
            # Make the API request
            self.logger.info(f"Creating subtask for parent task {parent_id}")
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            subtask_id = response.json().get("id")
            self.logger.info(f"Successfully created subtask {subtask_id}")
            return subtask_id
        except Exception as e:
            self.logger.error(f"Failed to create subtask for parent task {parent_id}: {e}")
            return None
    
    def create_task_from_template(self, template: Dict[str, Any]) -> Optional[str]:
        """
        Create a task in ClickUp based on a template.
        
        Args:
            template: Template data for the task
            
        Returns:
            ID of the created task if successful, None otherwise
        """
        if not self.api_token or not self.list_id:
            self.logger.error("Cannot create task: ClickUp API credentials not configured")
            return None
        
        try:
            # Prepare API request
            url = f"{self.api_base_url}/list/{self.list_id}/task"
            headers = {
                "Authorization": self.api_token,
                "Content-Type": "application/json"
            }
            
            data = {
                "name": template.get("name", "New Task"),
                "description": template.get("description", ""),
                "tags": template.get("tags", []),
                "status": template.get("status", "Open"),
                "priority": template.get("priority", 3)
            }
            
            assignees = template.get("assignees")
            if assignees:
                # Convert names to IDs if needed
                assignee_ids = []
                for assignee in assignees:
                    if assignee in self.team_members:
                        assignee_ids.append(self.team_members[assignee])
                    else:
                        assignee_ids.append(assignee)
                data["assignees"] = assignee_ids
            
            # Make the API request
            self.logger.info(f"Creating task from template")
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            task_id = response.json().get("id")
            
            # If task created successfully and template has checklist items
            if task_id and template.get("checklist"):
                self._add_checklist_to_task(task_id, template["checklist"])
            
            self.logger.info(f"Successfully created task {task_id}")
            return task_id
        except Exception as e:
            self.logger.error(f"Failed to create task from template: {e}")
            return None
    
    def _add_checklist_to_task(self, task_id: str, checklist_items: List[Dict[str, Any]]) -> bool:
        """
        Add checklist items to a task.
        
        Args:
            task_id: ID of the task
            checklist_items: List of checklist items to add
            
        Returns:
            Boolean indicating success or failure
        """
        try:
            # First create a checklist
            url = f"{self.api_base_url}/task/{task_id}/checklist"
            headers = {
                "Authorization": self.api_token,
                "Content-Type": "application/json"
            }
            data = {"name": "Action Items"}
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            checklist_id = response.json().get("id")
            
            # Then add each checklist item
            for item in checklist_items:
                item_url = f"{self.api_base_url}/checklist/{checklist_id}/checklist_item"
                item_data = {
                    "name": item.get("name"),
                    "resolved": item.get("resolved", False)
                }
                
                if "orderindex" in item:
                    item_data["orderindex"] = item["orderindex"]
                
                requests.post(item_url, headers=headers, json=item_data)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to add checklist to task {task_id}: {e}")
            return False
    
    def create_doc(self, title: str, content: str, parent_id: str = None) -> Optional[str]:
        """
        Create a ClickUp Doc and optionally attach it to a task.
        
        Args:
            title: Title of the document
            content: Content of the document in HTML format
            parent_id: Optional ID of the parent task to attach the doc to
            
        Returns:
            ID of the created doc if successful, None otherwise
        """
        if not self.api_token or not self.workspace_id:
            self.logger.error("Cannot create doc: ClickUp API credentials not configured")
            return None
        
        try:
            # Create the doc
            url = f"{self.api_base_url}/team/{self.workspace_id}/view"
            headers = {
                "Authorization": self.api_token,
                "Content-Type": "application/json"
            }
            data = {
                "name": title,
                "type": "doc",
                "content": {
                    "type": "doc",
                    "content": content
                }
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            doc_id = response.json().get("id")
            self.logger.info(f"Successfully created doc {doc_id}")
            
            # If a parent task ID is provided, attach the doc to the task
            if parent_id and doc_id:
                self._attach_doc_to_task(doc_id, parent_id)
            
            return doc_id
        except Exception as e:
            self.logger.error(f"Failed to create doc: {e}")
            return None
    
    def _attach_doc_to_task(self, doc_id: str, task_id: str) -> bool:
        """
        Attach a doc to a task.
        
        Args:
            doc_id: ID of the doc
            task_id: ID of the task
            
        Returns:
            Boolean indicating success or failure
        """
        if not self.api_token:
            return False
        
        try:
            url = f"{self.api_base_url}/task/{task_id}/relationship"
            headers = {
                "Authorization": self.api_token,
                "Content-Type": "application/json"
            }
            data = {
                "links_to": doc_id,
                "relationship_type": "doc"
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            self.logger.info(f"Successfully attached doc {doc_id} to task {task_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to attach doc to task: {e}")
            return False
    
    def find_related_tasks(self, task_id: str, keywords: List[str] = None, 
                           tags: List[str] = None) -> List[Dict[str, Any]]:
        """
        Find tasks related to a given task based on keywords and tags.
        
        Args:
            task_id: ID of the task to find relations for
            keywords: List of keywords to search for in task names and descriptions
            tags: List of tags to filter by
            
        Returns:
            List of related tasks
        """
        if not self.api_token or not self.list_id:
            self.logger.error("Cannot find related tasks: ClickUp API credentials not configured")
            return []
        
        # Get all tasks from the list
        all_tasks = self.get_tasks()
        current_task = None
        
        # Find the current task
        for task in all_tasks:
            if task.get("id") == task_id:
                current_task = task
                break
        
        if not current_task:
            self.logger.error(f"Could not find task {task_id}")
            return []
        
        # Build a list of related tasks
        related_tasks = []
        
        for task in all_tasks:
            # Skip the current task
            if task.get("id") == task_id:
                continue
            
            score = 0
            
            # Check tags
            if tags:
                task_tags = [tag.get("name") for tag in task.get("tags", [])]
                for tag in tags:
                    if tag in task_tags:
                        score += 3  # Higher weight for tag matches
            
            # Check keywords
            if keywords:
                task_name = task.get("name", "").lower()
                task_description = task.get("description", "").lower()
                
                for keyword in keywords:
                    kw = keyword.lower()
                    if kw in task_name:
                        score += 2  # Higher weight for name matches
                    if kw in task_description:
                        score += 1  # Lower weight for description matches
            
            # If the task has a decent match score, add it to related tasks
            if score >= 3:  # Threshold can be adjusted
                related_tasks.append(task)
        
        self.logger.info(f"Found {len(related_tasks)} related tasks for task {task_id}")
        return related_tasks
    
    def process_ai_assessment_trigger(self, task_id: str) -> Dict[str, Any]:
        """
        Process an AI assessment trigger for a task.
        This implements the first automation step in the workflow.
        
        Args:
            task_id: ID of the task
            
        Returns:
            Results of the processing
        """
        results = {
            "status": "success",
            "task_id": task_id,
            "actions_performed": [],
            "errors": []
        }
        
        try:
            # Get task details
            task_url = f"{self.api_base_url}/task/{task_id}"
            headers = {"Authorization": self.api_token}
            response = requests.get(task_url, headers)
            response.raise_for_status()
            
            task = response.json()
            
            # Step 1: Update task status to AI Analysis
            if self.update_task_status(task_id, self.statuses.get("ai_analysis", "AI Analysis")):
                results["actions_performed"].append("Updated status to AI Analysis")
            else:
                results["errors"].append("Failed to update task status")
            
            # Step 2: Get task creator ID
            creator_id = task.get("creator", {}).get("id")
            if creator_id:
                # Assign task to creator
                assign_url = f"{self.api_base_url}/task/{task_id}"
                assign_data = {"assignees": [creator_id]}
                assign_response = requests.put(assign_url, headers={**headers, "Content-Type": "application/json"}, json=assign_data)
                
                if assign_response.status_code == 200:
                    results["actions_performed"].append("Assigned task to creator")
                else:
                    results["errors"].append("Failed to assign task to creator")
            
            # Step 3: Fill Task Sentiment field with AI
            # Note: This would typically be filled by ClickUp's AI directly
            # For our agent, we'll add a comment noting that this would be done
            task_details = f"Task Name: {task.get('name')}\nDescription: {task.get('description')}"
            self.add_comment_to_task(
                task_id, 
                "🤖 ClickUpAgent: AI would analyze the Task Sentiment here. (Simulated field update)"
            )
            results["actions_performed"].append("Added comment about Task Sentiment analysis")
            
            # Step 4: Fill AI Task Brief field with AI
            # Again, we're simulating this with a comment
            self.add_comment_to_task(
                task_id, 
                "🤖 ClickUpAgent: AI would generate a Task Brief here. (Simulated field update)"
            )
            results["actions_performed"].append("Added comment about AI Task Brief generation")
            
            # Step 5: Add a general AI-Processing tag
            tags_url = f"{self.api_base_url}/task/{task_id}"
            tags = [tag.get("name") for tag in task.get("tags", [])]
            tags.append("AI-Processing")
            tags_data = {"tags": tags}
            
            tags_response = requests.put(tags_url, headers={**headers, "Content-Type": "application/json"}, json=tags_data)
            if tags_response.status_code == 200:
                results["actions_performed"].append("Added AI-Processing tag")
            else:
                results["errors"].append("Failed to add AI-Processing tag")
                
            # Step 6: Based on task content, determine if AI Needed
            # This is a simulation - in real use this would be determined by the Task Sentiment field
            # We'll assume AI is needed and continue the workflow by adding a comment
            self.add_comment_to_task(
                task_id, 
                "🛡️ Airth requires intervention. Review related tasks based on tags and content brief. Define necessary subtasks manually."
            )
            results["actions_performed"].append("Added Airth intervention comment")
            
            # Further steps would be triggered by status changes or custom field updates in ClickUp
            
        except Exception as e:
            self.logger.error(f"Failed to process AI assessment trigger for task {task_id}: {e}")
            results["status"] = "error"
            results["errors"].append(str(e))
        
        return results
    
    def generate_lore_doc(self, task_id: str) -> Dict[str, Any]:
        """
        Generate a lore document from a task and its related content.
        This implements the final step in the complex automation workflow.
        
        Args:
            task_id: ID of the task
            
        Returns:
            Results of the document generation
        """
        results = {
            "status": "success",
            "task_id": task_id,
            "doc_created": False,
            "errors": []
        }
        
        try:
            # Get task details
            task_url = f"{self.api_base_url}/task/{task_id}"
            headers = {"Authorization": self.api_token}
            response = requests.get(task_url, headers)
            response.raise_for_status()
            
            task = response.json()
            
            # Get task comments
            comments_url = f"{self.api_base_url}/task/{task_id}/comment"
            comments_response = requests.get(comments_url, headers)
            comments_response.raise_for_status()
            
            comments = comments_response.json().get("comments", [])
            
            # Get subtasks
            subtasks_url = f"{self.api_base_url}/task/{task_id}/subtask"
            subtasks_response = requests.get(subtasks_url, headers)
            subtasks_response.raise_for_status()
            
            subtasks = subtasks_response.json().get("subtasks", [])
            
            # Get related tasks based on tags
            task_tags = [tag.get("name") for tag in task.get("tags", [])]
            related_tasks = self.find_related_tasks(task_id, tags=task_tags)
            
            # Extract task name for document title
            task_name = task.get("name", "Untitled Task")
            doc_title = f"TEC Lore Drop: {task_name}"
            
            # Build document content
            content = f"""
            <h1>TEC Lore Drop</h1>
            <h2>{task_name}</h2>
            <p><em>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}</em></p>
            
            <h3>Task Description</h3>
            <div>{task.get('description', 'No description provided.')}</div>
            
            <h3>Key Actions</h3>
            <ul>
            """
            
            # Add subtasks as action items
            for subtask in subtasks:
                subtask_name = subtask.get("name", "Unnamed subtask")
                subtask_status = subtask.get("status", {}).get("status", "Unknown")
                content += f"<li>{subtask_name} ({subtask_status})</li>"
            
            content += """
            </ul>
            
            <h3>Related Content</h3>
            <ul>
            """
            
            # Add related tasks
            for related_task in related_tasks:
                related_name = related_task.get("name", "Unnamed task")
                related_id = related_task.get("id", "")
                content += f"<li>{related_name} (ID: {related_id})</li>"
            
            content += """
            </ul>
            
            <h3>Discussion Highlights</h3>
            <div>
            """
            
            # Add key comments (limiting to last 5 for brevity)
            for comment in comments[-5:]:
                comment_text = comment.get("comment_text", "")
                comment_user = comment.get("user", {}).get("username", "Unknown")
                content += f"<p><strong>{comment_user}:</strong> {comment_text}</p>"
            
            content += """
            </div>
            
            <h3>Next Steps</h3>
            <p>This document requires review by Polkin Rishall before final integration into The Elidoras Codex.</p>
            """
            
            # Create the doc
            doc_id = self.create_doc(doc_title, content, task_id)
            
            if doc_id:
                results["doc_created"] = True
                results["doc_id"] = doc_id
                
                # Update task status to Polkin pre-deploy
                self.update_task_status(task_id, self.statuses.get("polkin_pre_deploy", "Polkin pre-deploy"))
                
                # Notify Polkin
                polkin_id = self.team_members.get("Polkin Rishall")
                if polkin_id:
                    notification = f"🔮 @{polkin_id} Airth Alert: Lore Drop Ready for Pre-Deploy Review - Task: {task_name}"
                    self.add_comment_to_task(task_id, notification)
            else:
                results["errors"].append("Failed to create lore doc")
            
        except Exception as e:
            self.logger.error(f"Failed to generate lore doc for task {task_id}: {e}")
            results["status"] = "error" 
            results["errors"].append(str(e))
        
        return results
    
    def bulk_import_tasks(self, tasks_json_file: str) -> Dict[str, Any]:
        """
        Import multiple tasks from a JSON file.
        
        Args:
            tasks_json_file: Path to the JSON file containing task templates
            
        Returns:
            Results of the import operation
        """
        results = {
            "status": "success",
            "tasks_created": 0,
            "failed_tasks": 0,
            "task_ids": [],
            "errors": []
        }
        
        try:
            # Read the JSON file
            with open(tasks_json_file, 'r') as f:
                data = json.load(f)
            
            tasks = data.get("tasks", [])
            self.logger.info(f"Importing {len(tasks)} tasks from {tasks_json_file}")
            
            # Create each task
            for task in tasks:
                task_id = self.create_task_from_template(task)
                if task_id:
                    results["tasks_created"] += 1
                    results["task_ids"].append(task_id)
                else:
                    results["failed_tasks"] += 1
                    results["errors"].append(f"Failed to create task: {task.get('name', 'Unnamed task')}")
            
            self.logger.info(f"Successfully imported {results['tasks_created']} tasks")
            
        except Exception as e:
            self.logger.error(f"Failed to import tasks: {e}")
            results["status"] = "error"
            results["errors"].append(str(e))
        
        return results
    
    def run(self) -> Dict[str, Any]:
        """
        Execute the main ClickUpAgent workflow.
        
        Returns:
            Results of the ClickUpAgent execution
        """
        self.logger.info("Starting ClickUpAgent workflow")
        
        results = {
            "status": "success",
            "tasks_processed": 0,
            "errors": []
        }
        
        try:
            # Step 1: Get tasks that have trigger tags
            tasks = []
            for tag in self.trigger_tags:
                tag_tasks = self.get_tasks(tags=[tag])
                tasks.extend(tag_tasks)
            
            results["tasks_found"] = len(tasks)
            self.logger.info(f"Found {len(tasks)} tasks with trigger tags")
            
            # Step 2: Process each task
            processed_tasks = []
            for task in tasks:
                task_id = task.get("id")
                
                # Skip already processed tasks
                if task_id in processed_tasks:
                    continue
                
                # Process task based on its status
                status = task.get("status", {}).get("status", "")
                
                if status in ["Open", "Unprocessed", ""]:
                    # Initial triage for new tasks
                    self.process_ai_assessment_trigger(task_id)
                    results["tasks_processed"] += 1
                    processed_tasks.append(task_id)
                
                # Additional workflow steps would be implemented here
                # In a real implementation, most of these would be triggered
                # by ClickUp's own automation system, with our agent handling
                # the complex parts
            
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
    print(f"Tasks processed: {results['tasks_processed']}")
    
    if results.get("errors"):
        print("Errors encountered:")
        for error in results["errors"]:
            print(f" - {error}")