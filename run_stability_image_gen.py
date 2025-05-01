#!/usr/bin/env python
"""
Stability AI Image Generation for The Elidoras Codex.
This script provides a command-line interface for using the StabilityAgent.
"""

import os
import sys
import argparse
import logging
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.stability_agent import StabilityAgent

def setup_logging():
    """Set up logging configuration."""
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f'stability_gen_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger('stability_gen')

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate images for The Elidoras Codex using Stability AI')
    
    # Task selection
    parser.add_argument(
        '--task',
        choices=['generate', 'edit', 'upscale', 'control', 'generate_faction_images', 'generate_block_nexus'],
        default='generate',
        help='Task to run'
    )
    
    # Basic generation parameters
    parser.add_argument('--prompt', help='Text prompt for image generation')
    parser.add_argument('--negative-prompt', default='', help='Negative prompt to avoid specific elements')
    parser.add_argument('--model', choices=['ultra', 'core', 'sd3'], default='core', help='Model to use')
    parser.add_argument('--sd3-model', choices=['sd3.5-large', 'sd3.5-large-turbo', 'sd3.5-medium'], 
                       default='sd3.5-large', help='SD3 specific model variant')
    parser.add_argument('--aspect-ratio', default='1:1', 
                       help='Aspect ratio (e.g., 1:1, 16:9, 21:9)')
    parser.add_argument('--style-preset', 
                       help='Style preset (e.g., cinematic, digital-art, fantasy-art)')
    parser.add_argument('--seed', type=int, default=0, help='Seed for reproducible generation')
    parser.add_argument('--output-format', choices=['jpeg', 'png', 'webp'], default='png', 
                       help='Output format for the generated image')
    parser.add_argument('--output-name', help='Name for the output file (without extension)')
    
    # Faction image generation
    parser.add_argument('--faction-name', help='Name of faction for faction image generation')
    parser.add_argument('--image-type', choices=['banner', 'icon', 'landscape'], default='banner',
                      help='Type of image to generate for faction')
    
    # Edit parameters
    parser.add_argument('--image', help='Path to input image for editing/upscaling')
    parser.add_argument('--mask', help='Path to mask image for inpainting')
    parser.add_argument('--edit-type', choices=['inpaint', 'outpaint', 'erase', 'search-and-replace', 
                                             'search-and-recolor', 'remove-background',
                                             'replace-background-and-relight'],
                      help='Type of edit to perform')
    parser.add_argument('--search-prompt', help='Prompt for what to search/replace in the image')
    parser.add_argument('--select-prompt', help='Prompt for what to recolor in the image')
    
    # Control parameters
    parser.add_argument('--control-type', choices=['sketch', 'structure', 'style', 'style-transfer'],
                      help='Type of control to use')
    parser.add_argument('--control-strength', type=float, default=0.7,
                      help='Strength of the control (0.0 to 1.0)')
    parser.add_argument('--style-image', help='Path to style reference image for style transfer')
    
    # Upscale parameters
    parser.add_argument('--upscale-type', choices=['creative', 'conservative', 'fast'],
                      help='Type of upscaling to use')
    parser.add_argument('--creativity', type=float, default=0.3,
                      help='Creativity level for upscaling (0.0 to 1.0)')
    
    # Config
    parser.add_argument('--config', 
                      default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                        'config', 'config.yaml'),
                      help='Path to configuration file')
    
    return parser.parse_args()

