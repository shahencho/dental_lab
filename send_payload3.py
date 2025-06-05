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
        print("clinic_phone_number :", phone_number)
    else:
        print("No matching record found.")
else:
    print("Error fetching data:", res.text)

import airtable_utils
# --- Webhook Section ---
# --- Webhook Section ---
# --- Webhook Section ---
webhook_url = "https://hook.us2.make.com/vpkolrkjd27a0b9h81ku87a5l3dtd14t"  

 # new version



# Prepare the metadata fields
data = {
    "record_id": clinic_id,
    "dental_clinic_name": clinic_name,
    "clinic_phone_number": phone_number,
    "patients_first_name": "shah Vardis sas aasssa with image",
    "patients_last_name": "shaha HISHI22T with image",
    "patients_DOB": "01/31/1990",
    "due-date": "01/31/2005",
    "shade": "Artshahena2k HISHIT with image",
    "notes": "2 HISHIT with image"
}

# Prepare image file
with open("example_image.jpg", "rb") as img_file:
    files = {"image": img_file}
    
    # Send POST request
    # response = requests.post(webhook_url, data=data, files=files)
    response = requests.post(webhook_url, data=data )

# --- Print readable payload only ---
print("📥Payload manual  ", data)


print("\n=== REQUEST PAYLOAD ===")
print("Metadata Fields:")
for key, value in data.items():
    print(f"  {key}: {value}")

print("\nFile Uploaded:")
print(f"  Filename: example_image.jpg")
print("=== END OF PAYLOAD ===")

# --- Response ---
print("\nStatus code:", response.status_code)
print("Response body:", response.text)