// ===============================
// APPOINTMENT - FLASK + MYSQL
// ===============================

// Load appointments when page opens
document.addEventListener("DOMContentLoaded", function () {

    loadAppointments();

    // Set today's date as minimum date
    let today = new Date().toISOString().split("T")[0];
    let dateField = document.getElementById("appointmentDate");

    if (dateField) {
        dateField.setAttribute("min", today);
    }

});

// ===============================
// BOOK APPOINTMENT
// ===============================
async function bookAppointment() {

    let patient = document.getElementById("patientName").value.trim();
    let doctor = document.getElementById("doctorSelect").value;
    let date = document.getElementById("appointmentDate").value;
    let time = document.getElementById("appointmentTime").value;
    let symptoms = document.getElementById("symptoms").value.trim();

    if (patient === "" || doctor === "" || date === "" || time === "") {
        alert("Please fill all appointment details.");
        return;
    }

    let appointment = {
        patient_name: patient,
        doctor_name: doctor,
        appointment_date: date,
        appointment_time: time,
        symptoms: symptoms
    };

    try {

        const response = await fetch("/appointment", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(appointment)
        });

        const result = await response.json();

        if (result.success) {

            alert("Appointment Booked Successfully!");

            // Clear form
            document.getElementById("patientName").value = "";
            document.getElementById("doctorSelect").value = "";
            document.getElementById("appointmentDate").value = "";
            document.getElementById("appointmentTime").value = "";
            document.getElementById("symptoms").value = "";

            loadAppointments();

        } else {
            alert(result.message);
        }

    } catch (error) {
        alert("Server Error! Please try again.");
        console.log(error);
    }

}

// ===============================
// LOAD APPOINTMENTS FROM MYSQL
// ===============================
async function loadAppointments() {

    let table = document.getElementById("appointmentTable");

    if (!table) return;

    table.innerHTML = `
        <tr>
            <th>Patient</th>
            <th>Doctor</th>
            <th>Date</th>
            <th>Time</th>
            <th>Symptoms</th>
            <th>Status</th>
            <th>Action</th>
        </tr>
    `;

    try {

        const response = await fetch("/get_appointments");
        const appointments = await response.json();

        appointments.forEach((appointment) => {

            let row = table.insertRow();

            row.insertCell(0).innerHTML = appointment.patient_name;
            row.insertCell(1).innerHTML = appointment.doctor_name;
            row.insertCell(2).innerHTML = appointment.appointment_date;
            row.insertCell(3).innerHTML = appointment.appointment_time;
            row.insertCell(4).innerHTML = appointment.symptoms;
            row.insertCell(5).innerHTML =
                `<span style="color:green;font-weight:bold;">${appointment.status}</span>`;

            row.insertCell(6).innerHTML =
                `<button class="delete-btn"
                    onclick="deleteAppointment(${appointment.id})">
                    Delete
                </button>`;
        });

    } catch (error) {
        console.log("Error loading appointments:", error);
    }

}

// ===============================
// DELETE APPOINTMENT FROM MYSQL
// ===============================
async function deleteAppointment(id) {

    if (!confirm("Are you sure you want to delete this appointment?")) {
        return;
    }

    try {

        const response = await fetch(`/delete_appointment/${id}`, {
            method: "DELETE"
        });

        const result = await response.json();

        if (result.success) {
            alert("Appointment Deleted Successfully!");
            loadAppointments();
        } else {
            alert(result.message);
        }

    } catch (error) {
        console.log(error);
        alert("Error deleting appointment.");
    }

}