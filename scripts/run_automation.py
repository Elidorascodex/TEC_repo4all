#!/usr/bin/env python
"""
TEC Automation Pipeline
This script runs the full automation pipeline for The Elidoras Codex:
1. Fetches tasks from ClickUp
2. Processes them with AI content enhancement
3. Posts the enhanced content to WordPress
"""
import os
import sys
import yaml
import logging
from typing import Dict, Any, List
from datetime import datetime

# Add parent directory to path to import agents
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

# Import agents
from agents.tecbot import TECBot
from agents.clickup_agent import ClickUpAgent
from agents.wp_poster import WordPressAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(script_dir, f"automation_{datetime.now().strftime('%Y%m%d')}.log"))
    ]
)
logger = logging.getLogger("TEC.Automation")

def load_config() -> Dict[str, Any]:
    """Load configuration from the config.yaml file"""
    config_path = os.path.join(parent_dir, "config", "config.yaml")
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Loaded configuration from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)

def run_pipeline(config: Dict[str, Any]) -> Dict[str, Any]:
    """Run the full automation pipeline"""
    logger.info("Starting TEC automation pipeline")
    results = {
        "status": "success",
        "tasks_processed": 0,
        "content_enhanced": 0,
        "posts_created": 0,
        "errors": []
    }
    
    try:
        # Initialize agents
        config_path = os.path.join(parent_dir, "config", "config.yaml")
        clickup_agent = ClickUpAgent(config_path)
        tecbot = TECBot(config_path)
        wp_agent = WordPressAgent(config_path)
        
        # Step 1: Get tasks from ClickUp
        ready_status = "Ready for Publishing"  # Or get from config
        tasks = clickup_agent.get_tasks(status=ready_status)
        
        if not tasks:
            logger.info(f"No tasks with status '{ready_status}' found in ClickUp")
            return results
        
        logger.info(f"Found {len(tasks)} tasks ready for processing")
        
        # Step 2: Process each task
        for task in tasks:
            task_id = task.get("id")
            task_name = task.get("name", "Unnamed task")
            task_description = task.get("description", "")
            
            logger.info(f"Processing task: {task_name} ({task_id})")
            
            try:
                # Step 2a: Enhance content with AI
                enhanced_content = tecbot.generate_content(
                    "content_enhancement", 
                    {"content": f"{task_name}\n\n{task_description}"}
                )
                
                results["content_enhanced"] += 1
                
                # Step 2b: Generate a compelling title
                title_suggestions = tecbot.generate_content(
                    "post_title_generator",
                    {"topic": task_name}
                )
                
                # Use the first title in the list or the original task name if parsing fails
                try:
                    import re
                    titles = re.findall(r'^\d+\.\s+(.+)$', title_suggestions, re.MULTILINE)
                    post_title = titles[0] if titles else task_name
                except:
                    post_title = task_name
                
                # Step 3: Post to WordPress
                post_result = wp_agent.create_post(
                    title=post_title,
                    content=enhanced_content,
                    excerpt=task_name,
                    status=config.get('agents', {}).get('wordpress', {}).get('post_status', 'draft')
                )
                
                if post_result.get("success"):
                    results["posts_created"] += 1
                    post_url = post_result.get("post_url", "")
                    
                    # Step 4: Update ClickUp task with the WordPress post URL
                    comment = f"Content published to WordPress: {post_url}"
                    clickup_agent.add_comment_to_task(task_id, comment)
                    
                    # Update task status to "Published" or similar
                    clickup_agent.update_task_status(task_id, "Published")
                else:
                    error_msg = post_result.get("error", "Unknown error")
                    logger.error(f"Failed to publish task {task_id}: {error_msg}")
                    results["errors"].append(f"Task {task_id} publishing failed: {error_msg}")
                
                results["tasks_processed"] += 1
                
            except Exception as e:
                logger.error(f"Error processing task {task_id}: {e}")
                results["errors"].append(f"Task {task_id} processing failed: {str(e)}")
        
        logger.info("TEC automation pipeline completed")
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        results["status"] = "error"
        results["errors"].append(str(e))
    
    return results

if __name__ == "__main__":
    # Load configuration
    config = load_config()
    
    # Run the pipeline
    start_time = datetime.now()
    logger.info(f"Starting automation at {start_time}")
    
    results = run_pipeline(config)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"TEC AUTOMATION PIPELINE SUMMARY")
    print("=" * 50)
    print(f"Status: {results['status'].upper()}")
    print(f"Tasks processed: {results['tasks_processed']}")
    print(f"Content enhanced: {results['content_enhanced']}")
    print(f"WordPress posts created: {results['posts_created']}")
    print(f"Duration: {duration:.2f} seconds")
    
    if results["errors"]:
        print("\nErrors encountered:")
        for error in results["errors"]:
            print(f" - {error}")
    
    print("=" * 50)