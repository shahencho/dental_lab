from dotenv import load_dotenv
import os
import requests

load_dotenv()

def history_orders(login_value, table_name):
    """
    Fetches all orders from Airtable for the given login value.
    Returns a list of order metadata dictionaries.
    """
    token = os.getenv("AIRTABLE_TOKEN")
    base_id = os.getenv("AIRTABLE_BASE")

    if not token or not base_id:
        raise EnvironmentError("Missing AIRTABLE_TOKEN or AIRTABLE_BASE in environment.")

    url = f"https://api.airtable.com/v0/{base_id}/{table_name}" 
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    # params = {
    #     # Filter by Login field equals login_value
    #     "filterByFormula": f"{{Login}}='{login_value}'"
    # }

    params = {
    "filterByFormula": f"{{Login}}='{login_value}'",
    "sort[0][field]": "Date Submitted",
    "sort[0][direction]": "desc"
    }

    res = requests.get(url, headers=headers, params=params)

    

    if res.status_code == 200:
        records = res.json().get('records', [])

        if not records:
            print("❌ No matching records found.")
            return []

        # Process all records
        results = []
        for record in records:
            fields = record['fields']
            print("🔍 View Label:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaddddddddd", fields.get("View Label URL"))

            result = {
                "record_id": record['id'],
                "date_submitted": fields.get("Date Submitted", " "),
                "due_date": fields.get("DUE DATE", " Not "),
                "patient_first_name": fields.get("Patient First Name", " "),
                "patient_last_name": fields.get("Patient Last Name", " "),
                "notes": fields.get("Notes", " "),
                "status": fields.get("Status", " "),
                "label": fields.get("View Label URL", " ")
            }
              
            results.append(result)

        print("📦 history_orders -> Airtable Results:", results)
        return results

    else:
        raise Exception(f"Failed to fetch from Airtable: {res.status_code} | {res.text}")

# Test the function
# history_orders("brightsmiles", "Orders")