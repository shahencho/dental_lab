from dotenv import load_dotenv
import os
import requests

load_dotenv()

def get_clinic_metadata(login_value, table_name):
    """
    Fetches clinic metadata (ID, name, phone number) from Airtable
    based on the provided login value.
    """
    token = os.getenv("AIRTABLE_TOKEN")
    base_id = os.getenv("AIRTABLE_BASE")

    if not token or not base_id:
        raise EnvironmentError("Missing AIRTABLE_TOKEN or AIRTABLE_BASE in environment.")

    url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "filterByFormula": f"{{Login}}='{login_value}'"
    }

    res = requests.get(url, headers=headers, params=params)

    if res.status_code == 200:
        records = res.json().get('records', [])
        if records:
            fields = records[0]['fields']
            result = {
                "record_id": records[0].get('id', 'Not Found'),
                "dental_clinic_name": fields.get("Clinic Name", "Not Found"),
                "clinic_phone_number": fields.get("Phone Number", "Not Found")
            }
            print("📦 get_clinic_metadata -> Airtable Result:", result)  # <-- Logging the result
            return result
        else:
            raise ValueError("No matching record found for login.")
    else:
        raise Exception(f"Failed to fetch from Airtable: {res.status_code} {res.text}")

# get_clinic_metadata("brightsmiles", "Orders")