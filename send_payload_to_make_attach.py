import requests

# webhook_url = "https://hook.us2.make.com/1tamgh5r56u7ij6r7drmxhlegb27avry" prod version

webhook_url = "https://hook.us2.make.com/vpkolrkjd27a0b9h81ku87a5l3dtd14t" #new version

# Prepare the metadata fields
data = {
    "loginmame": "BrightSmiles",
    "dental_clinic_name": "Bright Smiles",
    "doctor": "shasga",
    "name": "sha",
    "last-name": "sha",
    "dob": "2025-06-18",
    "due-date": "2025-06-18",
    "shade": "shade",
    "clinic number": "9295369700",
    "notes": "notes"
}
 


# Prepare image file
files = {
    "image": open("example_image.jpg", "rb")  # change to your image file
}

# Send POST request
# response = requests.post(webhook_url, data=data, files=files)
response = requests.post(webhook_url, data=data)

print("Status code:", response.status_code)
print("Response body:", response.text)
