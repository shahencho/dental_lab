import requests

webhook_url = "https://hook.us2.make.com/1tamgh5r56u7ij6r7drmxhlegb27avry"

# Prepare the metadata fields
data = {
    "dental_clinic_name": "Dental Clinic 33",
    "doctor": "Dental Clinic tst32",
    "name": "Dental Clinic  32",
    "last-name": "pat_lastname32",
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
response = requests.post(webhook_url, data=data, files=files)

print("Status code:", response.status_code)
print("Response body:", response.text)
