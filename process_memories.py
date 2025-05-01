#!/usr/bin/env python3
"""
Process custom memories from text or DOCX files and convert them to structured memories.
This script extracts text from files and uses the AirthAgent to process them into memory objects.
"""
import os
import sys
import json
import logging
import argparse
from typing import List, Dict, Any, Optional
from pathlib import Path

# Try to import docx for DOCX file processing
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# Add the parent directory to sys.path to import the agents module
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

from agents.airth_agent import AirthAgent

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(script_dir, "memory_processing.log"))
    ]
)
logger = logging.getLogger("MemoryProcessor")

def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text from a DOCX file.
    
    Args:
        file_path: Path to the DOCX file
        
    Returns:
        Extracted text from the file
    """
    if not DOCX_AVAILABLE:
        logger.error("python-docx package is not installed. Cannot process DOCX files.")
        return "ERROR: python-docx package is required to process DOCX files."
    
    try:
        doc = docx.Document(file_path)
        text = "\n\n".join([paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()])
        logger.info(f"Successfully extracted {len(text)} characters from {file_path}")
        return text
    except Exception as e:
        logger.error(f"Failed to extract text from DOCX file {file_path}: {e}")
        return f"ERROR: Failed to extract text from DOCX file: {e}"

def extract_text_from_file(file_path: str) -> str:
    """
    Extract text from a file based on its extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Extracted text from the file
    """
    _, ext = os.path.splitext(file_path)
    
    if ext.lower() == ".docx":
        return extract_text_from_docx(file_path)
    elif ext.lower() in [".txt", ".md", ".text"]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            logger.info(f"Successfully read {len(text)} characters from {file_path}")
            return text
        except Exception as e:
            logger.error(f"Failed to read text file {file_path}: {e}")
            return f"ERROR: Failed to read text file: {e}"
    else:
        logger.error(f"Unsupported file extension: {ext}")
        return f"ERROR: Unsupported file extension: {ext}"

def split_text_into_chunks(text: str, max_chunk_size: int = 1000) -> List[str]:
    """
    Split a large text into smaller chunks based on paragraphs.
    
    Args:
        text: The text to split
        max_chunk_size: Maximum size of each chunk in characters
        
    Returns:
        List of text chunks
    """
    # Split by paragraphs first
    paragraphs = text.split('\n\n')
    
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        # If adding this paragraph would exceed the chunk size, start a new chunk
        if len(current_chunk) + len(paragraph) > max_chunk_size and current_chunk:
            chunks.append(current_chunk)
            current_chunk = paragraph
        else:
            # Add to current chunk with a separator if needed
            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph
    
    # Add the last chunk if there's anything left
    if current_chunk:
        chunks.append(current_chunk)
    
    logger.info(f"Split text into {len(chunks)} chunks")
    return chunks

def process_memory_file(file_path: str, agent: AirthAgent, type_hint: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Process a memory file and convert it to structured memories.
    
    Args:
        file_path: Path to the memory file
        agent: AirthAgent instance to use for processing
        type_hint: Optional hint about the type of memories in the file
        
    Returns:
        List of structured memory objects
    """
    logger.info(f"Processing memory file: {file_path}")
    
    # Extract text from the file
    text = extract_text_from_file(file_path)
    if text.startswith("ERROR:"):
        logger.error(text)
        return []
    
    # Split the text into manageable chunks
    chunks = split_text_into_chunks(text)
    
    # Process each chunk into a structured memory
    memories = []
    for i, chunk in enumerate(chunks, 1):
        logger.info(f"Processing chunk {i} of {len(chunks)} ({len(chunk)} characters)")
        try:
            memory_data = agent.process_memory_from_text(chunk, type_hint)
            memories.append(memory_data)
            logger.info(f"Successfully processed chunk {i} into memory: {memory_data.get('title', 'Untitled')}")
        except Exception as e:
            logger.error(f"Failed to process chunk {i}: {e}")
    
    return memories

def add_memories_to_database(memories: List[Dict[str, Any]], agent: AirthAgent) -> int:
    """
    Add processed memories to Airth's memory database.
    
    Args:
        memories: List of structured memory objects
        agent: AirthAgent instance
        
    Returns:
        Number of successfully added memories
    """
    success_count = 0
    
    for i, memory in enumerate(memories, 1):
        logger.info(f"Adding memory {i} of {len(memories)} to database")
        try:
            success = agent.add_new_memory(memory)
            if success:
                success_count += 1
                logger.info(f"Successfully added memory {i}: {memory.get('title', 'Untitled')}")
            else:
                logger.error(f"Failed to add memory {i}: Unknown error")
        except Exception as e:
            logger.error(f"Failed to add memory {i}: {e}")
    
    return success_count

def process_directory(dir_path: str, agent: AirthAgent, type_hint: Optional[str] = None) -> int:
    """
    Process all compatible files in a directory.
    
    Args:
        dir_path: Path to the directory
        agent: AirthAgent instance to use for processing
        type_hint: Optional hint about the type of memories
        
    Returns:
        Total number of memories added
    """
    logger.info(f"Processing directory: {dir_path}")
    
    if not os.path.isdir(dir_path):
        logger.error(f"Directory does not exist: {dir_path}")
        return 0
    
    total_added = 0
    
    for file_name in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file_name)
        if os.path.isfile(file_path):
            _, ext = os.path.splitext(file_path)
            if ext.lower() in [".txt", ".md", ".text", ".docx"]:
                logger.info(f"Found compatible file: {file_name}")
                memories = process_memory_file(file_path, agent, type_hint)
                added = add_memories_to_database(memories, agent)
                total_added += added
                logger.info(f"Added {added} memories from {file_name}")
    
    return total_added

def main():
    """Main function to process memory files or directories."""
    parser = argparse.ArgumentParser(description="Process custom memories for Airth")
    parser.add_argument("path", help="Path to a memory file or directory of memory files")
    parser.add_argument("--type", help="Optional hint about the type of memories (personal, faction, event, relationship, knowledge)")
    parser.add_argument("--config", help="Path to the config file")
    args = parser.parse_args()
    
    # Check if python-docx is available
    if not DOCX_AVAILABLE:
        logger.warning("python-docx is not installed. DOCX files will not be processed.")
    
    # Initialize the AirthAgent
    config_path = args.config if args.config else os.path.join(parent_dir, "config", "config.yaml")
    agent = AirthAgent(config_path)
    
    # Process the specified path
    path = args.path
    type_hint = args.type
    
    if os.path.isdir(path):
        total_added = process_directory(path, agent, type_hint)
        logger.info(f"Total memories added from directory: {total_added}")
        print(f"Successfully added {total_added} memories from directory: {path}")
    elif os.path.isfile(path):
        memories = process_memory_file(path, agent, type_hint)
        added = add_memories_to_database(memories, agent)
        logger.info(f"Total memories added from file: {added}")
        print(f"Successfully added {added} memories from file: {path}")
    else:
        logger.error(f"Path does not exist: {path}")
        print(f"Error: Path does not exist: {path}")

if __name__ == "__main__":
    main()