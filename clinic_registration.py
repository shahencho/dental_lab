# clinic_registration.py
import os
from flask import Flask, render_template, request, redirect, flash, url_for
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import mysql.connector
from pyairtable import Api
from pyairtable.formulas import match

# Load .env config
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")



# DB setup
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

@app.route("/register", methods=["GET", "POST"])
def register():
        # Airtable setup
    AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
    AIRTABLE_BASE = os.getenv("AIRTABLE_BASE")
    AIRTABLE_TABLE = "Dental Clinics"  # Corrected from Orders
    api = Api(AIRTABLE_TOKEN)
    airtable = api.table(AIRTABLE_BASE, AIRTABLE_TABLE)




    if request.method == "POST":
        login = request.form.get("login")
        password = request.form.get("password")
        clinic_name = request.form.get("clinic_name")
        clinic_phone = request.form.get("clinic_phone")

        # Validate required fields
        if not all([login, password, clinic_name, clinic_phone]):
            flash("All fields are required.")
            return redirect(url_for("register"))

        # Check if login exists in Airtable
        existing = airtable.first(formula=match({"Login": login}))
        if existing:
            flash(f"❌ Clinic with login '{login}' already exists. Please use another login or contact admin.")
            return redirect(url_for("register"))

        # Insert into Airtable
        new_data = {
            "Clinic Name": clinic_name,
            "Login": login,
            "Phone Number": clinic_phone,
            "Status": "Trial",
            "Notes": "Registered via website"
        }
        inserted = airtable.create(new_data)

        # Insert into MySQL with hashed password
        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO dental_clinic (login_name, password_hash, mobile_number)
            VALUES (%s, %s, %s)
            """,
            (login, hashed_password, clinic_phone)
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash("✅ Clinic registered successfully!")
        return redirect(url_for("register"))

    return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)
