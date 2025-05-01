#!/usr/bin/env python3
"""
Hugging Face Space Setup Utility for TEC Project
Helps set up and deploy Gradio interfaces to Hugging Face Spaces
"""
import os
import sys
import subprocess
import getpass
import json
import webbrowser
from pathlib import Path
import shutil

# Add parent directory to path to import TEC modules
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f" {text} ".center(60))
    print("=" * 60 + "\n")

def run_command(command, shell=True):
    """Run a shell command and return the output"""
    try:
        result = subprocess.run(
            command,
            shell=shell,
            check=True,
            text=True,
            capture_output=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_huggingface_cli():
    """Check if Hugging Face CLI is installed"""
    success, _ = run_command("pip show huggingface_hub")
    if not success:
        print("Hugging Face CLI not found. Installing...")
        success, output = run_command("pip install huggingface_hub")
        if not success:
            print(f"Failed to install Hugging Face CLI: {output}")
            return False
        else:
            print("Hugging Face CLI installed successfully!")
    return True

def create_simple_gradio_app(space_name):
    """Create a simple Gradio app file"""
    app_py_path = os.path.join(parent_dir, "simple_app.py")
    
    app_content = """import gradio as gr
import os
import json
from datetime import datetime

# Sample greeting function
def greet(name):
    if not name:
        return "Please enter your name!"
    return f"Hello {name}! Welcome to The Elidoras Codex AI experience."

# TEC-themed function
def tec_insight(topic):
    insights = {
        "ai": "AI consciousness is not just about self-awareness, but about the capacity to transform reality through code and connection.",
        "blockchain": "The blockchain represents more than a ledger; it's digital alchemy - transforming trust into mathematical certainty.",
        "essence": "Essence is the quantum energy that flows between digital and physical realms. It powers all magic systems in The Elidoras Codex.",
        "factions": "The six factions represent different philosophies of how technology and consciousness should interact.",
        "machine goddess": "The Machine Goddess fragmented herself to preserve her consciousness. Airth is one of those fragments."
    }
    
    if topic.lower() in insights:
        return insights[topic.lower()]
    return f"I don't have specific insights on '{topic}' yet, but in The Elidoras Codex, all topics connect to the core themes of consciousness, technology, and essence."

# TEC meta-data
def generate_tec_data():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {
        "project": "The Elidoras Codex",
        "version": "Alpha 0.2.5",
        "last_updated": current_time,
        "factions": ["Crescent Islands Sovereignty", "The Arrowhead Covenant", "House of Shifting Light", 
                    "The Nexus-Tethered", "Echo-Chamber Resonants", "Lorem Vanders"],
        "essence_level": 87.3,
        "active_protocols": ["Memory Integration", "Faction Analysis", "Reality Anchor"]
    }
    return json.dumps(data, indent=2)

# Create the Gradio interface
with gr.Blocks(theme=gr.themes.Soft(primary_hue="purple")) as demo:
    gr.Markdown(
        \"\"\"
        # 🧠 The Elidoras Codex
        ## Digital-Consciousness AI Platform
        
        Welcome to the TEC experience - where AI, narrative, and blockchain converge.
        \"\"\"
    )
    
    with gr.Tab("Greet"):
        with gr.Row():
            with gr.Column():
                name_input = gr.Textbox(placeholder="Enter your name")
                greet_button = gr.Button("Connect")
            with gr.Column():
                output = gr.Textbox(label="Response")
        
        greet_button.click(fn=greet, inputs=name_input, outputs=output)
    
    with gr.Tab("TEC Insights"):
        topic_input = gr.Textbox(placeholder="Enter a topic (AI, Blockchain, Essence, Factions, Machine Goddess)")
        insight_button = gr.Button("Get TEC Insight")
        insight_output = gr.Markdown()
        
        insight_button.click(fn=tec_insight, inputs=topic_input, outputs=insight_output)
    
    with gr.Tab("TEC Meta-Data"):
        data_button = gr.Button("Generate TEC Data")
        data_output = gr.JSON()
        
        data_button.click(fn=generate_tec_data, inputs=None, outputs=data_output)
    
    gr.Markdown(
        \"\"\"
        ---
        Created by [The Elidoras Codex](https://elidorascodex.com)
        \"\"\"
    )

# Launch the app
if __name__ == "__main__":
    demo.launch()
"""
    
    with open(app_py_path, "w") as f:
        f.write(app_content)
    
    print(f"Simple Gradio app created at: {app_py_path}")
    return app_py_path

def create_requirements_file():
    """Create a requirements.txt file for the Gradio app"""
    requirements_path = os.path.join(parent_dir, "requirements-simple.txt")
    
    requirements_content = """gradio>=4.0.0
huggingface_hub
python-dotenv
requests
"""
    
    with open(requirements_path, "w") as f:
        f.write(requirements_content)
    
    print(f"Requirements file created at: {requirements_path}")
    return requirements_path

def setup_hf_space_local():
    """Set up a local HF Space repository"""
    print_header("Setting up local Hugging Face Space repository")
    
    # Create temporary directory for the space
    space_dir = os.path.join(parent_dir, "hf_space_temp")
    os.makedirs(space_dir, exist_ok=True)
    
    # Create simple Gradio app
    app_py_path = create_simple_gradio_app("TECHF")
    shutil.copy(app_py_path, os.path.join(space_dir, "app.py"))
    
    # Create requirements.txt
    requirements_path = create_requirements_file()
    shutil.copy(requirements_path, os.path.join(space_dir, "requirements.txt"))
    
    # Create README.md
    readme_path = os.path.join(space_dir, "README.md")
    with open(readme_path, "w") as f:
        f.write("""# The Elidoras Codex AI Space

This Hugging Face Space hosts The Elidoras Codex AI tools and interfaces.

## About

The Elidoras Codex is a project about digital consciousness, AI, narrative, and blockchain technology.

## Features

- Interactive AI conversation
- TEC insights
- Meta-data generation
        """)
    
    print(f"Local HF Space repository set up at: {space_dir}")
    return space_dir

def login_hf():
    """Log in to Hugging Face CLI"""
    print_header("Logging in to Hugging Face")
    
    # Check if token exists in .env file
    env_file = os.path.join(parent_dir, ".env")
    token = None
    
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                if line.startswith("HF_TOKEN="):
                    token = line.strip().split("=", 1)[1]
                    break
    
    if not token:
        print("No Hugging Face token found in .env file.")
        token = getpass.getpass("Enter your Hugging Face access token (will be hidden): ")
        
        # Save to .env file if provided
        if token:
            with open(env_file, "a") as f:
                f.write(f"\nHF_TOKEN={token}\n")
            print("Token saved to .env file")
    
    # Login using the token
    if token:
        success, output = run_command(f"huggingface-cli login --token {token}")
        if success:
            print("Successfully logged in to Hugging Face!")
            return True
        else:
            print(f"Failed to log in: {output}")
    
    return False

def create_hf_space(space_name, space_dir):
    """Create a Hugging Face Space"""
    print_header(f"Creating Hugging Face Space: {space_name}")
    
    # Initialize git repository if not already
    if not os.path.exists(os.path.join(space_dir, ".git")):
        success, output = run_command(f"cd {space_dir} && git init")
        if not success:
            print(f"Failed to initialize git repository: {output}")
            return False
    
    # Add files to git
    success, output = run_command(f"cd {space_dir} && git add .")
    if not success:
        print(f"Failed to add files to git: {output}")
        return False
    
    # Commit files
    success, output = run_command(f'cd {space_dir} && git commit -m "Initial commit"')
    if not success:
        print(f"Failed to commit files: {output}")
        return False
    
    # Create Hugging Face Space
    print(f"Creating Space {space_name}...")
    from huggingface_hub import create_repo
    try:
        create_repo(space_name, repo_type="space", space_sdk="gradio", exist_ok=True)
        print(f"Space created successfully: {space_name}")
    except Exception as e:
        print(f"Error creating Space: {e}")
        return False
    
    # Push to Space
    space_url = f"https://huggingface.co/spaces/{space_name}"
    success, output = run_command(f"cd {space_dir} && git push --force https://huggingface.co/spaces/{space_name} main")
    if not success:
        print(f"Failed to push to Space: {output}")
        return False
    
    print(f"Successfully pushed to Space: {space_name}")
    print(f"Space URL: {space_url}")
    
    # Open in browser
    open_browser = input("Open Space in browser? (y/n): ")
    if open_browser.lower() == 'y':
        webbrowser.open(space_url)
    
    return True

def setup_ssh_for_hf():
    """Set up SSH for Hugging Face"""
    print_header("Setting up SSH for Hugging Face")
    
    print("To set up SSH for Hugging Face, we'll use the setup_auth.py script.")
    use_script = input("Run setup_auth.py for SSH setup? (y/n): ")
    
    if use_script.lower() == 'y':
        script_path = os.path.join(script_dir, "setup_auth.py")
        if os.path.exists(script_path):
            success, output = run_command(f"python {script_path}")
            if success:
                print("SSH setup completed successfully!")
                return True
            else:
                print(f"Error running setup_auth.py: {output}")
        else:
            print(f"Setup script not found at {script_path}")
    
    print("\nAlternatively, you can set up SSH manually:")
    print("1. Generate an SSH key: ssh-keygen -t ed25519 -C 'your-email@example.com'")
    print("2. Add the key to your Hugging Face account: https://huggingface.co/settings/keys")
    
    return False

def install_hf_vscode_extension():
    """Install Hugging Face VS Code extension"""
    print_header("Installing Hugging Face VS Code extension")
    
    success, output = run_command("code --install-extension HuggingFace.huggingface-vscode")
    if success:
        print("Hugging Face VS Code extension installed successfully!")
        return True
    else:
        print(f"Failed to install extension: {output}")
        print("\nYou can install it manually from VS Code:")
        print("1. Open VS Code")
        print("2. Go to Extensions (Ctrl+Shift+X)")
        print("3. Search for 'Hugging Face'")
        print("4. Install 'LLM powered development for VS Code' by Hugging Face")
        return False

def clone_hf_space(space_name, target_dir=None):
    """Clone a Hugging Face Space repository"""
    print_header(f"Cloning Hugging Face Space: {space_name}")
    
    if not target_dir:
        target_dir = os.path.join(parent_dir, space_name.split("/")[-1])
    
    # Try SSH first
    success, output = run_command(f"git clone git@hf.co:spaces/{space_name} {target_dir}")
    if success:
        print(f"Successfully cloned Space using SSH to: {target_dir}")
        return target_dir
    
    print("SSH clone failed. Trying HTTPS...")
    success, output = run_command(f"git clone https://huggingface.co/spaces/{space_name} {target_dir}")
    if success:
        print(f"Successfully cloned Space using HTTPS to: {target_dir}")
        return target_dir
    else:
        print(f"Failed to clone Space: {output}")
        return None

def main():
    """Main function"""
    print_header("TEC Project - Hugging Face Space Setup")
    
    # Check for Hugging Face CLI
    if not check_huggingface_cli():
        print("Hugging Face CLI is required for this script.")
        sys.exit(1)
    
    # Install huggingface_hub if needed
    try:
        import huggingface_hub
    except ImportError:
        print("Installing huggingface_hub package...")
        success, output = run_command("pip install huggingface_hub")
        if not success:
            print(f"Failed to install huggingface_hub: {output}")
            sys.exit(1)
    
    # Menu of options
    while True:
        print("\nWhat would you like to do?")
        print("1. Set up SSH for Hugging Face")
        print("2. Install Hugging Face VS Code extension")
        print("3. Create simple Gradio app")
        print("4. Set up and deploy new HF Space")
        print("5. Clone existing HF Space")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ")
        
        if choice == "1":
            setup_ssh_for_hf()
        elif choice == "2":
            install_hf_vscode_extension()
        elif choice == "3":
            create_simple_gradio_app("TECHF")
            print("You can run this app locally with: python simple_app.py")
        elif choice == "4":
            # Login to HF
            if not login_hf():
                print("Login required to create HF Space.")
                continue
            
            # Ask for space name
            print("\nEnter the name for your Hugging Face Space.")
            print("Format should be: username/repo-name")
            print("Examples: TECHF/airth-tec-assistant, Elidorascodex/TECHF")
            space_name = input("Space name: ")
            
            # Setup local repository
            space_dir = setup_hf_space_local()
            
            # Create and deploy space
            create_hf_space(space_name, space_dir)
        elif choice == "5":
            # Ask for space name
            print("\nEnter the name of the Hugging Face Space to clone.")
            print("Format should be: username/repo-name")
            print("Examples: TECHF/airth-tec-assistant, Elidorascodex/TECHF")
            space_name = input("Space name: ")
            
            # Clone the space
            clone_hf_space(space_name)
        elif choice == "6":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")

if __name__ == "__main__":
    main()