def check_dosage_form(candidate_rows):
    if candidate_rows['dosage_form'].str.strip().eq('NA').all():
        return candidate_rows
    else:
        dosage_forms_in_kb = "\n".join(
            f"- {val}" for val in candidate_rows['dosage_form'].unique() if val != 'NA'
        )

        dosage_form = input("What is your dosage form? ").strip()

        prompt = f"""
You are a pharmaceutical regulatory expert.

A user has described this dosage form: "{dosage_form}"

Below are dosage forms from a regulatory guidance knowledge base:
{dosage_forms_in_kb}

Which of the above descriptions best matches the user's dosage form?
Output only the exact matching description(s) from the list, one per line. Nothing else.
"""
        response = model.generate_content(prompt)
        matched_items = [
            line.strip().lstrip('- ') 
            for line in response.text.strip().split("\n") 
            if line.strip()
        ]
        filtered = candidate_rows[candidate_rows['dosage_form'].isin(matched_items)]
        na_rows = candidate_rows[candidate_rows['dosage_form'].str.strip() == 'NA']
        return pd.concat([filtered, na_rows]).drop_duplicates()
    

def check_release_mechanism(candidate_rows):
    # returns filtered rows
    pass

def check_single_row(candidate_rows):
    if len(candidate_rows) == 1:
        return True
    else:
        return False

def ask_conditions(matched_row):
    # returns "proceed" or "defer"
    pass

def run_agent3(candidate_rows):
    # orchestrates the full Agent 3 flow
    # returns matched_row or "defer"
    pass