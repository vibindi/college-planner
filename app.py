from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'df2bdc83df6c3edba5d094802ecc1844cedd30579009f36e'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'

current_user = None

db = SQLAlchemy(app)

class Users(db.Model):
  user_id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(200), nullable=False)
  email = db.Column(db.String(200), nullable=False, index=True)
  curr_semester_id = db.Column(db.Integer, nullable=False, index=True)

class Semesters(db.Model):
  semester_id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, nullable=False, index=True)
  season = db.Column(db.String(200), nullable=False)
  year = db.Column(db.Integer, nullable=False)
  
class Courses(db.Model):
  course_id = db.Column(db.Integer, primary_key=True)
  semester_id = db.Column(db.Integer, nullable=False, index=True)
  course_prefix = db.Column(db.String(200), nullable=False)
  course_number = db.Column(db.String(200), nullable=False)
  course_name = db.Column(db.String(200), nullable=False)

class Assignments(db.Model):
  assignment_id = db.Column(db.Integer, primary_key=True)
  course_id = db.Column(db.Integer, nullable=False, index=True)
  name = db.Column(db.String(200), nullable=False)
  description = db.Column(db.String(200), nullable=False)
  due_date = db.Column(db.DateTime, nullable=False)
  is_completed = db.Column(db.Integer, nullable=False)
  completed_date = db.Column(db.DateTime, nullable=True)

class Exams(db.Model):
  exam_id = db.Column(db.Integer, primary_key=True)
  course_id = db.Column(db.Integer, nullable=False, index=True)
  name = db.Column(db.String(200), nullable=False)
  exam_date = db.Column(db.DateTime, nullable=False)
  exam_location = db.Column(db.String(200), nullable=False)

with app.app_context():
  db.create_all()
  db.session.commit()

### ROUTES ###

## UI ROUTES ##

@app.route('/')
def home():
  global current_user

  if not current_user:
    return render_template('signin.html')
  
  user = Users.query.filter_by(email=current_user).first()
  semester = Semesters.query.filter_by(semester_id=user.curr_semester_id).first()
  courses = []
  
  for c in Courses.query.filter_by(semester_id=semester.semester_id).all():
    assignments = []
    exams = []

    for a in Assignments.query.filter_by(course_id=c.course_id).all():
      if a.is_completed == 0:
        assignments.append({
          'id': a.assignment_id,
          'name': a.name,
          'description': a.description,
          'due_date': a.due_date
        })

    for e in Exams.query.filter_by(course_id=c.course_id).all():
      exams.append({
        'id': e.exam_id,
        'name': e.name,
        'exam_date': e.exam_date,
        'location': e.exam_location
      })

    courses.append({
      'id': c.course_id, 
      'prefix': c.course_prefix, 
      'number': c.course_number, 
      'name': c.course_name,
      'assignments': assignments,
      'exams': exams
    })

  return render_template('index.html', name=user.name, email=current_user, sem_name=f"{semester.season} {semester.year}", courses=courses)

@app.route('/create_account')
def create_account():
  return render_template('create_account.html')

@app.route('/settings')
def settings():
  global current_user

  user = Users.query.filter_by(email=current_user).first()
  semester = Semesters.query.filter_by(semester_id=user.curr_semester_id).first()
  all_semesters = [f"{s.season} {s.year}" for s in Semesters.query.filter_by(user_id=user.user_id).all()]
  courses = [{'id': c.course_id, 'prefix': c.course_prefix, 'number': c.course_number, 'name': c.course_name} for c in Courses.query.filter_by(semester_id=semester.semester_id).all()]

  return render_template('settings.html', sem_name=f"{semester.season} {semester.year}", all_sems=all_semesters, courses=courses)


@app.route('/report')
def report():
  global current_user

  user = Users.query.filter_by(email=current_user).first()

  semesters = []
  for s in Semesters.query.filter_by(user_id=user.user_id).all():
    courses = []
  
    for c in Courses.query.filter_by(semester_id=s.semester_id).all():
      assignments = []
      exams = []

      for a in Assignments.query.filter_by(course_id=c.course_id).all():
        if a.is_completed == 0:
          assignments.append({
            'id': a.assignment_id,
            'name': a.name,
            'description': a.description
          })

      for e in Exams.query.filter_by(course_id=c.course_id).all():
        exams.append({
          'id': e.exam_id,
          'name': e.name,
          'location': e.exam_location
        })

      courses.append({
        'id': c.course_id, 
        'prefix': c.course_prefix, 
        'number': c.course_number, 
        'name': c.course_name,
        'assignments': assignments,
        'exams': exams
      })
    
    semesters.append({
      'id': s.semester_id,
      'season': s.season,
      'year': s.year,
      'name': f"{s.season} {s.year}",
      'courses': courses
    })

  return render_template('report.html', semesters=semesters)

