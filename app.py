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
        clinic_name = request.form['clinic']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Dental_clinic WHERE dental_clinic_name = %s", (clinic_name,))
        clinic = cursor.fetchone()
        cursor.close()
        conn.close()

        if clinic and check_password_hash(clinic['password_hash'], password):
            session['clinic'] = clinic['dental_clinic_name']
            session['clinic_number'] = clinic['mobile_number']
            return redirect(url_for('form'))

        return "Invalid credentials", 403

    return render_template('login.html')

import json

@app.route('/form', methods=['GET', 'POST'])
def form():
    if 'clinic' not in session:
        return redirect(url_for('login'))

    success_message = None

    # Handle form submission
    if request.method == 'POST':
        payload = {
            "dental_clinic_name": session['clinic'],
            "doctor": request.form['doctor'],
            "name": request.form['name'],
            "last-name": request.form['last_name'],
            "dob": request.form['dob'],
            "due-date": request.form['due_date'],
            "shade": request.form['shade'],
            "clinic number": session['clinic_number'],
            "notes": request.form['notes']
        }

        webhook_url = os.getenv("WEBHOOK_URL")

    # ✅ Get the uploaded file
        uploaded_file = request.files.get('image')
        files = {}

        if uploaded_file and uploaded_file.filename:
            files['image'] = (uploaded_file.filename, uploaded_file.stream, uploaded_file.mimetype)

        try:
            print("📤 Sending webhook with image:", uploaded_file.filename if uploaded_file else "None")
            response = requests.post(webhook_url, data=payload, files=files)
            print("✅ Webhook Response:", response.status_code)
            print("📥", response.text)

            if response.status_code == 200:
                return redirect(url_for('success'))
            else:
                success_message = f"❌ Error: Submission failed with status {response.status_code}"
        except Exception as e:
            success_message = f"❌ Error: {str(e)}"

    # Fetch Airtable records
    airtable_token = os.getenv("AIRTABLE_TOKEN")
    base_id = os.getenv("AIRTABLE_BASE")
    table_name = os.getenv("AIRTABLE_TABLE")
    url = f"https://api.airtable.com/v0/{base_id}/{table_name}"

    headers = {"Authorization": f"Bearer {airtable_token}"}
    filter_formula = f"{{Clinic Name}} = '{session['clinic']}'"
    params = {"filterByFormula": filter_formula, "pageSize": 100}

    print("=== 🔍 Fetching Airtable records ===")
    print("📛 Clinic:", session['clinic'])
    print("📄 FilterByFormula:", filter_formula)

    res = requests.get(url, headers=headers, params=params)
    airtable_rows = []

    if res.status_code == 200:
        records = res.json().get("records", [])
        airtable_rows = [r["fields"] for r in records]
        print(f"✅ Airtable returned {len(airtable_rows)} records.")
    else:
        print(f"❌ Airtable API failed: {res.status_code}")
        print("📥 Response body:", res.text)

    return render_template("form.html", clinic=session['clinic'], rows=airtable_rows, message=success_message)


@app.route('/success')
def success():
    return render_template('success.html')


@app.route('/airtable')
def airtable_view():
    if 'clinic' not in session:
        return redirect(url_for('login'))

    airtable_token = os.getenv("AIRTABLE_TOKEN")
    base_id = os.getenv("AIRTABLE_BASE")
    table_name = os.getenv("AIRTABLE_TABLE")
    clinic_name = session['clinic']

    url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
    headers = {"Authorization": f"Bearer {airtable_token}"}
    params = {
        "filterByFormula": f"{{Clinic Name}} = '{clinic_name}'",
        "pageSize": 100
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return f"Error fetching data: {response.status_code}<br>{response.text}"

    records = response.json().get('records', [])
    data = [r['fields'] for r in records]

    return render_template("airtable.html", clinic=clinic_name, rows=data)




if __name__ == '__main__':
    app.run(debug=True)
