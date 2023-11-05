import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'df2bdc83df6c3edba5d094802ecc1844cedd30579009f36e'

current_user = None

### ROUTES ###

@app.route('/')
def home():
  global current_user

  if not current_user:
    return render_template('signin.html')
  return render_template('index.html', name=current_user, email=current_user)

@app.route('/sign_in', methods=['POST'])
def sign_in():
  global current_user

  email = request.form['email']
  current_user = email
  
  # check if email is in database, if so redirect('/')
  conn = db_conn()
  users = conn.execute(f'select * from users where email = "{email}"').fetchall()
  conn.close()

  if users:
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

  conn = db_conn()

  # insert user
  conn.execute(f'insert into users (name, email, curr_semester_id) values (?, ?, ?)', (name, current_user, -1))
  conn.commit()

  # get user id
  user_id = conn.execute(f'select user_id from users where email = "{current_user}"').fetchall()[0]['user_id']
  conn.commit()

  # insert semester
  conn.execute(f'insert into semesters (user_id, season, year) values (?, ?, ?)', (user_id, sem_season, sem_year))
  conn.commit()

  # get semester id
  semester_id = conn.execute(f'select semester_id from semesters where user_id = "{user_id}" and season = "{sem_season}" and year = "{sem_year}"').fetchall()[0]['semester_id']
  conn.commit()

  # update user
  conn.execute(f'update users set curr_semester_id = "{semester_id}" where user_id = "{user_id}"')
  conn.commit()
  
  conn.close()

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
  conn = db_conn()
  conn.execute(f'delete from users where email = "{current_user}"')
  conn.commit()
  conn.close()

  current_user = None

  return redirect('/')


### DB CONNECTIONS ###

def db_conn():
    conn = sqlite3.connect('college-planner.db')
    conn.row_factory = sqlite3.Row
    return conn


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=3000, debug=True)