#!/usr/bin/env python3
"""
Authentication Setup Utility for TEC Project
Helps set up SSH keys and access tokens for GitHub and Hugging Face
"""
import os
import sys
import subprocess
import getpass
import json
import platform
from pathlib import Path
import webbrowser

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

def setup_ssh_key(service_name, email):
    """Generate and setup SSH key for a service"""
    print_header(f"Setting up SSH key for {service_name}")
    
    # Create SSH directory if it doesn't exist
    ssh_dir = os.path.expanduser("~/.ssh")
    os.makedirs(ssh_dir, exist_ok=True)
    
    # Generate key filename
    key_filename = os.path.join(ssh_dir, f"id_ed25519_{service_name.lower()}")
    
    # Check if key already exists
    if os.path.exists(key_filename):
        overwrite = input(f"SSH key for {service_name} already exists. Overwrite? (y/n): ")
        if overwrite.lower() != 'y':
            print(f"Keeping existing SSH key for {service_name}")
            with open(f"{key_filename}.pub", "r") as f:
                public_key = f.read().strip()
            return key_filename, public_key
    
    # Generate new SSH key
    print(f"Generating new SSH key for {service_name}...")
    success, output = run_command(
        f'ssh-keygen -t ed25519 -C "{email}" -f "{key_filename}" -N ""'
    )
    
    if not success:
        print(f"Failed to generate SSH key: {output}")
        return None, None
        
    # Read the public key
    with open(f"{key_filename}.pub", "r") as f:
        public_key = f.read().strip()
        
    print(f"SSH key generated: {key_filename}")
    return key_filename, public_key

def configure_ssh_config(services):
    """Configure SSH config file"""
    print_header("Configuring SSH Config")
    
    config_file = os.path.expanduser("~/.ssh/config")
    
    # Check if config exists and read it
    config_exists = os.path.exists(config_file)
    existing_config = ""
    if config_exists:
        with open(config_file, "r") as f:
            existing_config = f.read()
    
    # Create or append to config
    with open(config_file, "a") as f:
        if config_exists:
            f.write("\n\n# Added by TEC Setup\n")
        
        for service, key_file in services.items():
            service_domain = "github.com" if service == "GitHub" else "huggingface.co"
            
            # Check if the host is already in the config
            if service_domain in existing_config:
                print(f"Host {service_domain} already in SSH config. Skipping.")
                continue
                
            f.write(f"\nHost {service_domain}\n")
            f.write(f"  HostName {service_domain}\n")
            f.write(f"  User git\n")
            f.write(f"  IdentityFile {key_file}\n")
            f.write(f"  IdentitiesOnly yes\n")
    
    print(f"SSH config updated: {config_file}")

def setup_github():
    """Setup GitHub SSH and access token"""
    print_header("GitHub Setup")
    
    # 1. Get GitHub email
    github_email = input("Enter your GitHub email: ")
    
    # 2. Setup SSH key
    key_file, public_key = setup_ssh_key("GitHub", github_email)
    if not key_file:
        return
    
    # 3. Open GitHub SSH settings page
    print("\nCopy your SSH public key to add to GitHub:")
    print(f"\n{public_key}\n")
    
    open_browser = input("Open GitHub SSH key settings in browser? (y/n): ")
    if open_browser.lower() == 'y':
        webbrowser.open("https://github.com/settings/keys")
    
    # 4. Setup Personal Access Token
    print("\nYou'll need a GitHub Personal Access Token for automation.")
    print("Tokens can be created at: https://github.com/settings/tokens")
    
    open_browser = input("Open GitHub token settings in browser? (y/n): ")
    if open_browser.lower() == 'y':
        webbrowser.open("https://github.com/settings/tokens")
    
    # Save SSH key file path
    return key_file

def setup_huggingface():
    """Setup Hugging Face SSH and access token"""
    print_header("Hugging Face Setup")
    
    # 1. Get Hugging Face email
    hf_email = input("Enter your Hugging Face email: ")
    
    # 2. Setup SSH key
    key_file, public_key = setup_ssh_key("HuggingFace", hf_email)
    if not key_file:
        return
    
    # 3. Open Hugging Face SSH settings page
    print("\nCopy your SSH public key to add to Hugging Face:")
    print(f"\n{public_key}\n")
    
    open_browser = input("Open Hugging Face SSH key settings in browser? (y/n): ")
    if open_browser.lower() == 'y':
        webbrowser.open("https://huggingface.co/settings/keys")
    
    # 4. Setup Access Token
    print("\nYou'll need a Hugging Face Access Token for API access and automation.")
    print("Tokens can be created at: https://huggingface.co/settings/tokens")
    
    open_browser = input("Open Hugging Face token settings in browser? (y/n): ")
    if open_browser.lower() == 'y':
        webbrowser.open("https://huggingface.co/settings/tokens")
    
    # 5. Ask user to enter token for local config
    hf_token = getpass.getpass("\nEnter your Hugging Face Access Token (input will be hidden): ")
    if hf_token:
        # Save token to .env file
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
        
        if os.path.exists(env_file):
            with open(env_file, "r") as f:
                env_content = f.read()
            
            if "HF_TOKEN=" in env_content:
                print("HF_TOKEN already exists in .env file. Not modifying.")
            else:
                with open(env_file, "a") as f:
                    f.write(f"\nHF_TOKEN={hf_token}\n")
                print("Added HF_TOKEN to .env file")
        else:
            with open(env_file, "w") as f:
                f.write(f"HF_TOKEN={hf_token}\n")
            print("Created .env file with HF_TOKEN")
    
    # Save SSH key file path
    return key_file

