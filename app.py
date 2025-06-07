from flask import Flask, render_template, request, redirect, session, url_for, Response, flash
from db_config import get_db_connection

from werkzeug.security import check_password_hash
from dotenv import load_dotenv
import os
import requests
import json
import re

from utils import print_readable_response 


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        webhook_url = os.getenv("WEBHOOK_URL")
        print("🔗 Webhook URL: aaaaaaaaaaaaaaaaaaaаааааааааааааааааааааааааа", webhook_url)

        actual_loginname = request.form['clinic']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM dental_clinic WHERE login_name = %s", (actual_loginname,))
        row_from_db = cursor.fetchone()
        cursor.close()
        conn.close()

        if row_from_db and check_password_hash(row_from_db['password_hash'], password):
            session['login'] = row_from_db['login_name']
            session['clinic_number'] = row_from_db['mobile_number']
            print("📛 Password hash from DB:", row_from_db['password_hash'])

            print(f"🔐 Current session login: {session['login'] }")


            return redirect(url_for('form'))

        return "Invalid credentials", 403

    return render_template('login.html')

import json
from airtable_utils import get_clinic_metadata
from airtable_utils_history import history_orders
from datetime import datetime
import traceback
import time

# Example: Sleep for 1 second
time.sleep(1)

# Get current timestamp
timestamp = time.time()
@app.route('/form', methods=['GET', 'POST'])
def form():
    if 'login' not in session:
        return redirect(url_for('login'))
    
    
    success_message = None

    getcurrentlogin = session['login']
    
    data_from_airtable= get_clinic_metadata(getcurrentlogin, "Dental Clinics")


    # Handle form submission
    if request.method == 'POST':

        
                # Mandatory Fields
        name_strip = request.form.get('name', '').strip()
        due_date_strip = request.form.get('due_date', '').strip()

        if not name_strip or not due_date_strip:
            flash("First Name and Due Date are required.")
            return redirect(url_for('form'))
        
        # sd
        try:
            due_date = datetime.strptime(due_date_strip, "%Y-%m-%d")
            if due_date.year < 1900 or due_date.year > 2100:
                raise ValueError("Unrealistic due date")
            due_date = due_date.strftime("%m/%d/%Y")
        except ValueError:
            flash("Invalid due date. Please enter a valid date between 1900 and 2100.")

            return redirect(url_for('form'))



        # Due Date parsing
        # try:
        #     due_date = datetime.strptime(due_date_strip, "%Y-%m-%d").strftime("%m/%d/%Y")
        # except ValueError:
        #     flash("Invalid due date format.")
        #     return redirect(url_for('form'))

        # Optional Fields
        last_name_strip = request.form.get('last_name', '').strip()
        dob_raw_strip = request.form.get('dob', '').strip()
        shade_strip = request.form.get('shade', '').strip()
        notes_strip = request.form.get('notes', '').strip()
        special_instructions_strip = request.form.get('specialInstructions', '').strip()
        doctor_strip = request.form.get('doctor', 'Default Doctor') #not used in the payload but can be used for future reference

        dob = ''
        if dob_raw_strip:
            try:
                dob = datetime.strptime(dob_raw_strip, "%Y-%m-%d").strftime("%m/%d/%Y")
            except ValueError:
                flash("Invalid DOB date format.")
                return redirect(url_for('form'))

            # # Convert dates to MM/DD/YYYY
            # dob = datetime.strptime(request.form['dob'], "%Y-%m-%d").strftime("%m/%d/%Y")
            # due_date = datetime.strptime(request.form['due_date'], "%Y-%m-%d").strftime("%m/%d/%Y")

        payload = {
            "record_id": data_from_airtable["record_id"],
            "dental_clinic_name": data_from_airtable["dental_clinic_name"],
            "clinic_phone_number": data_from_airtable["clinic_phone_number"],
            "patients_first_name": name_strip,
            "patients_last_name": last_name_strip,
            "patients_DOB": dob,
            "due_date": due_date,
            "shade": shade_strip,
            "notes":  notes_strip,
            # "doctor": doctor_strip,  # Optional field, can be used for future reference
            # "specialInstructions": request.form.get("specialInstructions", "")

        }

        






        webhook_url = os.getenv("WEBHOOK_URL")
        print("🔗 Webhook URL: aaaaaaaaaaaaaaaaaaa", webhook_url)

    # # ✅ Get the uploaded file
        uploaded_file = request.files.get('image')
        files = {}

        if uploaded_file and uploaded_file.filename:
            files['image'] = (uploaded_file.filename, uploaded_file.stream, uploaded_file.mimetype)
            print("📎 File uploaded:", uploaded_file.filename)
        else:
            print("📎 No file uploaded")
        try:

            # print("📤 Sending webhook with image:", uploaded_file.filename if uploaded_file else "None")
            response = requests.post(webhook_url, data=payload, files=files)
            # response = requests.post(webhook_url, data=payload)
            print("📤 Sending webhook to:", webhook_url)
            print("📤 Payload:",payload)

            print("📤 aaaaaaaaaaaaaaaaaaaaaaaa:" )
            print("📤 response.status_code:", response.status_code)
            print("📤 response.text:", response.text)
            print("📤 response.headers:", response.headers)
            print("📤 response.headers:", response.text)
            # try:
            #     print("📤 response.json():", response.json())
            # except Exception as e:
            #     print("❌ response.json() failed:", str(e))


            print("📤 aaaaaaaaaaaaaaaaaaaaaaaa:" )

            if response.status_code == 200:

                session['response_url'] = response.text
                print("📥session['response_url'] =====", session['response_url'])

                #
                 # Wait and retry if it's not a Google Docs link
                max_wait = 5
                interval = 1
                waited = 0

                while not re.search(r'/document/d/.+/(edit|preview)', session['response_url']) and waited < max_wait:
                    print(f"⏳ Waiting for URL... ({waited}s)")
                    time.sleep(interval)
                    waited += interval

                    # Optionally re-check or re-fetch from webhook if supported
                    # But here we just check if the original response_url updates (e.g. via polling API)

                    # If response_url is a redirect endpoint or status page, you might request it again here
                    # For example:
                    # followup = requests.get(response_url)
                    # if followup.status_code == 200:
                    #     response_url = followup.text.strip()
                # Final validation after waiting
                if not re.search(r'/document/d/.+/(edit|preview)', session['response_url']):
                    print("🚨🚨🚨 BIG ALARM! Webhook did NOT return a valid Google Docs URL after waiting.")
                    print(f"🧨 Final response text: {session['response_url']}")
                    print("⚠️ Proceeding with placeholder link — PDF may not be ready yet.")
                # Use regex to replace "/edit?usp=drivesdk" with "/preview" 
                modified_url = re.sub(r"/edit\?usp=drivesdk$", "/preview", response.text)
                print("🌐 Modified URL:", modified_url)
                session['response_url'] = modified_url  # Store in session for later use
                print("📥session['response_url'] after modification =====", session['response_url'])
                
                # After successful response from webhook
                # record_id = response.json().get("record_id")  # only if webhook returns it
                # print("📦 Record ID from webhook:", record_id)
                # session['last_record_id'] = record_id


                                # Read the response URL if available
                # response_url = response.headers.get("Location") or response.json().get("url") or response.json().get("link")
                # if response_url:
                #     print(f"🌐 Response URL: {response_url}")
                #     session['response_url'] = response_url  # Store in session for later use

                # # After successful response from webhook
                # record_id = response.json().get("record_id")  # Only if webhook returns it
                # print(f"📦 Record ID from webhook: {record_id}")
                # session['last_record_id'] = record_id

                # Redirect to success page
                return redirect(url_for('success'))



                return redirect(url_for('success'))
            else:
                success_message = f"❌ Error: Submission failed with status {response.status_code}"
        except Exception as e:
         
            
            print("❌ Error during webhook POST:")
            traceback.print_exc()
            success_message = f"❌ Error: {str(e)}"

    # Fetch Airtable records

    getcurrentlogin = session['login']
  
    data_from_airtable_history= history_orders(getcurrentlogin, "Orders")

    return render_template("form.html", clinic=session['login'], orders=data_from_airtable_history, message=success_message)

    # airtable_token = os.getenv("AIRTABLE_TOKEN")
    # base_id = os.getenv("AIRTABLE_BASE")
    # table_name = os.getenv("AIRTABLE_TABLE")
    # url = f"https://api.airtable.com/v0/{base_id}/{table_name}"

    # headers = {"Authorization": f"Bearer {airtable_token}"}
    # filter_formula = f"{{Clinic Name}} = '{session['clinic']}'"
    # params = {"filterByFormula": filter_formula, "pageSize": 100}

    # print("=== 🔍 Fetching Airtable records ===")
    # print("📛 Clinic:", session['clinic'])
    # print("📄 FilterByFormula:", filter_formula)

    # res = requests.get(url, headers=headers, params=params)
    # airtable_rows = []

    # if res.status_code == 200:
    #     records = res.json().get("records", [])
    #     airtable_rows = [r["fields"] for r in records]
    #     print(f"✅ Airtable returned {len(airtable_rows)} records.")
    # else:
    #     print(f"❌ Airtable API failed: {res.status_code}")
    #     print("📥 Response body:", res.text)

 

