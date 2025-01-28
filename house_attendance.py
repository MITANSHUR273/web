from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from datetime import datetime


# Initialize Flask app
app = Flask(__name__)

# Configure SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///attendance.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Define the Attendance model
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    house_or_class = db.Column(db.String(100), nullable=False)  # House or Class
    category = db.Column(db.String(50), nullable=True)  # Category (for house-wise)
    total = db.Column(db.Integer, nullable=False)
    present = db.Column(db.Integer, nullable=False)
    absent = db.Column(db.Integer, nullable=False)
    on_duty = db.Column(db.Integer, nullable=False)
    leave = db.Column(db.Integer, nullable=False)
    not_reported = db.Column(db.Integer, nullable=False)

# Create database tables
with app.app_context():
    db.create_all()

# Home route
@app.route("/")
def home():
    return render_template("index.html")

# Submit attendance route
@app.route("/submit_attendance", methods=["POST"])
def submit_attendance():
    try:
        # Get attendance type (house or class)
        attendance_type = request.form.get("attendance_type")
        if not attendance_type:
            return "Attendance type is required", 400

        house_or_class = None
        category = None

        if attendance_type == "house":
            # Handle house-wise attendance
            house = request.form.get("house")
            category = request.form.get("category")
            if not house or not category:
                return "House and Category are required for house-wise attendance", 400
            house_or_class = house

        elif attendance_type == "class":
            # Handle class-wise attendance
            class_name = request.form.get("class")
            if not class_name:
                return "Class is required for class-wise attendance", 400
            house_or_class = class_name

        # Validate numeric fields
        total = int(request.form.get("total", 0))
        present = int(request.form.get("present", 0))
        absent = int(request.form.get("absent", 0))
        on_duty = int(request.form.get("onDuty", 0))
        leave = int(request.form.get("leave", 0))
        not_reported = int(request.form.get("notReported", 0))

        # Ensure valid numbers
        if total <= 0 or any(x < 0 for x in [present, absent, on_duty, leave, not_reported]):
            return "Invalid attendance numbers", 400

        # Save to the database
        attendance = Attendance(
            house_or_class=house_or_class,
            category=category or "N/A",  # Default to "N/A" for class-wise attendance
            total=total,
            present=present,
            absent=absent,
            on_duty=on_duty,
            leave=leave,
            not_reported=not_reported
        )
        db.session.add(attendance)
        db.session.commit()

        return redirect(url_for("home"))

    except Exception as e:
        db.session.rollback()
        return f"An error occurred: {str(e)}", 500

# Export to Excel route
@app.route("/export")
def export():
    # Fetch all attendance records
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
        for r in records
    ]

    df = pd.DataFrame(data)

    # Save DataFrame to an Excel file
    file_path = f"attendance_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    df.to_excel(file_path, index=False)

    # Serve the file for download
    return send_file(file_path, as_attachment=True)

# Run Flask app
if __name__ == "__main__":
    app.run(debug=True, port=5002)
