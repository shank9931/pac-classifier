import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure your API key
genai.configure(api_key=os.getenv("api_key"))

# Initialize the model
model = genai.GenerativeModel("gemini-2.5-flash")

# A sample PAC change description
change_description = """
The active substance is currently stored in double polyethe bags inside fibre drums with an approved re-test period of 24 months.
During routine stability monitoring, the marketing authorization holder generated new long term stability data showing that the active substance remains within specification for upto 36 months under ICH storage conditions.
However, evaluation of the data indicated that the current polyethylene packaging has limited moisture barrier properties, which may not sufficiently protect the active susbtance for the proposed extended storage period.
"""

# The prompt
prompt = f"""
You are a pharmaceutical regulatory expert. 
Based on the following post-approval change description, identify the change items. 
The change item is an isolation of an activity that is causing a modification to the status-quo.

For example:

if change description: The manufacturer proposes to change the tablet coating from HPMC-based to a PVA-based film coat using Opadry II. The drug product is an 
immediate release oral tablet. No change to core formulation. then change item: change in tablet coating 

Change description:{change_description}

Output only the change items as a numbered list. Nothing else.
"""

# Call the API
response = model.generate_content(prompt)

# Print the result
print(response.text)