from flask import Flask, request, redirect

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <form method="POST" action="/submit_attendance">
        <h3>Select Attendance Type:</h3>
        <label for="attendance_type">Attendance Type:</label>
        <select name="attendance_type" id="attendance_type" required>
            <option value="">--Select--</option>
            <option value="house">House-wise Attendance</option>
            <option value="class">Class-wise Attendance</option>
        </select>
        <button type="submit">Submit</button>
    </form>
    """

@app.route("/submit_attendance", methods=["POST"])
def submit_attendance():
    attendance_type = request.form.get("attendance_type")
    if attendance_type == "house":
        return redirect("http://127.0.0.1:5002")  # Redirect to house-wise app
    elif attendance_type == "class":
        return redirect("http://127.0.0.1:5001")  # Redirect to class-wise app
    else:
        return "Invalid attendance type", 400

if __name__ == "__main__":
    app.run(port=5050)