## FORM ROUTES ##

@app.route('/sign_in', methods=['POST'])
def sign_in():
  global current_user

  email = request.form['email']
  current_user = email
  
  # check if email is in database, if so redirect('/')
  user = Users.query.filter_by(email=email).first()

  if user:
    return redirect('/')

  return redirect('/create_account')

@app.route('/sign_up', methods=['POST'])
def sign_up():
  global current_user

  name = request.form['name']
  sem_season = request.form['semester-season']
  sem_year =  request.form['semester-year']

  # insert user
  db.session.add(Users(name=name, email=current_user, curr_semester_id=-1))
  db.session.commit()

  # get user id
  user = Users.query.filter_by(email=current_user).first()
  user_id = user.user_id

  # insert semester
  db.session.add(Semesters(user_id=user_id, season=sem_season, year=sem_year))
  db.session.commit()

  # get semester id
  semester_id = Semesters.query.filter_by(user_id=user_id, season=sem_season, year=sem_year).first().semester_id

  # update user
  user.curr_semester_id = semester_id
  db.session.commit()

  return redirect('/')

@app.route("/sign_out", methods=["POST"])
def sign_out():
  global current_user

  current_user = None

  return redirect('/')

@app.route("/delete_account", methods=["POST"])
def delete_account():
  global current_user

  # delete user and all user related info from database
  user = Users.query.filter_by(email=current_user).first()
  semesters = Semesters.query.filter_by(user_id=user.user_id).all()

  db.session.delete(user)
  for semester in semesters:
    for course in Courses.query.filter_by(semester_id=semester.semester_id).all():
      for assignment in Assignments.query.filter_by(course_id=course.course_id).all():
        db.session.delete(assignment)
      for exam in Exams.query.filter_by(course_id=course.course_id).all():
        db.session.delete(exam)
      db.session.delete(course)
    db.session.delete(semester)


  db.session.commit()

  current_user = None

  return redirect('/')

@app.route("/change-semester", methods=["POST"])
def change_semester():
  active_semester = request.form['active_semester'].split()

  user = Users.query.filter_by(email=current_user).first()
  semester = Semesters.query.filter_by(user_id=user.user_id, season=active_semester[0], year=active_semester[1]).first()
  user.curr_semester_id = semester.semester_id
  db.session.commit()
  
  return redirect('/settings')

@app.route("/add-semester", methods=["POST"])
def add_semester():
  sem_season = request.form['semester-season']
  sem_year = request.form['semester-year']

  if not Semesters.query.filter_by(season=sem_season, year=sem_year).first():
    user = Users.query.filter_by(email=current_user).first()

    db.session.add(Semesters(user_id=user.user_id, season=sem_season, year=sem_year))
    db.session.commit()

    semester = Semesters.query.filter_by(user_id=user.user_id, season=sem_season, year=sem_year).first()

    user = Users.query.filter_by(email=current_user).first()
    user.curr_semester_id = semester.semester_id
    db.session.commit()
  
  return redirect('/settings')

@app.route("/add-course", methods=['POST'])
def add_course():
  prefix = request.form['course-prefix']
  number = request.form['course-number']
  name = request.form['course-name']

  user = Users.query.filter_by(email=current_user).first()

  db.session.add(Courses(semester_id=user.curr_semester_id, course_prefix=prefix, course_number=number, course_name=name))
  db.session.commit()
  
  return redirect('/settings')

@app.route("/delete-course", methods=['POST'])
def delete_course():
  course_id = request.form['course-id']
  course = Courses.query.filter_by(course_id=course_id).first()
  for assignment in Assignments.query.filter_by(course_id=course.course_id).all():
    db.session.delete(assignment)
  for exam in Exams.query.filter_by(course_id=course.course_id).all():
    db.session.delete(exam)
  db.session.delete(course)
  db.session.commit()
  return redirect('/settings')

@app.route("/add-assignment", methods=["POST"])
def add_assignment():
  course = request.form['assignment-course']
  name = request.form['assignment-name']
  description = request.form['assignment-description']

  date = request.form['assignment-due-date'].split("T")
  day = date[0].split("-")
  time = date[1].split(":")
  due_date = datetime(int(day[0]), int(day[1]), int(day[2]), int(time[0]), int(time[1]))

  db.session.add(Assignments(course_id=course, name=name, description=description, due_date=due_date, is_completed=0))
  db.session.commit()

  return redirect('/')

