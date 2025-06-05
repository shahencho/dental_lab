from flask import Flask, render_template, request, redirect, session, url_for
from db_config import get_db_connection
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
import os
import requests
import json

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
        cursor.execute("SELECT * FROM Dental_clinic WHERE login_name = %s", (actual_loginname,))
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
@app.route('/form', methods=['GET', 'POST'])
def form():
    if 'login' not in session:
        return redirect(url_for('login'))
    

    


    success_message = None

    getcurrentlogin = session['login']

    
    data_from_airtable= get_clinic_metadata(getcurrentlogin, "Dental Clinics")



    # Handle form submission
    if request.method == 'POST':
        
        
        # Convert dates to MM/DD/YYYY
        dob = datetime.strptime(request.form['dob'], "%Y-%m-%d").strftime("%m/%d/%Y")
        due_date = datetime.strptime(request.form['due_date'], "%Y-%m-%d").strftime("%m/%d/%Y")

        payload = {
            "record_id": data_from_airtable["record_id"],
            "dental_clinic_name": data_from_airtable["dental_clinic_name"],
            "clinic_phone_number": data_from_airtable["clinic_phone_number"],
            "patients_first_name": request.form['name'],
            "patients_last_name": request.form['last_name'],
            "patients_DOB": dob,
            "due-date": due_date,
            "shade": request.form['shade'],
            "notes": request.form['notes']
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

            # response = requests.post(webhook_url, data=payload)

            print("✅ Webhook Response:", response.status_code)
            print("📥Payload ", payload)
            print("📥", response.text)

            if response.status_code == 200:

                # After successful response from webhook
                # record_id = response.json().get("record_id")  # only if webhook returns it
                # print("📦 Record ID from webhook:", record_id)
                # session['last_record_id'] = record_id
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
    airtable_token = os.getenv("AIRTABLE_TOKEN")
    base_id = os.getenv("AIRTABLE_BASE")
    table_name = os.getenv("AIRTABLE_TABLE")
    url = f"https://api.airtable.com/v0/{base_id}/{table_name}"

    headers = {"Authorization": f"Bearer {airtable_token}"}

    params = {
        "pageSize": 1,
        "sort[0][field]": "Date Submitted",  # Ensure Airtable is sorted by newest
        "sort[0][direction]": "desc"
    }
    # params = {"pageSize": 1}

    label_url = None
    response = requests.get(url, headers=headers, params=params)


    if response.status_code == 200:
        records = response.json().get("records", [])
        if records:
            label_url = records[0]["fields"].get("View Label URL")
            print("📄 Label URL:", label_url)

    return render_template("success.html", label_url=label_url)



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


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
