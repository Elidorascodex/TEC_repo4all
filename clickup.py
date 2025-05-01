# clickup.py — AIRTH's ClickUp-to-WP Automation
import os
import requests
import openai
from dotenv import load_dotenv

load_dotenv()

# Load Env Vars
openai.api_key = os.getenv("OPENAI_API_KEY")
clickup_token = os.getenv("CLICKUP_API_TOKEN")
clickup_list = os.getenv("CLICKUP_LIST_ID")
wp_url = os.getenv("WP_SITE_URL") + "/wp-json/wp/v2/posts"
wp_user = os.getenv("WP_USER")
wp_pass = os.getenv("WP_APP_PASS")

# Validate Env Setup
def validate_env():
    """
    Validate that all necessary environment variables are set.
    """
    vars_needed = [openai.api_key, clickup_token, clickup_list, wp_url, wp_user, wp_pass]
    if not all(vars_needed):
        print("❌ Missing one or more .env variables. Check your .env file.")
        exit()

# Fetch Tasks from ClickUp
def fetch_tasks():
    """
    Fetch tasks from ClickUp.
    
    Returns:
        list: A list of tasks.
    """
    headers = {"Authorization": clickup_token}
    url = f"https://api.clickup.com/api/v2/list/{clickup_list}/task"
    r = requests.get(url, headers=headers)
    return r.json().get("tasks", [])

# Summarize Task into Blog Post
def summarize(text):
    """
    Summarize a ClickUp task into a blog post draft.
    
    Args:
        text (str): The text of the ClickUp task.
    
    Returns:
        str: The summarized blog post draft.
    """
    res = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You're AIRTH, TEC's mythic blog AI. Summarize this ClickUp task as a compelling WordPress draft."},
            {"role": "user", "content": text}
        ]
    )
    return res.choices[0].message.content

# Post to WordPress
def post(title, content):
    """
    Post a blog draft to WordPress.
    
    Args:
        title (str): The title of the blog post.
        content (str): The content of the blog post.
    """
    res = requests.post(wp_url, auth=(wp_user, wp_pass), json={
        "title": title,
        "content": content,
        "status": "draft",
        "categories": [1]
    })
    print("✅ Posted:", res.json().get("link"))

if __name__ == "__main__":
    validate_env()
    for task in fetch_tasks():
        raw = task.get("description", "")
        if raw:
            blog = summarize(raw)
            post(blog.split("\n")[0][:70], blog)