@app.route("/add-exam", methods=["POST"])
def add_exam():
  course = request.form['exam-course']
  name = request.form['exam-name']
  location = request.form['exam-location']

  date = request.form['exam-date'].split("T")
  day = date[0].split("-")
  time = date[1].split(":")
  exam_date = datetime(int(day[0]), int(day[1]), int(day[2]), int(time[0]), int(time[1]))

  db.session.add(Exams(course_id=course, name=name, exam_date=exam_date, exam_location=location))
  db.session.commit()

  return redirect('/')

@app.route("/delete-assignment", methods=["POST"])
def delete_assginment():
  assignment_id = request.form['assignment-id']
  
  assignment = Assignments.query.filter_by(assignment_id=assignment_id).first()
  db.session.delete(assignment)
  db.session.commit()

  return redirect("/")

@app.route("/complete-assignment", methods=["POST"])
def complete_assignment():
  assignment_id = request.form['assignment-id']

  assignment = Assignments.query.filter_by(assignment_id=assignment_id).first()
  assignment.is_completed = 1
  assignment.completed_date = datetime.now()
  db.session.commit()

  return redirect("/")

@app.route("/delete-exam", methods=["POST"])
def delete_exam():
  exam_id = request.form['exam-id']
  
  exam = Exams.query.filter_by(exam_id=exam_id).first()
  db.session.delete(exam)
  db.session.commit()

  return redirect("/")

@app.route("/generate-report", methods=['POST'])
def generate_report():

  semester_dropdown = int(request.form['semester-dropdown'])
  course_dropdown = int(request.form['course-dropdown'])

  start_date = request.form['start-date']
  if start_date:
    start_date = start_date.split("T")
    day = start_date[0].split("-")
    start_date = datetime(int(day[0]), int(day[1]), int(day[2]))

  end_date = request.form['end-date']
  if end_date:
    end_date = end_date.split("T")
    day = end_date[0].split("-")
    end_date = datetime(int(day[0]), int(day[1]), int(day[2]))


  # catch all errors in input
  if start_date and end_date and start_date > end_date:
    return redirect('/report')

  title = ""

  if semester_dropdown == -1:
    title += "All Semesters"
  else:
    query = text(f"""
      SELECT season || " " || year
      FROM Semesters
      WHERE semester_id = {semester_dropdown}
    """)
    title += f"{db.session.execute(query).fetchone()[0]}"

  if course_dropdown == -1:
    title += ", All Courses"
  else:
    query = text(f"""
      SELECT course_prefix || " " || course_number || " (" || course_name || ")"
      FROM Courses
      WHERE course_id = {course_dropdown}
    """)
    title += f", {db.session.execute(query).fetchone()[0]}"

  if start_date and not end_date:
    title += f", On or After {start_date.strftime('%m-%d-%y')}"
  elif end_date and not start_date:
    title += f", On or Before {end_date.strftime('%m-%d-%y')}"
  elif start_date and end_date:
    if start_date == end_date:
      title += f", On {start_date.strftime('%m-%d-%y')}"
    else:
      title += f", Between {start_date.strftime('%m-%d-%y')} and {end_date.strftime('%m-%d-%y')}"

  assignment_date_condition = ""
  if start_date and end_date:
    if start_date == end_date:
      assignment_date_condition += f"a.completed_date = '{start_date}'"
    else:
      assignment_date_condition += f"a.completed_date >= '{start_date}' AND a.completed_date <= '{end_date}'"
  elif start_date and not end_date:
    assignment_date_condition += f"a.completed_date >= '{start_date}'"
  elif end_date and not start_date:
    assignment_date_condition += f"a.completed_date <= '{end_date}'"


  all_reports = []
  
  if semester_dropdown == -1 and course_dropdown == -1:
    all_reports.append(semester_num_classes())
    all_reports.append(semester_num_assignments())
    all_reports.append(semester_num_incomplete())
    all_reports.append(semester_num_complete())
    all_reports.append(semester_num_exams())

    if start_date or end_date:
      all_reports.append(semester_num_complete_date(assignment_date_condition))
  elif semester_dropdown != -1 and course_dropdown == -1:
    all_reports.append(sem_class_num_assignments(semester_dropdown))
    all_reports.append(sem_class_num_incomplete(semester_dropdown))
    all_reports.append(sem_class_num_complete(semester_dropdown))
    all_reports.append(sem_class_num_exams(semester_dropdown))
  else:
    pass

  return render_template('generated.html', title=title, all_reports=all_reports)

### QUERY FUNCTIONS ###


### ALL SEMS & ALL CLASSES

