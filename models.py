from app import db

class Users(db.Model):
  user_id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(200), nullable=False)
  email = db.Column(db.String(200), nullable=False)
  curr_semester_id = db.Column(db.Integer, nullable=False)

class Semesters(db.Model):
  semester_id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, nullable=False)
  season = db.Column(db.String(200), nullable=False)
  year = db.Column(db.Integer, nullable=False)
  

class Courses(db.Model):
  course_id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, nullable=False)
  semester_id = db.Column(db.Integer, nullable=False)
  course_prefix = db.Column(db.String(200), nullable=False)
  course_number = db.Column(db.String(200), nullable=False)
  course_name = db.Column(db.String(200), nullable=False)
  num_credits = db.Column(db.Integer, nullable=False)

class Assignments(db.Model):
  assignment_id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, nullable=False)
  course_id = db.Column(db.Integer, nullable=False)
  name = db.Column(db.String(200), nullable=False)
  description = db.Column(db.String(200), nullable=False)
  due_date = db.Column(db.DateTime, nullable=False)
  is_completed = db.Column(db.Integer, nullable=False)
  completed_date = db.Column(db.DateTime, nullable=False)

class Exams(db.Model):
  exam_id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, nullable=False)
  course_id = db.Column(db.Integer, nullable=False)
  name = db.Column(db.String(200), nullable=False)
  exam_date = db.Column(db.DateTime, nullable=False)
  exam_location = db.Column(db.String(200), nullable=False)