# airth.py — Manual TEC Prompt to Blog
import os
import openai
import requests
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

wp_user = os.getenv("WP_USER")
wp_pass = os.getenv("WP_APP_PASS")

# Get WP_SITE_URL from environment variables
wp_base = os.getenv("WP_SITE_URL")
if not wp_base:
    raise ValueError("Missing WP_SITE_URL in environment variables.")

# Construct the full URL
wp_url = wp_base + "/wp-json/wp/v2/posts"

def validate_env():
    required = [client.api_key, wp_user, wp_pass, wp_url]
    if not all(required):
        print("❌ Missing .env values")
        exit()

def summarize(text):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are AIRTH, summarizing a TEC article in a compelling, mythic, journalistic style."},
            {"role": "user", "content": text}
        ],
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].message.content.strip()

def post(title, content):
    res = requests.post(wp_url, auth=(wp_user, wp_pass), json={
        "title": title,
        "content": content,
        "status": "draft"
    })
    print("✅ Draft Created:", res.json().get("link"))

def get_openai_response(prompt):
    """Fetch a response from OpenAI API."""
    response = openai.Completion.create(
        engine="davinci-codex",
        prompt=prompt,
        max_tokens=50
    )
    return response.choices[0].text.strip()

def fetch_data(url):
    """Fetch JSON data from a given URL."""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    validate_env()
    raw = input("📜 Paste raw TEC content: ")
    result = summarize(raw)
    post(result.split("\n")[0][:70], result)