def semester_num_classes():
  report_query = text(f"""
    SELECT s.season || ' ' || s.year AS semester, count(*) AS number_of_classes
    FROM Users u
    JOIN Semesters s
    ON u.user_id = s.user_id
    JOIN Courses c
    ON c.semester_id = s.semester_id     
    WHERE u.email = "{current_user}"
    GROUP BY s.semester_id
    ;
  """)
  return execute_query(report_query)

def semester_num_assignments():
  report_query = text(f"""
    WITH valid_sems AS (SELECT s.season || ' ' || s.year AS semester, count(*) AS number_of_assignments
                        FROM Users u
                        JOIN Semesters s
                        ON u.user_id = s.user_id
                        JOIN Courses c
                        ON c.semester_id = s.semester_id
                        JOIN Assignments a
                        ON a.course_id = c.course_id     
                        WHERE u.email = "{current_user}"
                        GROUP BY s.semester_id)

    SELECT *
    FROM valid_sems

    UNION
    
    SELECT s.season || ' ' || s.year AS semester, 0 AS number_of_assignments
    FROM Users u
    JOIN Semesters s
    ON u.user_id = s.user_id
    WHERE semester NOT IN (SELECT semester FROM valid_sems)

    ;
  """)
  return execute_query(report_query)

def semester_num_incomplete():
  report_query = text(f"""
    WITH valid_sems AS (SELECT s.season || ' ' || s.year AS semester, count(*) AS number_of_incomplete_assignments
                        FROM Users u
                        JOIN Semesters s
                        ON u.user_id = s.user_id
                        JOIN Courses c
                        ON c.semester_id = s.semester_id
                        JOIN Assignments a
                        ON a.course_id = c.course_id     
                        WHERE u.email = "{current_user}" and a.is_completed = 0
                        GROUP BY s.semester_id)

    SELECT *
    FROM valid_sems

    UNION
    
    SELECT s.season || ' ' || s.year AS semester, 0 AS number_of_incomplete_assignments
    FROM Users u
    JOIN Semesters s
    ON u.user_id = s.user_id
    WHERE semester NOT IN (SELECT semester FROM valid_sems)

    ;
  """)
  return execute_query(report_query)

def semester_num_complete():
  report_query = text(f"""
    WITH valid_sems AS (SELECT s.season || ' ' || s.year AS semester, count(*) AS number_of_complete_assignments
                        FROM Users u
                        JOIN Semesters s
                        ON u.user_id = s.user_id
                        JOIN Courses c
                        ON c.semester_id = s.semester_id
                        JOIN Assignments a
                        ON a.course_id = c.course_id     
                        WHERE u.email = "{current_user}" and a.is_completed = 1
                        GROUP BY s.semester_id)

    SELECT *
    FROM valid_sems

    UNION
    
    SELECT s.season || ' ' || s.year AS semester, 0 AS number_of_complete_assignments
    FROM Users u
    JOIN Semesters s
    ON u.user_id = s.user_id
    WHERE semester NOT IN (SELECT semester FROM valid_sems)

    ;
  """)
  return execute_query(report_query)

def semester_num_exams():
  report_query = text(f"""
    WITH valid_sems AS (SELECT s.season || ' ' || s.year AS semester, count(*) AS number_of_exams
                        FROM Users u
                        JOIN Semesters s
                        ON u.user_id = s.user_id
                        JOIN Courses c
                        ON c.semester_id = s.semester_id
                        JOIN Exams e
                        ON e.course_id = c.course_id     
                        WHERE u.email = "{current_user}"
                        GROUP BY s.semester_id)

    SELECT *
    FROM valid_sems

    UNION
    
    SELECT s.season || ' ' || s.year AS semester, 0 AS number_of_exams
    FROM Users u
    JOIN Semesters s
    ON u.user_id = s.user_id
    WHERE semester NOT IN (SELECT semester FROM valid_sems)

    ;
  """)
  return execute_query(report_query)

def semester_num_complete_date(date_condition):
  report_query = text(f"""
    WITH valid_sems AS (SELECT s.season || ' ' || s.year AS semester, count(*) AS number_of_complete_assignments_in_date_range
                        FROM Users u
                        JOIN Semesters s
                        ON u.user_id = s.user_id
                        JOIN Courses c
                        ON c.semester_id = s.semester_id
                        JOIN Assignments a
                        ON a.course_id = c.course_id     
                        WHERE u.email = "{current_user}" and a.is_completed = 1 and {date_condition}
                        GROUP BY s.semester_id)

    SELECT *
    FROM valid_sems

    UNION
    
    SELECT s.season || ' ' || s.year AS semester, 0 AS number_of_complete_assignments_in_date_range
    FROM Users u
    JOIN Semesters s
    ON u.user_id = s.user_id
    WHERE semester NOT IN (SELECT semester FROM valid_sems)

    ;
  """)
  return execute_query(report_query)

