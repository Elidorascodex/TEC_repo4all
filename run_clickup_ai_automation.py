#!/usr/bin/env python
"""
Run ClickUp AI Automation for The Elidoras Codex.
This script triggers the AI-driven workflow for tasks tagged with 'ai-alpha-commence-assessment'.
"""

import os
import sys
import argparse
import logging
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.clickup_agent import ClickUpAgent

def setup_logging():
    """Set up logging configuration."""
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f'clickup_automation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger('clickup_automation')

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run ClickUp AI Automation for The Elidoras Codex')
    
    parser.add_argument(
        '--task-id', 
        help='Process a specific task ID instead of searching for tagged tasks'
    )
    
    parser.add_argument(
        '--import-templates', 
        action='store_true',
        help='Import tasks from templates file'
    )
    
    parser.add_argument(
        '--generate-doc', 
        help='Generate a lore document for the specified task ID'
    )
    
    parser.add_argument(
        '--config', 
        default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                          'config', 'config.yaml'),
        help='Path to configuration file'
    )
    
    return parser.parse_args()

def main():
    """Main entry point for the script."""
    logger = setup_logging()
    args = parse_args()
    
    logger.info("Starting ClickUp AI Automation")
    
    try:
        # Initialize the ClickUp agent
        agent = ClickUpAgent(args.config)
        
        # Process based on arguments
        if args.task_id:
            # Process a specific task
            logger.info(f"Processing specific task: {args.task_id}")
            results = agent.process_ai_assessment_trigger(args.task_id)
            logger.info(f"Task processing completed with status: {results['status']}")
            
            if results['status'] == 'success':
                for action in results.get('actions_performed', []):
                    logger.info(f"Action performed: {action}")
            
            if results.get('errors'):
                for error in results['errors']:
                    logger.error(f"Error: {error}")
        
        elif args.import_templates:
            # Import tasks from templates
            templates_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                      'data', 'clickup_task_templates.json')
            
            logger.info(f"Importing tasks from templates file: {templates_file}")
            results = agent.bulk_import_tasks(templates_file)
            
            logger.info(f"Task import completed with status: {results['status']}")
            logger.info(f"Tasks created: {results['tasks_created']}")
            logger.info(f"Tasks failed: {results['failed_tasks']}")
            
            if results.get('errors'):
                for error in results['errors']:
                    logger.error(f"Error: {error}")
        
        elif args.generate_doc:
            # Generate a lore document for a task
            task_id = args.generate_doc
            logger.info(f"Generating lore document for task: {task_id}")
            
            results = agent.generate_lore_doc(task_id)
            
            if results['status'] == 'success' and results.get('doc_created'):
                logger.info(f"Document created successfully. Doc ID: {results.get('doc_id')}")
            else:
                logger.error("Failed to create document")
                
                if results.get('errors'):
                    for error in results['errors']:
                        logger.error(f"Error: {error}")
        
        else:
            # Run the standard workflow - find tasks with trigger tags and process them
            logger.info("Running standard workflow")
            results = agent.run()
            
            logger.info(f"Workflow completed with status: {results['status']}")
            logger.info(f"Tasks found: {results.get('tasks_found', 0)}")
            logger.info(f"Tasks processed: {results.get('tasks_processed', 0)}")
            
            if results.get('errors'):
                for error in results['errors']:
                    logger.error(f"Error: {error}")
        
        logger.info("ClickUp AI Automation completed successfully")
        return 0
    
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())