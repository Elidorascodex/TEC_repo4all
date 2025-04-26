"""
Stability AI Agent for The Elidoras Codex.
Handles interactions with the Stability AI API for image generation and manipulation.
"""
import os
import requests
import logging
import json
import time
from typing import Dict, Any, List, Optional, Union, BinaryIO
from io import BytesIO
from datetime import datetime
from pathlib import Path
import base64

from PIL import Image

from .base_agent import BaseAgent

class StabilityAgent(BaseAgent):
    """
    StabilityAgent handles interactions with the Stability AI API.
    It provides methods for text-to-image generation, image editing, and upscaling.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        super().__init__("StabilityAgent", config_path)
        self.logger.info("StabilityAgent initialized")
        
        # Initialize Stability AI API credentials
        self.api_token = os.getenv("STABILITY_API_KEY")
        if not self.api_token:
            self.logger.warning("Stability API token not found in environment variables.")
        
        # API base URL
        self.api_base_url = "https://api.stability.ai/v2beta"
        
        # Output directory
        self.output_dir = self.config.get("stability", {}).get("output_dir", 
                                                              os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                                                         "output", "images"))
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _send_generation_request(
        self,
        endpoint: str,
        params: Dict[str, Any],
        files: Optional[Dict[str, BinaryIO]] = None,
        return_json: bool = False
    ) -> requests.Response:
        """
        Send a request to the Stability AI API.
        
        Args:
            endpoint: API endpoint to call
            params: Parameters for the request
            files: File data to send
            return_json: Whether to expect JSON response instead of image
        
        Returns:
            API response
        """
        if not self.api_token:
            raise ValueError("Stability API token not configured")
        
        headers = {
            "Accept": "application/json" if return_json else "image/*",
            "Authorization": f"Bearer {self.api_token}"
        }
        
        if files is None:
            files = {}
        
        # Handle image and mask parameters by loading file contents
        image = params.pop("image", None)
        mask = params.pop("mask", None)
        
        if image is not None and image != '':
            if isinstance(image, str):
                files["image"] = open(image, 'rb')
            elif hasattr(image, 'read'):  # File-like object
                files["image"] = image
        
        if mask is not None and mask != '':
            if isinstance(mask, str):
                files["mask"] = open(mask, 'rb')
            elif hasattr(mask, 'read'):  # File-like object
                files["mask"] = mask
        
        if len(files) == 0:
            files["none"] = ''
        
        # Send request
        self.logger.info(f"Sending request to {endpoint}")
        url = f"{self.api_base_url}/{endpoint}"
        
        response = requests.post(
            url,
            headers=headers,
            files=files,
            data=params
        )
        
        if not response.ok:
            self.logger.error(f"API request failed: {response.text}")
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        
        return response
    
    def _send_async_generation_request(
        self,
        endpoint: str,
        params: Dict[str, Any],
        files: Optional[Dict[str, BinaryIO]] = None
    ) -> requests.Response:
        """
        Send an asynchronous request to the Stability AI API and wait for the result.
        
        Args:
            endpoint: API endpoint to call
            params: Parameters for the request
            files: File data to send
        
        Returns:
            API response with the final result
        """
        # Send initial request to get generation ID
        response = self._send_generation_request(endpoint, params, files, return_json=True)
        response_dict = json.loads(response.text)
        generation_id = response_dict.get("id")
        
        if not generation_id:
            raise ValueError("Expected generation ID in response")
        
        # Poll for results
        timeout = int(os.getenv("WORKER_TIMEOUT", 500))
        start = time.time()
        status_code = 202
        headers = {
            "Accept": "*/*",
            "Authorization": f"Bearer {self.api_token}"
        }
        
        # Loop until we get a final result
        while status_code == 202:
            self.logger.info(f"Polling results at https://api.stability.ai/v2beta/results/{generation_id}")
            
            response = requests.get(
                f"https://api.stability.ai/v2beta/results/{generation_id}",
                headers=headers
            )
            
            if not response.ok:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
            
            status_code = response.status_code
            time.sleep(10)
            
            if time.time() - start > timeout:
                raise Exception(f"Timeout after {timeout} seconds")
        
        return response
    
    def _save_and_process_image(
        self, 
        response: requests.Response, 
        output_name: Optional[str] = None,
        return_path: bool = True,
        return_image: bool = False
    ) -> Union[str, Image.Image, Dict[str, Any]]:
        """
        Process the API response, save the image, and return path or image object.
        
        Args:
            response: API response containing image data
            output_name: Optional name for the output file
            return_path: Whether to return the path to the saved image
            return_image: Whether to return the PIL Image object
            
        Returns:
            Path to the saved image, PIL Image object, or dict with both
        """
        output_image = response.content
        finish_reason = response.headers.get("finish-reason")
        seed = response.headers.get("seed", "0")
        
        # Check for content filtering
        if finish_reason == "CONTENT_FILTERED":
            self.logger.warning("Generation result was filtered due to content policy")
            raise ContentFilteredException("Generation result was filtered due to content policy")
        
        # Determine output format from response headers or default to jpeg
        content_type = response.headers.get("Content-Type", "image/jpeg")
        output_format = content_type.split("/")[1] if "/" in content_type else "jpeg"
        
        # Generate output filename if not provided
        if not output_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"stability_{timestamp}_{seed}"
        
        # Make sure the name doesn't include the extension
        if "." in output_name:
            output_name = output_name.split(".")[0]
        
        # Create full path
        output_path = os.path.join(self.output_dir, f"{output_name}.{output_format}")
        
        # Save the image
        with open(output_path, "wb") as f:
            f.write(output_image)
        
        self.logger.info(f"Saved image to {output_path}")
        
        # Return based on parameters
        result = {}
        
        if return_path:
            result["path"] = output_path
        
        if return_image:
            img = Image.open(BytesIO(output_image))
            result["image"] = img
        
        # If only one return type is requested, return just that value
        if len(result) == 1:
            return next(iter(result.values()))
        
        # Add metadata
        result["seed"] = seed
        result["finish_reason"] = finish_reason
        
        return result
    
    def generate_image(
        self,
        prompt: str,
        model: str = "ultra",  # ultra, core, or sd3
        negative_prompt: str = "",
        aspect_ratio: str = "1:1",
        seed: int = 0,
        style_preset: Optional[str] = None,
        output_format: str = "jpeg",
        sd3_model: str = "sd3.5-large",  # Only used when model="sd3"
        output_name: Optional[str] = None,
        return_path: bool = True,
        return_image: bool = False
    ) -> Union[str, Image.Image, Dict[str, Any]]:
        """
        Generate an image using text-to-image models.
        
        Args:
            prompt: Text prompt describing the desired image
            model: Model to use (ultra, core, or sd3)
            negative_prompt: Text describing what to avoid in the image
            aspect_ratio: Aspect ratio for the generated image
            seed: Random seed for generation
            style_preset: Optional style preset to apply
            output_format: Output format (jpeg, png, webp)
            sd3_model: SD3 specific model (sd3.5-large, sd3.5-large-turbo, sd3.5-medium)
            output_name: Optional name for the output file
            return_path: Whether to return the path to the saved image
            return_image: Whether to return the PIL Image object
            
        Returns:
            Path to the saved image, PIL Image object, or dict with both
        """
        self.logger.info(f"Generating image with model {model}")
        
        # Select the appropriate endpoint based on model
        if model == "ultra":
            endpoint = "stable-image/generate/ultra"
        elif model == "core":
            endpoint = "stable-image/generate/core"
        elif model == "sd3":
            endpoint = "stable-image/generate/sd3"
        else:
            raise ValueError(f"Unknown model: {model}")
        
        # Set up parameters
        params = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "aspect_ratio": aspect_ratio,
            "seed": seed,
            "output_format": output_format
        }
        
        # Add model-specific parameters
        if model == "sd3":
            params["model"] = sd3_model
            params["mode"] = "text-to-image"
            # Turbo doesn't support negative prompt
            if sd3_model == "sd3.5-large-turbo":
                params.pop("negative_prompt", None)
        
        # Add style preset if specified
        if style_preset and style_preset != "None":
            params["style_preset"] = style_preset
        
        # Send the request
        response = self._send_generation_request(endpoint, params)
        
        # Process and return the result
        return self._save_and_process_image(
            response=response,
            output_name=output_name,
            return_path=return_path,
            return_image=return_image
        )
    
    def edit_image_with_prompt(
        self,
        edit_type: str,
        image_path: str,
        prompt: str = "",
        negative_prompt: str = "",
        output_format: str = "jpeg",
        seed: int = 0,
        output_name: Optional[str] = None,
        return_path: bool = True,
        return_image: bool = False,
        **kwargs
    ) -> Union[str, Image.Image, Dict[str, Any]]:
        """
        Edit an image using various techniques.
        
        Args:
            edit_type: Type of edit to perform (inpaint, outpaint, search-and-replace, etc.)
            image_path: Path to the input image
            prompt: Text prompt describing the desired edit
            negative_prompt: Text describing what to avoid in the edit
            output_format: Output format (jpeg, png, webp)
            seed: Random seed for generation
            output_name: Optional name for the output file
            return_path: Whether to return the path to the saved image
            return_image: Whether to return the PIL Image object
            **kwargs: Additional parameters specific to each edit type
            
        Returns:
            Path to the saved image, PIL Image object, or dict with both
        """
        self.logger.info(f"Editing image using {edit_type}")
        
        valid_edit_types = [
            "inpaint",
            "outpaint", 
            "erase", 
            "search-and-replace", 
            "search-and-recolor",
            "remove-background",
            "replace-background-and-relight"
        ]
        
        if edit_type not in valid_edit_types:
            raise ValueError(f"Invalid edit type: {edit_type}. Must be one of {valid_edit_types}")
        
        # Basic parameters
        params = {
            "image": image_path,
            "output_format": output_format,
            "seed": seed
        }
        
        # Add prompt-related parameters if needed
        if edit_type in ["inpaint", "outpaint", "search-and-replace", "search-and-recolor"]:
            params["prompt"] = prompt
            params["negative_prompt"] = negative_prompt
        
        # Add edit-specific parameters
        if edit_type == "inpaint":
            params["mask"] = kwargs.get("mask", "")
            params["mode"] = "mask"
        
        elif edit_type == "outpaint":
            for param in ["left", "right", "up", "down"]:
                if param in kwargs:
                    params[param] = kwargs[param]
            if "creativity" in kwargs:
                params["creativity"] = kwargs["creativity"]
        
        elif edit_type == "search-and-replace":
            params["search_prompt"] = kwargs.get("search_prompt", "")
            params["mode"] = "search"
        
        elif edit_type == "search-and-recolor":
            params["select_prompt"] = kwargs.get("select_prompt", "")
            params["mode"] = "search"
            if "grow_mask" in kwargs:
                params["grow_mask"] = kwargs["grow_mask"]
        
        elif edit_type == "replace-background-and-relight":
            # This is more complex with multiple images and parameters
            files = {"subject_image": open(image_path, 'rb')}
            
            # Add background reference if provided
            bg_ref = kwargs.get("background_reference")
            if bg_ref:
                files["background_reference"] = open(bg_ref, 'rb')
            
            # Add light reference if provided
            light_ref = kwargs.get("light_reference")
            if light_ref:
                files["light_reference"] = open(light_ref, 'rb')
            
            # Add all other parameters
            for key, value in kwargs.items():
                if key not in ["background_reference", "light_reference"]:
                    params[key] = value
            
            # Remove image from params since we're passing it in files
            params.pop("image", None)
            
            # This operation is async
            response = self._send_async_generation_request(
                f"stable-image/edit/{edit_type}", 
                params, 
                files
            )
            
            return self._save_and_process_image(
                response=response,
                output_name=output_name,
                return_path=return_path,
                return_image=return_image
            )
        
        # Send the request
        endpoint = f"stable-image/edit/{edit_type}"
        
        # For async operations
        if edit_type in ["replace-background-and-relight"]:
            response = self._send_async_generation_request(endpoint, params)
        else:
            response = self._send_generation_request(endpoint, params)
        
        # Process and return the result
        return self._save_and_process_image(
            response=response,
            output_name=output_name,
            return_path=return_path,
            return_image=return_image
        )
    
    def control_image(
        self,
        control_type: str,
        image_path: str,
        prompt: str,
        negative_prompt: str = "",
        output_format: str = "jpeg",
        seed: int = 0,
        output_name: Optional[str] = None,
        return_path: bool = True,
        return_image: bool = False,
        **kwargs
    ) -> Union[str, Image.Image, Dict[str, Any]]:
        """
        Control image generation using various guidance techniques.
        
        Args:
            control_type: Type of control to use (sketch, structure, style)
            image_path: Path to the control input image
            prompt: Text prompt describing the desired image
            negative_prompt: Text describing what to avoid in the image
            output_format: Output format (jpeg, png, webp)
            seed: Random seed for generation
            output_name: Optional name for the output file
            return_path: Whether to return the path to the saved image
            return_image: Whether to return the PIL Image object
            **kwargs: Additional parameters specific to each control type
            
        Returns:
            Path to the saved image, PIL Image object, or dict with both
        """
        self.logger.info(f"Controlling image using {control_type}")
        
        valid_control_types = ["sketch", "structure", "style", "style-transfer"]
        
        if control_type not in valid_control_types:
            raise ValueError(f"Invalid control type: {control_type}. Must be one of {valid_control_types}")
        
        # Basic parameters
        params = {
            "image": image_path,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "output_format": output_format,
            "seed": seed
        }
        
        # Add control-specific parameters
        if control_type in ["sketch", "structure"]:
            if "control_strength" in kwargs:
                params["control_strength"] = kwargs["control_strength"]
        
        elif control_type == "style":
            if "fidelity" in kwargs:
                params["fidelity"] = kwargs["fidelity"]
            if "aspect_ratio" in kwargs:
                params["aspect_ratio"] = kwargs["aspect_ratio"]
        
        elif control_type == "style-transfer":
            # Style transfer requires a special setup with multiple images
            files = {}
            files["init_image"] = open(image_path, 'rb')
            
            # Add style image
            style_image = kwargs.get("style_image")
            if not style_image:
                raise ValueError("style_image is required for style-transfer")
            
            files["style_image"] = open(style_image, 'rb')
            
            # Add all other parameters
            for key, value in kwargs.items():
                if key != "style_image":
                    params[key] = value
            
            # Remove image from params since we're passing it in files
            params.pop("image", None)
            
            # Send the request
            response = self._send_generation_request(
                f"stable-image/control/{control_type}", 
                params, 
                files
            )
            
            return self._save_and_process_image(
                response=response,
                output_name=output_name,
                return_path=return_path,
                return_image=return_image
            )
        
        # Send the request
        response = self._send_generation_request(f"stable-image/control/{control_type}", params)
        
        # Process and return the result
        return self._save_and_process_image(
            response=response,
            output_name=output_name,
            return_path=return_path,
            return_image=return_image
        )
    
    def upscale_image(
        self,
        upscale_type: str,
        image_path: str,
        prompt: str = "",
        negative_prompt: str = "",
        output_format: str = "jpeg",
        seed: int = 0,
        creativity: float = 0.3,
        output_name: Optional[str] = None,
        return_path: bool = True,
        return_image: bool = False
    ) -> Union[str, Image.Image, Dict[str, Any]]:
        """
        Upscale an image using various techniques.
        
        Args:
            upscale_type: Type of upscaling to use (creative, conservative, fast)
            image_path: Path to the input image
            prompt: Text prompt describing the desired result
            negative_prompt: Text describing what to avoid
            output_format: Output format (jpeg, png, webp)
            seed: Random seed for generation
            creativity: Creativity level for creative upscaling (0.0 to 1.0)
            output_name: Optional name for the output file
            return_path: Whether to return the path to the saved image
            return_image: Whether to return the PIL Image object
            
        Returns:
            Path to the saved image, PIL Image object, or dict with both
        """
        self.logger.info(f"Upscaling image using {upscale_type}")
        
        valid_upscale_types = ["creative", "conservative", "fast"]
        
        if upscale_type not in valid_upscale_types:
            raise ValueError(f"Invalid upscale type: {upscale_type}. Must be one of {valid_upscale_types}")
        
        # Basic parameters
        params = {
            "image": image_path,
            "output_format": output_format,
            "seed": seed
        }
        
        # Add type-specific parameters
        if upscale_type in ["creative", "conservative"]:
            params["prompt"] = prompt
            params["negative_prompt"] = negative_prompt
            params["creativity"] = creativity
        
        # Creative upscaler is async
        if upscale_type == "creative":
            response = self._send_async_generation_request(f"stable-image/upscale/{upscale_type}", params)
        else:
            response = self._send_generation_request(f"stable-image/upscale/{upscale_type}", params)
        
        # Process and return the result
        return self._save_and_process_image(
            response=response,
            output_name=output_name,
            return_path=return_path,
            return_image=return_image
        )
    
    def generate_image_for_faction(
        self, 
        faction_name: str, 
        image_type: str = "banner",
        model: str = "ultra"
    ) -> str:
        """
        Generate an image for a TEC faction based on its characteristics.
        
        Args:
            faction_name: Name of the faction
            image_type: Type of image to generate (banner, icon, etc.)
            model: Model to use for generation
            
        Returns:
            Path to the generated image
        """
        self.logger.info(f"Generating {image_type} image for faction {faction_name}")
        
        # Load faction data
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        factions_file = os.path.join(data_dir, "factions.json")
        
        try:
            with open(factions_file, 'r') as f:
                factions_data = json.load(f)
            
            # Find the specified faction
            faction = None
            for f in factions_data.get("factions", []):
                if f.get("name", "").lower() == faction_name.lower():
                    faction = f
                    break
            
            if not faction:
                self.logger.error(f"Faction '{faction_name}' not found")
                return ""
            
            # Build prompt based on faction characteristics
            ethos = faction.get("ethos", "")
            description = faction.get("description", "")
            colors = faction.get("colors", [])
            color_names = faction.get("color_names", [])
            
            color_desc = ""
            if colors and color_names and len(colors) == len(color_names):
                color_desc = f" with a color scheme of {', '.join(color_names)}"
            
            # Construct the prompt based on image type
            if image_type == "banner":
                prompt = f"An epic banner for '{faction_name}', a faction in The Elidoras Codex universe. {description} Their ethos is: '{ethos}'{color_desc}. Dramatic lighting, cinematic composition."
                aspect_ratio = "16:9"
            
            elif image_type == "icon":
                prompt = f"A minimalist icon representing '{faction_name}', a faction in The Elidoras Codex universe. {description}{color_desc}. Clean lines, emblematic, symbolic."
                aspect_ratio = "1:1"
            
            elif image_type == "landscape":
                prompt = f"A landscape scene representing the territory of '{faction_name}', a faction in The Elidoras Codex universe. {description} Their ethos is: '{ethos}'{color_desc}. Epic wide shot, atmospheric, detailed environment."
                aspect_ratio = "21:9"
            
            else:
                self.logger.error(f"Unknown image type: {image_type}")
                return ""
            
            # Generate a filename slug
            slug = faction_name.lower().replace(" ", "_")
            output_name = f"faction_{slug}_{image_type}"
            
            # Generate the image
            result = self.generate_image(
                prompt=prompt,
                model=model,
                aspect_ratio=aspect_ratio,
                output_name=output_name,
                style_preset="fantasy-art"
            )
            
            if isinstance(result, dict):
                return result.get("path", "")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to generate faction image: {e}")
            return ""
    
    def generate_images_for_tec_block_nexus(self) -> Dict[str, str]:
        """
        Generate a set of images for the TEC Block-Nexus page.
        
        Returns:
            Dictionary mapping image types to file paths
        """
        self.logger.info("Generating images for TEC Block-Nexus page")
        
        results = {}
        
        try:
            # Generate header image
            header_prompt = "Abstract digital representation of blockchain networks interconnected as a nexus, with glowing nodes and pathways representing different cryptocurrencies, dark tech background, high contrast."
            results["header"] = self.generate_image(
                prompt=header_prompt,
                model="sd3",
                sd3_model="sd3.5-large",
                aspect_ratio="21:9",
                output_name="block_nexus_header",
                style_preset="digital-art"
            )
            
            # Generate ETH network visualization
            eth_prompt = "Abstract representation of Ethereum blockchain, featuring the classic Ethereum diamond logo, blue-purple color scheme, network connections, nodes and blocks flowing in digital space."
            results["ethereum"] = self.generate_image(
                prompt=eth_prompt,
                model="core",
                aspect_ratio="16:9",
                output_name="block_nexus_ethereum",
                style_preset="digital-art"
            )
            
            # Generate XRP network visualization
            xrp_prompt = "Abstract representation of XRP Ledger blockchain, featuring ripple wave patterns, blue-white-black color scheme, hexagonal nodes and connections flowing in digital space."
            results["xrp"] = self.generate_image(
                prompt=xrp_prompt,
                model="core",
                aspect_ratio="16:9",
                output_name="block_nexus_xrp",
                style_preset="digital-art"
            )
            
            # Generate Cardano network visualization
            cardano_prompt = "Abstract representation of Cardano blockchain, featuring Cardano's symbols, blue and green tones, mathematical patterns, scientific notation, and proof of stake concepts."
            results["cardano"] = self.generate_image(
                prompt=cardano_prompt,
                model="core",
                aspect_ratio="16:9",
                output_name="block_nexus_cardano",
                style_preset="digital-art"
            )
            
            # Convert any result objects to strings
            for key, value in results.items():
                if isinstance(value, dict):
                    results[key] = value.get("path", "")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to generate Block-Nexus images: {e}")
            return results
    
    def run(self, task: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Run the Stability AI Agent with a specific task.
        
        Args:
            task: Task to run ("generate", "edit", "upscale", etc.)
            **kwargs: Additional parameters for the specific task
            
        Returns:
            Results of the task
        """
        results = {
            "status": "success",
            "errors": []
        }
        
        try:
            if task == "generate":
                # Generate a single image
                output = self.generate_image(**kwargs)
                results["output"] = output
                
            elif task == "generate_faction_images":
                # Generate a set of images for a faction
                faction_name = kwargs.get("faction_name")
                image_types = kwargs.get("image_types", ["banner", "icon"])
                
                faction_results = {}
                for image_type in image_types:
                    result = self.generate_image_for_faction(
                        faction_name=faction_name,
                        image_type=image_type,
                        model=kwargs.get("model", "ultra")
                    )
                    faction_results[image_type] = result
                
                results["faction_images"] = faction_results
                
            elif task == "generate_block_nexus":
                # Generate images for the Block-Nexus page
                nexus_results = self.generate_images_for_tec_block_nexus()
                results["block_nexus_images"] = nexus_results
                
            elif task == "edit":
                # Edit an existing image
                edit_type = kwargs.pop("edit_type", "")
                output = self.edit_image_with_prompt(edit_type, **kwargs)
                results["output"] = output
                
            elif task == "control":
                # Control image generation
                control_type = kwargs.pop("control_type", "")
                output = self.control_image(control_type, **kwargs)
                results["output"] = output
                
            elif task == "upscale":
                # Upscale an image
                upscale_type = kwargs.pop("upscale_type", "")
                output = self.upscale_image(upscale_type, **kwargs)
                results["output"] = output
                
            else:
                self.logger.error(f"Unknown task: {task}")
                results["status"] = "error"
                results["errors"].append(f"Unknown task: {task}")
        
        except ContentFilteredException as e:
            self.logger.warning(f"Content was filtered: {e}")
            results["status"] = "filtered"
            results["errors"].append(str(e))
            
        except Exception as e:
            self.logger.error(f"Failed to run task: {e}")
            results["status"] = "error"
            results["errors"].append(str(e))
        
        return results

