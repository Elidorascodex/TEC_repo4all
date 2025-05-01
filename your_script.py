"""
Your Script for Automating ClickUp and WordPress Integration
"""

from dotenv import load_dotenv
import os
import requests

# Load environment variables from .env file
load_dotenv()

# Access environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
clickup_api_token = os.getenv("CLICKUP_API_TOKEN")
clickup_list_id = os.getenv("CLICKUP_LIST_ID")
wp_site_url = os.getenv("WP_SITE_URL")
wp_user = os.getenv("WP_USER")
wp_app_pass = os.getenv("WP_APP_PASS")


def validate_env_vars():
    """
    Validate that all required environment variables are loaded.
    """
    required_vars = {
        "OPENAI_API_KEY": openai_api_key,
        "CLICKUP_API_TOKEN": clickup_api_token,
        "CLICKUP_LIST_ID": clickup_list_id,
        "WP_SITE_URL": wp_site_url,
        "WP_USER": wp_user,
        "WP_APP_PASS": wp_app_pass,
    }
    for var_name, var_value in required_vars.items():
        if not var_value:
            print(f"Error: Missing environment variable {var_name}")
            return False
    return True


def fetch_clickup_tasks():
    """
    Fetch tasks from ClickUp using the API.
    """
    if not validate_env_vars():
        print("Environment validation failed. Exiting.")
        return []

    headers = {"Authorization": clickup_api_token}
    url = f"https://api.clickup.com/api/v2/list/{clickup_list_id}/task"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("tasks", [])
    print("Failed to fetch tasks:", response.json())
    return []


def post_to_wordpress(title, content):
    """
    Post a task to WordPress as a blog post.
    """
    if not validate_env_vars():
        print("Environment validation failed. Exiting.")
        return False

    url = f"{wp_site_url}/wp-json/wp/v2/posts"
    auth = (wp_user, wp_app_pass)
    data = {"title": title, "content": content, "status": "publish"}
    response = requests.post(url, auth=auth, json=data)
    if response.status_code == 201:
        print("Post published successfully:", response.json().get("link"))
        return True
    print("Failed to publish post:", response.json())
    return False


if __name__ == "__main__":
    tasks = fetch_clickup_tasks()
    for task in tasks:
        title = task.get("name", "Untitled Task")
        content = task.get("description", "No description provided.")
        post_to_wordpress(title, content)
