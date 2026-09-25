from flask import Flask, render_template, request, redirect
from database import get_db_connection

# ADD THESE IMPORTS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# Gmail Configuration
EMAIL_ADDRESS = "chandu06112006@gmail.com"
EMAIL_PASSWORD = "dmgl ctzv isfx fvoz"


def send_registration_email(patient_name, patient_email, village):

    subject = "Registration Successful - Smart Healthcare"

    body = f"""
Dear {patient_name},

Welcome to Smart Healthcare Management System!

Your registration has been completed successfully.

Patient Details
-------------------------
Name    : {patient_name}
Village : {village}

Thank you for registering with Smart Healthcare.

Regards,
Smart Healthcare Team
"""

    message = MIMEMultipart()
    message["From"] = EMAIL_ADDRESS
    message["To"] = patient_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(message)
        server.quit()
        print("Email sent successfully.")

    except Exception as e:
        print("Email Error:", e)

# ==========================
# HOME PAGE
# ==========================
@app.route("/")
def home():
    return render_template("index.html")


# ==========================
# PATIENT REGISTRATION
# ==========================
@app.route("/patient", methods=["GET", "POST"])
def patient():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        phone = request.form["phone"]
        email = request.form["email"]      # NEW
        village = request.form["village"]

        cursor.execute("""
            INSERT INTO patients(name, age, gender, phone, email, village)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (name, age, gender, phone, email, village))

        conn.commit()
        send_registration_email(name, email, village)

    cursor.execute("SELECT * FROM patients ORDER BY id DESC")
    patients = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("patient.html", patients=patients)


# ==========================
# DOCTOR REGISTRATION
# ==========================
@app.route("/doctor", methods=["GET", "POST"])
def doctor():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        name = request.form["doctorName"]
        specialization = request.form["specialization"]
        phone = request.form["doctorPhone"]
        email = request.form["email"]
        experience = request.form["experience"]
        available_time = request.form["available_time"]
        cursor.execute(
            """
            INSERT INTO doctors(name, specialization, phone)
            VALUES (%s,%s,%s)
            """,
            (name, specialization, phone),
        )

        conn.commit()
        return redirect("/doctor")

    cursor.execute("SELECT * FROM doctors ORDER BY id DESC")
    doctors = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("doctor.html", doctors=doctors)


# ==========================
# APPOINTMENT BOOKING
# ==========================
@app.route("/appointment", methods=["GET", "POST"])
def appointment():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get doctors for dropdown
    cursor.execute("SELECT name, specialization FROM doctors")
    doctors = cursor.fetchall()

    if request.method == "POST":
        patient = request.form["patientName"]
        doctor = request.form["doctorSelect"]
        date = request.form["appointmentDate"]
        time = request.form["appointmentTime"]
        symptoms = request.form["symptoms"]

        cursor.execute("""
            INSERT INTO appointments
            (patient, doctor, date, time, symptoms, status)
            VALUES (%s,%s,%s,%s,%s,'Confirmed')
        """, (patient, doctor, date, time, symptoms))

        conn.commit()
        return redirect("/appointment")

    # Get all appointments
    cursor.execute("SELECT * FROM appointments ORDER BY id DESC")
    appointments = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "appointment.html",
        doctors=doctors,
        appointments=appointments
    )


# ==========================
# MEDICAL RECORDS
# ==========================
@app.route("/records", methods=["GET", "POST"])
def records():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":

        patient = request.form["patient"]
        doctor = request.form["doctor"]
        diagnosis = request.form["diagnosis"]
        medicines = request.form["medicines"]
        bp = request.form["bp"]
        followup = request.form["followup"]

        cursor.execute(
            """
            INSERT INTO medical_records
            (patient, doctor, diagnosis, medicines, bp, followup_date)
            VALUES (%s,%s,%s,%s,%s,%s)
            """,
            (patient, doctor, diagnosis, medicines, bp, followup),
        )

        conn.commit()

        return redirect("/records")

    # Patient dropdown
    cursor.execute("SELECT name FROM patients ORDER BY name")
    patients = cursor.fetchall()

    # Doctor dropdown
    cursor.execute("SELECT name, specialization FROM doctors ORDER BY name")
    doctors = cursor.fetchall()

    # Medical Records table
    cursor.execute("SELECT * FROM medical_records ORDER BY id DESC")
    records = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "records.html",
        patients=patients,
        doctors=doctors,
        records=records,
    )


# ==========================
# RECEIPT PAGE
# ==========================
@app.route("/receipt")
def receipt():
    return render_template("receipt.html")


# ==========================
# DASHBOARD
# ==========================
@app.route("/dashboard")
def dashboard():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Total Patients
    cursor.execute("SELECT COUNT(*) AS total FROM patients")
    total_patients = cursor.fetchone()["total"]

    # Total Doctors
    cursor.execute("SELECT COUNT(*) AS total FROM doctors")
    total_doctors = cursor.fetchone()["total"]

    # Total Appointments
    cursor.execute("SELECT COUNT(*) AS total FROM appointments")
    total_appointments = cursor.fetchone()["total"]

    # Total Medical Records
    cursor.execute("SELECT COUNT(*) AS total FROM medical_records")
    total_records = cursor.fetchone()["total"]

    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",
        total_patients=total_patients,
        total_doctors=total_doctors,
        total_appointments=total_appointments,
        total_records=total_records
    )

@app.route("/prediction", methods=["GET", "POST"])
def prediction():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    prediction = None

    if request.method == "POST":
        patient_name = request.form["patient_name"]
        age = request.form["age"]
        temperature = float(request.form["temperature"])
        blood_pressure = request.form["blood_pressure"]
        symptoms = request.form["symptoms"]

        # Simple prediction logic
        if temperature >= 39:
            risk_level = "High"
            suggested_doctor = "General Physician"
            advice = "Visit the hospital immediately."
        elif temperature >= 37.5:
            risk_level = "Medium"
            suggested_doctor = "General Physician"
            advice = "Take rest, drink fluids and consult a doctor."
        else:
            risk_level = "Low"
            suggested_doctor = "Family Doctor"
            advice = "Monitor your health and maintain hydration."

        cursor.execute("""
            INSERT INTO health_predictions
            (patient_name, age, temperature, blood_pressure,
             symptoms, risk_level, suggested_doctor, advice)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            patient_name, age, temperature,
            blood_pressure, symptoms,
            risk_level, suggested_doctor, advice
        ))
        conn.commit()

        prediction = {
            "risk_level": risk_level,
            "suggested_doctor": suggested_doctor,
            "advice": advice
        }

    cursor.execute("SELECT * FROM health_predictions ORDER BY id DESC")
    predictions = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "prediction.html",
        prediction=prediction,
        predictions=predictions
    )


# ==========================
# RUN APPLICATION
# ==========================
if __name__ == "__main__":
    app.run(debug=True)