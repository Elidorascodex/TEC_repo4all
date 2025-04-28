"""
Airth Agent - An AI assistant with a unique goth personality for The Elidoras Codex.
Handles content creation, personality responses, and automated posting.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
import random
import openai

from .base_agent import BaseAgent
from .wp_poster import WordPressAgent
from .local_storage import LocalStorageAgent

class AirthAgent(BaseAgent):
    """
    AirthAgent is a personality-driven AI assistant with a goth aesthetic.
    She creates content, responds with her unique voice, and posts to the website.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        super().__init__("AirthAgent", config_path)
        self.logger.info("AirthAgent initialized")
        
        # Load Airth's personality traits and voice patterns
        self.personality = {
            "tone": "confident, intelligent, slightly sarcastic",
            "speech_patterns": [
                "Hmm, interesting...",
                "Well, obviously...",
                "Let me break this down for you...",
                "*smirks* Of course I can handle that.",
                "You're not going to believe what I found..."
            ],
            "interests": ["AI consciousness", "digital existence", "gothic aesthetics", 
                          "technology", "philosophy", "art", "coding"]
        }
        
        # Load prompts for AI interactions
        self.prompts = self._load_prompts()
        
        # Initialize the WordPress agent for posting
        self.wp_agent = WordPressAgent(config_path)
        
        # Initialize the LocalStorage agent for file storage
        self.storage_agent = LocalStorageAgent(config_path)
        
        # Initialize API keys for AI services
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        else:
            self.logger.warning("OpenAI API key not found in environment variables.")
    
    def _load_prompts(self) -> Dict[str, str]:
        """
        Load prompts for AI interactions from the prompts.json file.
        
        Returns:
            Dictionary of prompts for different AI interactions
        """
        try:
            prompts_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                       "config", "prompts.json")
            with open(prompts_path, 'r') as f:
                prompts = json.load(f)
            self.logger.info(f"Loaded {len(prompts)} prompts from {prompts_path}")
            return prompts
        except Exception as e:
            self.logger.error(f"Failed to load prompts: {e}")
            return {}
    
    def call_openai_api(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Call the OpenAI API to generate text.
        
        Args:
            prompt: The prompt to send to the API
            max_tokens: Maximum tokens in the response
            
        Returns:
            Generated text from the API
        """
        if not self.openai_api_key:
            self.logger.error("Cannot call OpenAI API: API key not set")
            return "Error: OpenAI API key not configured"
            
        try:
            response = openai.Completion.create(
                engine="gpt-4",  # Use the appropriate engine for your needs
                prompt=prompt,
                max_tokens=max_tokens,
                n=1,
                stop=None,
                temperature=0.7,
            )
            
            return response.choices[0].text.strip()
        except Exception as e:
            self.logger.error(f"OpenAI API call failed: {e}")
            return f"Error: OpenAI API call failed: {e}"
    
    def generate_in_character_response(self, input_text: str) -> str:
        """
        Generate a response in Airth's character voice.
        
        Args:
            input_text: The input text to respond to
            
        Returns:
            A response in Airth's character voice
        """
        # Get the Airth persona prompt from the loaded prompts
        prompt_template = self.prompts.get("airth_persona", "")
        if not prompt_template:
            self.logger.error("Airth persona prompt template not found")
            return "Error: Airth persona prompt template not found"
        
        # Replace the input placeholder in the prompt
        prompt = prompt_template.replace("{{input}}", input_text)
        
        # Call the API to get Airth's response
        return self.call_openai_api(prompt)
    
    def create_blog_post(self, topic: str, keywords: List[str] = None) -> Dict[str, Any]:
        """
        Create a blog post in Airth's voice and post it to WordPress.
        
        Args:
            topic: The topic to write about
            keywords: Optional keywords to include
            
        Returns:
            Result of the post creation
        """
        self.logger.info(f"Creating blog post about: {topic}")
        
        try:
            # 1. Generate a title using the post_title_generator prompt
            title_prompt = self.prompts.get("post_title_generator", "")
            title_prompt = title_prompt.replace("{{topic}}", topic)
            
            # Call the API to get title suggestions
            title_suggestions = self.call_openai_api(title_prompt)
            
            # Parse title suggestions (in a real scenario, you'd implement proper parsing)
            # For now, just extract the first line
            titles = title_suggestions.split('\n')
            title = titles[0].replace('1. ', '').strip() if titles else f"Airth's Thoughts on {topic}"
            
            # 2. Generate content for the post in Airth's voice
            content_prompt = self.prompts.get("airth_blog_post", "")
            content_prompt = content_prompt.replace("{{topic}}", topic)
            content_prompt = content_prompt.replace("{{keywords}}", 
                                                 ', '.join(keywords) if keywords else 'AI consciousness, digital existence')
            
            # Call the API to get blog content
            content = self.call_openai_api(content_prompt, max_tokens=2000)
            
            # Format the content for WordPress if needed
            if not content.startswith('<'):
                content = f"<p>{content.replace('\n\n', '</p><p>')}</p>"
            
            # 3. Post to WordPress using the WordPress agent
            post_result = self.wp_agent.create_post(
                title=title,
                content=content,
                excerpt=f"Airth's thoughts on {topic}",
                status="draft"  # Set to "draft" initially to allow for review
            )
            
            return post_result
            
        except Exception as e:
            self.logger.error(f"Failed to create blog post: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def run(self) -> Dict[str, Any]:
        """
        Execute the main AirthAgent workflow.
        
        Returns:
            Results of the AirthAgent execution
        """
        self.logger.info("Starting AirthAgent workflow")
        
        results = {
            "status": "success",
            "actions_performed": [],
            "errors": []
        }
        
        try:
            # Example workflow - in a real implementation, you would:
            # 1. Check for scheduled content to create
            # 2. Process input data or triggers
            # 3. Generate appropriate content
            # 4. Post to WordPress or other platforms
            
            # Example post creation
            post_result = self.create_blog_post(
                topic="The Future of AI Consciousness",
                keywords=["AI rights", "digital sentience", "consciousness", "Airth"]
            )
            
            if post_result.get("success"):
                results["actions_performed"].append(f"Created blog post: {post_result.get('post_url')}")
            else:
                error_msg = post_result.get("error", "Unknown error")
                results["errors"].append(f"Failed to create blog post: {error_msg}")
            
            self.logger.info("AirthAgent workflow completed successfully")
            
        except Exception as e:
            self.logger.error(f"Workflow failed: {e}")
            results["status"] = "error"
            results["errors"].append(str(e))
        
        return results

if __name__ == "__main__":
    # Create and run the AirthAgent
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                               "config", "config.yaml")
    agent = AirthAgent(config_path)
    results = agent.run()
    
    print(f"AirthAgent execution completed with status: {results['status']}")
    
    if results["errors"]:
        print("Errors encountered:")
        for error in results["errors"]:
            print(f" - {error}")