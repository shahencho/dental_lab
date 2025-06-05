import requests

# --- Config ---
token = "patn2i70wkWoPc6oJ.47cc30c3d1aa2a98408c72984007832ce06bfb6e20d312712b1b24d28cf12c03"
base_id = "app0gf8ECLPKzB9uN"
table_name = "Dental Clinics"

url = f"https://api.airtable.com/v0/{base_id}/{table_name}" 

headers = {
    "Authorization": f"Bearer {token}"
}

# --- Filter by Login field ---
params = {
    "filterByFormula": "{Login}='brightsmiles'"
}

# --- Fetch Data ---
res = requests.get(url, headers=headers, params=params)

# --- Output ---
print("Status Code:", res.status_code)
if res.status_code == 200:
    records = res.json().get('records', [])
    if records:
        first_record = records[0]
        fields = first_record['fields']
        
        # Get Dental Clinic ID (adjust field name if needed)
        clinic_id = fields.get("Dental Clinic ID", "Not Found")
        clinic_name = fields.get("Clinic Name", "Not Found")
        phone_number = fields.get("Phone Number", "Not Found")
        
        print("\nMatching Record Found!")
        print("Dental Clinic ID:", clinic_id)
        print("clinic_name :", clinic_name)
        print("clinic_name :", phone_number)
    else:
        print("No matching record found.")
else:
    print("Error fetching data:", res.text)
    