def setup_github_webhook(repo_name):
    """Setup GitHub webhook for automatic deployments"""
    print_header("GitHub Webhook Setup")
    
    print("To set up automated deployments, you'll need to create a webhook in your GitHub repository")
    print(f"1. Go to https://github.com/{repo_name}/settings/hooks")
    print("2. Click 'Add webhook'")
    print("3. Set Payload URL to your deployment endpoint")
    print("4. Set Content type to 'application/json'")
    print("5. Select 'Let me select individual events' and choose 'Pushes'")
    print("6. Ensure 'Active' is checked")
    
    open_browser = input(f"Open GitHub webhook settings for {repo_name} in browser? (y/n): ")
    if open_browser.lower() == 'y':
        webbrowser.open(f"https://github.com/{repo_name}/settings/hooks")

def setup_vscode_ssh():
    """Setup VS Code SSH configuration"""
    print_header("VS Code SSH Configuration")
    
    print("For seamless integration with VS Code:")
    print("1. Install the 'Remote - SSH' extension in VS Code")
    print("2. Use the 'Remote-SSH: Connect to Host' command to connect to your repositories")
    
    # Check if VS Code is installed
    vscode_path = None
    if platform.system() == "Windows":
        possible_paths = [
            os.path.expandvars("%LOCALAPPDATA%\\Programs\\Microsoft VS Code\\Code.exe"),
            os.path.expandvars("%APPDATA%\\Local\\Programs\\Microsoft VS Code\\Code.exe"),
            "C:\\Program Files\\Microsoft VS Code\\Code.exe"
        ]
        for path in possible_paths:
            if os.path.exists(path):
                vscode_path = path
                break
    elif platform.system() == "Darwin":  # macOS
        vscode_path = "/Applications/Visual Studio Code.app"
    else:  # Linux
        success, _ = run_command("which code", shell=True)
        if success:
            vscode_path = "code"
    
    if vscode_path:
        print(f"VS Code detected: {vscode_path}")
        install_extension = input("Install 'Remote - SSH' extension now? (y/n): ")
        if install_extension.lower() == 'y':
            if platform.system() == "Darwin":
                success, output = run_command("/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code --install-extension ms-vscode-remote.remote-ssh")
            else:
                success, output = run_command(f"{vscode_path} --install-extension ms-vscode-remote.remote-ssh")
                
            if success:
                print("Remote - SSH extension installed successfully!")
            else:
                print(f"Failed to install extension: {output}")
    else:
        print("VS Code not detected. Please install the 'Remote - SSH' extension manually.")

def main():
    """Main function"""
    print_header("TEC Project Authentication Setup")
    
    print("This script will help you set up SSH keys and access tokens for GitHub and Hugging Face")
    print("These will be used for secure access to repositories and APIs")
    
    # Setup GitHub
    github_key = None
    setup_gh = input("Set up GitHub authentication? (y/n): ")
    if setup_gh.lower() == 'y':
        github_key = setup_github()
    
    # Setup Hugging Face
    hf_key = None
    setup_hf = input("Set up Hugging Face authentication? (y/n): ")
    if setup_hf.lower() == 'y':
        hf_key = setup_huggingface()
    
    # Configure SSH config file if keys were generated
    ssh_services = {}
    if github_key:
        ssh_services["GitHub"] = github_key
    if hf_key:
        ssh_services["HuggingFace"] = hf_key
        
    if ssh_services:
        configure_ssh_config(ssh_services)
    
    # Setup GitHub webhook
    setup_webhook = input("Set up GitHub webhook for automated deployments? (y/n): ")
    if setup_webhook.lower() == 'y':
        repo_name = input("Enter your GitHub repository name (username/repo): ")
        setup_github_webhook(repo_name)
    
    # Setup VS Code SSH integration
    setup_vscode = input("Configure VS Code for SSH integration? (y/n): ")
    if setup_vscode.lower() == 'y':
        setup_vscode_ssh()
    
    print_header("Setup Complete")
    print("Authentication setup complete! You can now use SSH and access tokens for GitHub and Hugging Face.")
    print("Use these in your workflows, VS Code, and for automated deployments.")

if __name__ == "__main__":
    main()