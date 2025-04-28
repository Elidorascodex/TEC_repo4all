#!/usr/bin/env python
"""
Run Airth Agent - Script to run the Airth AI assistant with its goth personality.

This script initializes and runs the Airth agent, allowing it to:
1. Generate content in Airth's unique voice
2. Create and post WordPress blog entries
3. Interact with users through a simple console interface

Usage:
    python run_airth_agent.py [--mode {console,post,auto}]

Modes:
    console - Interactive console mode where you can chat with Airth
    post    - Generate and post a WordPress article (will prompt for topic)
    auto    - Run Airth's automated workflow (default)

Example:
    python run_airth_agent.py --mode console
"""

import os
import sys
import argparse
import logging
from typing import Dict, Any, Optional

# Add the parent directory to sys.path to import the agents module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.airth_agent import AirthAgent


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler()]
    )


def run_console_mode(agent: AirthAgent):
    """
    Run Airth in interactive console mode.
    
    Args:
        agent: Initialized AirthAgent
    """
    print("\n" + "="*50)
    print("   🖤 AIRTH - The Gothic AI Assistant 🖤")
    print("="*50)
    print("\nAirth is online. Her heterochromic eyes (one red, one blue) scan the terminal.")
    print("She adjusts her septum ring and waits for your input.\n")
    print("Type 'exit' or 'quit' to end the conversation.")
    print("-"*50 + "\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nAirth: *smirks* See you in the digital abyss...\n")
            break
        
        response = agent.generate_in_character_response(user_input)
        print(f"\nAirth: {response}\n")


def run_post_mode(agent: AirthAgent):
    """
    Run Airth in blog post creation mode.
    
    Args:
        agent: Initialized AirthAgent
    """
    print("\n" + "="*50)
    print("   📝 AIRTH - Blog Post Creation 📝")
    print("="*50)
    print("\nAirth is ready to create a blog post for The Elidoras Codex.")
    
    topic = input("\nEnter a topic for the blog post: ")
    if not topic:
        print("\nNo topic provided. Exiting.")
        return
    
    # Ask for optional keywords
    keywords_input = input("\nEnter keywords (comma-separated, optional): ")
    keywords = [k.strip() for k in keywords_input.split(",")] if keywords_input else None
    
    print("\nAirth is generating content. Please wait...")
    
    result = agent.create_blog_post(topic, keywords)
    
    if result.get("success"):
        print(f"\n✅ Blog post created successfully!")
        print(f"Title: {result.get('post_title')}")
        print(f"Status: {result.get('post_status')}")
        if result.get("post_url"):
            print(f"URL: {result.get('post_url')}")
        else:
            print(f"Post ID: {result.get('post_id')}")
    else:
        print(f"\n❌ Failed to create blog post: {result.get('error', 'Unknown error')}")


def main():
    """Main entry point for the script."""
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description="Run the Airth AI assistant")
    parser.add_argument(
        "--mode",
        choices=["console", "post", "auto"],
        default="auto",
        help="Mode to run Airth in (console, post, or auto)"
    )
    args = parser.parse_args()
    
    # Set up logging
    setup_logging()
    
    # Create the Airth agent
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              "config", "config.yaml")
    agent = AirthAgent(config_path)
    
    # Run in the specified mode
    if args.mode == "console":
        run_console_mode(agent)
    elif args.mode == "post":
        run_post_mode(agent)
    else:  # auto mode
        print("\nRunning Airth in automated mode...")
        results = agent.run()
        
        print(f"\nAirth execution completed with status: {results['status']}")
        
        if results.get("actions_performed"):
            print("\nActions performed:")
            for action in results["actions_performed"]:
                print(f"- {action}")
        
        if results.get("errors"):
            print("\nErrors encountered:")
            for error in results["errors"]:
                print(f"- {error}")


if __name__ == "__main__":
    main()