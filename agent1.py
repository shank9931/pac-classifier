import google.generativeai as genai
import os
from dotenv import load_dotenv
import re

load_dotenv()

# Configure your API key
genai.configure(api_key=os.getenv("api_key"))

# Initialize the model
model = genai.GenerativeModel("gemini-2.5-flash")

def extract_change_items(change_description):
    prompt = f"""
You are a pharmaceutical regulatory expert. 
Based on the following post-approval change description, identify the change items. 
The change item is an isolation of an activity that is causing a modification to the status-quo.

For example:

if change description: I want to change my primary packaging from HDPE to glass and also extend the shelf life from 24 to 36 months 
then change items: 1. change in primary packaging material 2. change in approved shelf life

Change description: {change_description}

Output only the change items as a numbered list. Nothing else.
"""
    response = model.generate_content(prompt)
    return response.text

def parse_change_items(text):
    lines = text.strip().split("\n")
    items = []
    for line in lines:
        cleaned = line.strip()
        if cleaned:
            # Remove the number and dot at the start e.g. "1. "
            parsed = re.sub(r'^\d+\.\s*', '', cleaned)
            items.append(parsed.lower())
    return items

if __name__ == "__main__":
    test_input = "I want to change my primary packaging from HDPE to glass and also extend the shelf life from 24 to 36 months"
    raw = extract_change_items(test_input)
    print("Raw output:")
    print(raw)
    print()
    items = parse_change_items(raw)
    print("Parsed list:")
    print(items)