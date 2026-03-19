import pandas as pd
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("api_key"))
model = genai.GenerativeModel("gemini-2.5-flash")

def load_knowledge_base():
    df = pd.read_excel('canada2.ods', engine='odf', header=1)
    df['change_item'] = df['change_item'].str.strip()
    return df

def collect_user_context():
    print("What is your market?")
    market = input("> ").strip()
    print("What is your material type? (Drug Substance / Drug Product / Excipient)")
    material_type = input("> ").strip()
    return market, material_type

def exact_filter(df, market, material_type):
    filtered = df[
        (df['market'].str.lower() == market.lower()) &
        (df['material_type'].str.lower() == material_type.lower())
    ]
    return filtered

def semantic_match(change_item, candidate_rows):
    change_items_text = "\n".join(
        f"- {row}" for row in candidate_rows['change_item'].unique()
    )
    prompt = f"""
You are a pharmaceutical regulatory expert.

A user has described this change item: "{change_item}"

Below are change item descriptions from a regulatory guidance knowledge base:
{change_items_text}

Which of the above descriptions best matches the user's change item?
Output only the exact matching description(s) from the list, one per line. Nothing else.
"""
    response = model.generate_content(prompt)
    
    # Debug: see what came back
    print("Finish reason:", response.candidates[0].finish_reason)
    print("Parts:", response.candidates[0].content.parts)
    
    if not response.candidates or not response.candidates[0].content.parts:
        print("Warning: no valid response from LLM")
        return ""
    
    return response.text.strip()

def get_candidate_rows(change_items, market, material_type):
    df = load_knowledge_base()
    filtered = exact_filter(df, market, material_type)
    
    all_candidates = []
    
    for item in change_items:
        print(f"\nFinding matches for: {item}")
        matched_text = semantic_match(item, filtered)
        print(f"Matched to: {matched_text}")
        
        # Find rows where change_item matches the LLM output
        matched_items = [line.strip() for line in matched_text.split("\n") if line.strip()]
        matched_rows = filtered[filtered['change_item'].isin(matched_items)]
        
        all_candidates.append({
            "change_item": item,
            "matched_rows": matched_rows
        })
    
    return all_candidates

if __name__ == "__main__":
    from agent1 import extract_change_items, parse_change_items
    
    user_input = input("Describe your proposed change: ")
    raw = extract_change_items(user_input)
    change_items = parse_change_items(raw)
    
    print(f"\nExtracted change items: {change_items}")
    
    market, material_type = collect_user_context()
    candidates = get_candidate_rows(change_items, market, material_type)
    
    for result in candidates:
        print(f"\nChange item: {result['change_item']}")
        print(f"Candidate rows found: {len(result['matched_rows'])}")
        print(result['matched_rows'][['change_item', 'change_scenario', 'filing_type']])