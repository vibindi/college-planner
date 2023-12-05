from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, url_for, flash, redirect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'df2bdc83df6c3edba5d094802ecc1844cedd30579009f36e'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'

current_user = None

db = SQLAlchemy(app)

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

with app.app_context():
  db.create_all()
  db.session.commit()

  #print(Users.query.all())

### ROUTES ###

@app.route('/')
def home():
  global current_user

  if not current_user:
    return render_template('signin.html')
  
  user = Users.query.filter_by(email=current_user).first()
  return render_template('index.html', name=user.name, email=current_user)

@app.route('/sign_in', methods=['POST'])
def sign_in():
  global current_user

  email = request.form['email']
  current_user = email
  
  # check if email is in database, if so redirect('/')
  user = Users.query.filter_by(email=email).first()
  print(user)

  if user:
    return redirect('/')

  return redirect('/create_account')

@app.route('/create_account')
def create_account():
  return render_template('create_account.html')

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
  db.session.delete(user)
  db.session.commit()

  current_user = None

  return redirect('/')


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=3000, debug=True)