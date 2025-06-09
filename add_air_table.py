from pyairtable import Table
from pyairtable.formulas import match

# Airtable API config
AIRTABLE_TOKEN = "patn2i70wkWoPc6oJ.47cc30c3d1aa2a98408c72984007832ce06bfb6e20d312712b1b24d28cf12c03"
AIRTABLE_BASE = "app0gf8ECLPKzB9uN"
AIRTABLE_TABLE = "Dental Clinics"  # Corrected to match your goal (not 'Orders')

# New clinic entry
new_clinic_data = {
    "Clinic Name": "added_via_script",
    "Login": "added_via_script",
    "Phone Number": "(888) 123-4567",
    "Contact Name": "Dr. Jane Smith",
    "Address": "789 Elm St\nNew York, NY 10001",
    "Email": "jane@whitedent.com",
    "Website": "https://whitedent.com",
    "PIN": "5678",
    "Status": "Trial",
    "Notes": "Interested in full integration",
    "Label Template": "Template A"
}

# Connect to Airtable
table = Table(AIRTABLE_TOKEN, AIRTABLE_BASE, AIRTABLE_TABLE)

# Check if Login already exists
existing = table.first(formula=match({"Login": new_clinic_data["Login"]}))

if existing:
    print(f"❌ Clinic with login '{new_clinic_data['Login']}' already exists (ID: {existing['id']})")
else:
    inserted = table.create(new_clinic_data)
    print(f"✅ Clinic added successfully (ID: {inserted['id']})")