class ContentFilteredException(Exception):
    """Exception raised when content is filtered by the Stability AI API."""
    pass

if __name__ == "__main__":
    # Example usage
    import argparse
    
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Run Stability AI Agent")
    parser.add_argument("--task", required=True, help="Task to run (generate, edit, upscale, etc.)")
    parser.add_argument("--prompt", help="Text prompt for image generation")
    parser.add_argument("--image", help="Path to input image (for edit/upscale)")
    parser.add_argument("--output", help="Path for output image")
    parser.add_argument("--model", default="core", help="Model to use (ultra, core, sd3)")
    parser.add_argument("--config", help="Path to config file")
    
    args = parser.parse_args()
    
    # Create and run the agent
    agent = StabilityAgent(args.config)
    
    if args.task == "generate":
        if not args.prompt:
            print("Error: --prompt is required for generation")
            sys.exit(1)
        
        result = agent.run(
            task="generate", 
            prompt=args.prompt,
            model=args.model,
            output_name=args.output
        )
    
    elif args.task in ["edit", "upscale", "control"]:
        if not args.image or not args.prompt:
            print("Error: --image and --prompt are required for edit/upscale")
            sys.exit(1)
        
        # Example edit
        if args.task == "edit":
            result = agent.run(
                task="edit",
                edit_type="inpaint",  # inpaint, outpaint, etc.
                image_path=args.image,
                prompt=args.prompt,
                output_name=args.output
            )
    
    else:
        print(f"Error: Unknown task {args.task}")
        sys.exit(1)
    
    # Print results
    print(f"Task completed with status: {result['status']}")
    if result.get("output"):
        print(f"Output saved to: {result['output']}")
    
    if result.get("errors"):
        print("Errors:")
        for error in result["errors"]:
            print(f"  - {error}")