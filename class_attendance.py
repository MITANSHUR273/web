from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from datetime import datetime
#pip install openpyxl
#pip install pandas
#pip install flask
#pip install flask-sqlalchemy


app = Flask(__name__)

# Configure SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///attendance.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Define the Attendance model
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    house_or_class = db.Column(db.String(100), nullable=False)  # This will store either House or Class
    category = db.Column(db.String(50), nullable=True)  # This will be used for house attendance only
    total = db.Column(db.Integer, nullable=False)
    present = db.Column(db.Integer, nullable=False)
    absent = db.Column(db.Integer, nullable=False)
    on_duty = db.Column(db.Integer, nullable=False)
    leave = db.Column(db.Integer, nullable=False)
    not_reported = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()  # This updates the database to match the model


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/submit_attendance", methods=["POST"])
def submit_attendance():
    try:
        # Get attendance type (house or class)
        attendance_type = request.form.get("attendance_type")
        if not attendance_type:
            return "Error: Attendance type is required.", 400

        class_or_house = None
        category = None

        if attendance_type == "house":
            house = request.form.get("house")
            category = request.form.get("category")
            if not house or not category:
                return "Error: House and Category are required for house-wise attendance.", 400
            class_or_house = house

        elif attendance_type == "class":
            class_name = request.form.get("class")
            if not class_name:
                return "Error: Class is required for class-wise attendance.", 400
            class_or_house = class_name

        # Validate numeric fields
        total = request.form.get("total")
        present = request.form.get("present")
        absent = request.form.get("absent")
        on_duty = request.form.get("onDuty")
        leave = request.form.get("leave")
        not_reported = request.form.get("notReported")

        if not all([total, present, absent, on_duty, leave, not_reported]):
            return "Error: All attendance fields are required.", 400

        # Convert to integers
        total = int(total)
        present = int(present)
        absent = int(absent)
        on_duty = int(on_duty)
        leave = int(leave)
        not_reported = int(not_reported)

        # Save to database
        attendance = Attendance(
            house_or_class=class_or_house,
            category=category or "N/A",
            total=total,
            present=present,
            absent=absent,
            on_duty=on_duty,
            leave=leave,
            not_reported=not_reported,
        )
        db.session.add(attendance)
        db.session.commit()

        return redirect(url_for("home"))

    except Exception as e:
        print(f"Error: {e}")
        return "Error: An unexpected error occurred.", 500


@app.route("/export")
def export():
    # Fetch all attendance records from the database
    records = Attendance.query.all()

    if not records:
        return "<h1>No data to export!</h1>"

    # Convert records to a Pandas DataFrame
    data = [
    {
        "House/Class": r.house_or_class,
        "Category": r.category if r.category else "N/A",
        "Total Students": r.total,
        "Present": r.present,
        "Absent": r.absent,
        "On Duty": r.on_duty,
        "Leave": r.leave,
        "Not Reported": r.not_reported,
    }
    for r in Attendance.query.all()
]

    df = pd.DataFrame(data)

    # Save the DataFrame to an Excel file
    file_path = f"attendance_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    df.to_excel(file_path, index=False)

    # Serve the file for download
    return send_file(file_path, as_attachment=True)

@app.route("/submit_report", methods=["POST"])  # Renamed this function
def submit_report():
    report_type = request.form.get("report_type")
    house_or_class = request.form.get("house_or_class")
    # You can process this data or save it to a database
    return f"You selected {report_type} for {house_or_class}!"


if __name__ == "__main__":
    app.run(debug=True, port=5001)

