from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

from models.health_task import HealthTask
from models.message import Message
from utils.json_handler import load_json, save_json

app = Flask(__name__)

# Constants for clinician session testing
CURRENT_CLINICIAN_ID = "12340000"
CURRENT_CLINIC_ID = "clinic001"


def generate_task_id(tasks_dict):
    next_num = len(tasks_dict) + 1
    new_id = f"task{next_num:03d}"
    
    # Ensures no duplicates if tasks were deleted or custom-named
    while new_id in tasks_dict:
        next_num += 1
        new_id = f"task{next_num:03d}"
        
    return new_id

@app.route("/clinician/dashboard", methods=["GET"])
def clinician_dashboard():
    #1. Load data from JSON files
    users_data = load_json("data/users.json")
    tasks_data = load_json("data/health_tasks.json")
    submissions_data = load_json("data/task_submissions.json")
    announcements_data = load_json("data/announcements.json")

    # Get current clinician details
    clinician = users_data.get(CURRENT_CLINICIAN_ID, {})

    # Filter patients assigned to this clinic
    patients = {
        user_id: user_info
        for user_id, user_info in users_data.items()
        if user_info.get("role") == "patient" and user_info.get("clinic_id") == CURRENT_CLINIC_ID
    }

    # Filter submissions belonging to this clinic
    clinic_submissions = {
        sub_id: sub_info
        for sub_id, sub_info in submissions_data.items()
        if sub_info.get("clinic_id") == CURRENT_CLINIC_ID
    }

    # Render template and pass the filtered data
    return render_template(
        "clinician_dashboard.html",
        clinician=clinician,
        patients=patients,
        tasks=tasks_data,
        submissions=clinic_submissions,
        announcements=announcements_data
    )
@app.route("/clinician/create_task", methods=["POST"])
def create_task():
    # Extract from fields
    title = request.form.get("title")
    description = request.form.get("description")
    due_date = request.form.get("due_date")

    assigned_patient_ids = request.form.getlist("patient_ids")

    # Validate
    if not title or not description or not due_date:
        return redirect(url_for("clinician_dashboard"))

    #Load existing tasks
    tasks_data = load_json("data/health_tasks.json")

    # Generate new task ID
    new_task_id = generate_task_id(tasks_data)

    # Create new task instance
    new_task = HealthTask(
        task_id=new_task_id,
        title=title,
        description=description,
        due_date=due_date,
        clinic_id=CURRENT_CLINIC_ID,
        assigned_patient_ids=assigned_patient_ids,
        created_by=CURRENT_CLINICIAN_ID
    )

    # Add the new task to the tasks dictionary
    tasks_data[new_task_id] = new_task.to_dict()
    save_json("data/health_tasks.json", tasks_data)

    return redirect(url_for("clinician_dashboard"))

@app.route("/clinician/review/<submission_id>", methods=["POST"])
def review_submission(submission_id):
    # Load submission data
    submissions_data = load_json("data/task_submissions.json")

    # Check if submission exists
    if submission_id not in submissions_data:
        return redirect(url_for("clinician_dashboard"))

    # Extract form fields
    review_status = request.form.get("review_status")
    notes = request.form.get("notes", "")

    # Validate allowed review status values
    valid_statuses = [
        "Pending",
        "Reviewed — Normal",
        "Needs Follow-up",
        "Escalated"
    ]
    if review_status not in valid_statuses:
        return redirect(url_for("clinician_dashboard"))

    # Update submission record
    submissions_data[submission_id]["review_status"] = review_status
    submissions_data[submission_id]["notes"] = notes
    submissions_data[submission_id]["reviewer_id"] = CURRENT_CLINICIAN_ID
    submissions_data[submission_id]["review_timestamp"] = datetime.now().isoformat()

    # Save updated dictionary back to JSON
    save_json("data/task_submissions.json", submissions_data)

    # Redirect back to dashboard
    return redirect(url_for("clinician_dashboard"))