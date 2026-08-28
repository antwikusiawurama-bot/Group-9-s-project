from datetime import datetime
class HealthTask:
    def __init__(self, task_id, title, description, due_date, clinic_id, assigned_patient_ids, created_by):
        self.task_id = task_id
        self.task_name = title
        self.task_description = description
        self.due_date = due_date
        self.clinic_id = clinic_id
        self.assigned_patient_ids = assigned_patient_ids
        self.created_by = created_by
        self.created_at = datetime.now().isoformat()

def to_dict(self):
    return {
        "task_id": self.task_id,
        "task_name": self.task_name,
        "task_description": self.task_description,
        "due_date": self.due_date,
        "clinic_id": self.clinic_id,
        "assigned_patient_ids": self.assigned_patient_ids,
        "created_by": self.created_by,
        "created_at": self.created_at
    }