def main():
    """Main entry point for the script."""
    logger = setup_logging()
    args = parse_args()
    
    logger.info("Starting Stability AI image generation")
    
    try:
        # Initialize the Stability agent
        agent = StabilityAgent(args.config)
        
        # Process based on task
        if args.task == 'generate':
            if not args.prompt:
                logger.error("Prompt is required for image generation")
                return 1
            
            logger.info(f"Generating image with prompt: '{args.prompt}'")
            
            result = agent.run(
                task="generate",
                prompt=args.prompt,
                negative_prompt=args.negative_prompt,
                model=args.model,
                sd3_model=args.sd3_model if args.model == 'sd3' else None,
                aspect_ratio=args.aspect_ratio,
                style_preset=args.style_preset,
                seed=args.seed,
                output_format=args.output_format,
                output_name=args.output_name
            )
            
        elif args.task == 'edit':
            if not args.image or not args.edit_type:
                logger.error("Image path and edit type are required for editing")
                return 1
            
            logger.info(f"Editing image using {args.edit_type}")
            
            # Build kwargs based on edit type
            kwargs = {
                "image_path": args.image,
                "edit_type": args.edit_type,
                "prompt": args.prompt or "",
                "negative_prompt": args.negative_prompt,
                "seed": args.seed,
                "output_format": args.output_format,
                "output_name": args.output_name
            }
            
            # Add edit-specific parameters
            if args.edit_type == 'inpaint':
                if args.mask:
                    kwargs["mask"] = args.mask
            elif args.edit_type == 'search-and-replace':
                if args.search_prompt:
                    kwargs["search_prompt"] = args.search_prompt
            elif args.edit_type == 'search-and-recolor':
                if args.select_prompt:
                    kwargs["select_prompt"] = args.select_prompt
            
            result = agent.run(task="edit", **kwargs)
            
        elif args.task == 'control':
            if not args.image or not args.control_type or not args.prompt:
                logger.error("Image path, control type, and prompt are required for control tasks")
                return 1
            
            logger.info(f"Controlling image generation with {args.control_type}")
            
            # Build kwargs based on control type
            kwargs = {
                "control_type": args.control_type,
                "image_path": args.image,
                "prompt": args.prompt,
                "negative_prompt": args.negative_prompt,
                "seed": args.seed,
                "output_format": args.output_format,
                "output_name": args.output_name
            }
            
            # Add control-specific parameters
            if args.control_type in ['sketch', 'structure']:
                kwargs["control_strength"] = args.control_strength
            elif args.control_type == 'style-transfer':
                if not args.style_image:
                    logger.error("Style image is required for style transfer")
                    return 1
                kwargs["style_image"] = args.style_image
            
            result = agent.run(task="control", **kwargs)
            
        elif args.task == 'upscale':
            if not args.image or not args.upscale_type:
                logger.error("Image path and upscale type are required for upscaling")
                return 1
            
            logger.info(f"Upscaling image with {args.upscale_type}")
            
            result = agent.run(
                task="upscale",
                upscale_type=args.upscale_type,
                image_path=args.image,
                prompt=args.prompt or "",
                negative_prompt=args.negative_prompt,
                seed=args.seed,
                creativity=args.creativity,
                output_format=args.output_format,
                output_name=args.output_name
            )
            
        elif args.task == 'generate_faction_images':
            if not args.faction_name:
                logger.error("Faction name is required for faction image generation")
                return 1
            
            logger.info(f"Generating images for faction: {args.faction_name}")
            
            result = agent.run(
                task="generate_faction_images",
                faction_name=args.faction_name,
                image_types=[args.image_type],
                model=args.model
            )
            
            # Display each generated image path
            if result.get("status") == "success" and result.get("faction_images"):
                for img_type, path in result["faction_images"].items():
                    logger.info(f"Generated {img_type} image: {path}")
            
        elif args.task == 'generate_block_nexus':
            logger.info("Generating Block-Nexus images")
            
            result = agent.run(task="generate_block_nexus")
            
            # Display each generated image path
            if result.get("status") == "success" and result.get("block_nexus_images"):
                for img_type, path in result["block_nexus_images"].items():
                    logger.info(f"Generated {img_type} image: {path}")
        
        # Check results and report
        if result.get("status") == "success":
            logger.info("Image generation completed successfully")
            if result.get("output"):
                logger.info(f"Output saved to: {result['output']}")
        elif result.get("status") == "filtered":
            logger.warning("Content was filtered by Stability AI content policy")
        else:
            logger.error("Image generation failed")
            if result.get("errors"):
                for error in result["errors"]:
                    logger.error(f"Error: {error}")
        
        return 0 if result.get("status") in ["success", "filtered"] else 1
    
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())