@app.route('/success')
def success():

    label_url = None
    label_url=  session.get('response_url')

    return render_template("success.html", label_url=label_url)

    # airtable_token = os.getenv("AIRTABLE_TOKEN")
    # base_id = os.getenv("AIRTABLE_BASE")
    # table_name = os.getenv("AIRTABLE_TABLE")
    # url = f"https://api.airtable.com/v0/{base_id}/{table_name}"

    # headers = {"Authorization": f"Bearer {airtable_token}"}

    # params = {
    #     "pageSize": 1,
    #     "sort[0][field]": "Date Submitted",  # Ensure Airtable is sorted by newest
    #     "sort[0][direction]": "desc"
    # }
    # # params = {"pageSize": 1}

    # label_url = None
    # response = requests.get(url, headers=headers, params=params)


    # if response.status_code == 200:
    #     records = response.json().get("records", [])
    #     if records:
    #         label_url = records[0]["fields"].get("View Label URL")
    #         print("📄 Label URL:", label_url)





@app.route('/airtable')
def airtable_view():
    if 'login' not in session:
        return redirect(url_for('login'))

    airtable_token = os.getenv("AIRTABLE_TOKEN")
    base_id = os.getenv("AIRTABLE_BASE")
    table_name = os.getenv("AIRTABLE_TABLE")
    loginname = session['login']

    url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
    headers = {"Authorization": f"Bearer {airtable_token}"}
    params = {
        "filterByFormula": f"{{Login}} = '{loginname}'",
        "pageSize": 100
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return f"Error fetching data: {response.status_code}<br>{response.text}"

    records = response.json().get('records', [])
    data = [r['fields'] for r in records]

    return render_template("airtable.html", clinic=loginname, rows=data)




@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))

from flask import Response, session
import requests

from flask import send_file, Response
import io

@app.route('/download-pdf')
def download_pdf():
    preview_url = session.get('response_url')
    if not preview_url or '/d/' not in preview_url:
        return "Invalid document URL", 400

    try:
        doc_id = preview_url.split('/d/')[1].split('/')[0]
    except IndexError:
        return "Could not extract document ID", 400

    pdf_url = f"https://docs.google.com/document/d/{doc_id}/export?format=pdf"

    r = requests.get(pdf_url)
    if r.status_code != 200:
        return "Could not fetch PDF", 502

    # Return the PDF directly from memory 
    return send_file(
        io.BytesIO(r.content),
        mimetype='application/pdf',
        as_attachment=False,
        download_name='label.pdf'
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5005)