### SEM & ALL CLASSES
def sem_class_num_assignments(sem):
  report_query = text(f"""
    WITH valid_sems AS (SELECT c.course_prefix || ' ' || c.course_number AS course, count(*) AS number_of_assignments
                        FROM Users u
                        JOIN Semesters s
                        ON u.user_id = s.user_id
                        JOIN Courses c
                        ON c.semester_id = s.semester_id
                        JOIN Assignments a
                        ON a.course_id = c.course_id     
                        WHERE u.email = "{current_user}" and s.semester_id = {sem}
                        GROUP BY c.course_id)

    SELECT *
    FROM valid_sems

    UNION
    
    SELECT c.course_prefix || ' ' || c.course_number AS course, 0 AS number_of_assignments
    FROM Users u
    JOIN Semesters s
    ON u.user_id = s.user_id
    JOIN Courses c
    ON c.semester_id = s.semester_id
    WHERE course NOT IN (SELECT course FROM valid_sems) and s.semester_id = {sem}

    ;
  """)
  return execute_query(report_query)

def sem_class_num_incomplete(sem):
  report_query = text(f"""
    WITH valid_sems AS (SELECT c.course_prefix || ' ' || c.course_number AS course, count(*) AS number_of_incomplete_assignments
                        FROM Users u
                        JOIN Semesters s
                        ON u.user_id = s.user_id
                        JOIN Courses c
                        ON c.semester_id = s.semester_id
                        JOIN Assignments a
                        ON a.course_id = c.course_id     
                        WHERE u.email = "{current_user}" and a.is_completed = 0 and s.semester_id = {sem}
                        GROUP BY s.semester_id)

    SELECT *
    FROM valid_sems

    UNION
    
    SELECT c.course_prefix || ' ' || c.course_number AS course, 0 AS number_of_incomplete_assignments
    FROM Users u
    JOIN Semesters s
    ON u.user_id = s.user_id
    JOIN Courses c
    ON c.semester_id = s.semester_id
    WHERE course NOT IN (SELECT course FROM valid_sems) and s.semester_id = {sem}

    ;
  """)
  return execute_query(report_query)

def sem_class_num_complete(sem):
  report_query = text(f"""
    WITH valid_sems AS (SELECT c.course_prefix || ' ' || c.course_number AS course, count(*) AS number_of_complete_assignments
                        FROM Users u
                        JOIN Semesters s
                        ON u.user_id = s.user_id
                        JOIN Courses c
                        ON c.semester_id = s.semester_id
                        JOIN Assignments a
                        ON a.course_id = c.course_id     
                        WHERE u.email = "{current_user}" and a.is_completed = 1 and s.semester_id = {sem}
                        GROUP BY s.semester_id)

    SELECT *
    FROM valid_sems

    UNION
    
    SELECT c.course_prefix || ' ' || c.course_number AS course, 0 AS number_of_complete_assignments
    FROM Users u
    JOIN Semesters s
    ON u.user_id = s.user_id
    JOIN Courses c
    ON c.semester_id = s.semester_id
    WHERE course NOT IN (SELECT course FROM valid_sems) and s.semester_id = {sem}

    ;
  """)
  return execute_query(report_query)

def sem_class_num_exams(sem):
  report_query = text(f"""
    WITH valid_sems AS (SELECT c.course_prefix || ' ' || c.course_number AS course, count(*) AS number_of_exams
                        FROM Users u
                        JOIN Semesters s
                        ON u.user_id = s.user_id
                        JOIN Courses c
                        ON c.semester_id = s.semester_id
                        JOIN Exams e
                        ON e.course_id = c.course_id     
                        WHERE u.email = "{current_user}" and s.semester_id = {sem}
                        GROUP BY s.semester_id)

    SELECT *
    FROM valid_sems

    UNION
    
    SELECT c.course_prefix || ' ' || c.course_number AS course, 0 AS number_of_exams
    FROM Users u
    JOIN Semesters s
    ON u.user_id = s.user_id
    JOIN Courses c
    ON c.semester_id = s.semester_id
    WHERE course NOT IN (SELECT course FROM valid_sems) and s.semester_id = {sem}

    ;
  """)
  return execute_query(report_query)


### SEM & CLASS

def execute_query(query):
  return db.session.execute(query).mappings().all()

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=3000, debug=True)