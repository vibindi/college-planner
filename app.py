import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'df2bdc83df6c3edba5d094802ecc1844cedd30579009f36e'

users = {}
current_user = None

@app.route('/')
def home():
  global users
  global current_user

  print(users)
  print(current_user)
  if not current_user:
    return render_template('login.html')
  return render_template('index.html', name=users[current_user], email=current_user)

@app.route('/sign_in', methods=['POST'])
def sign_in():
  global users
  global current_user

  print(request.form)
  email = request.form['email']
  current_user = email
  if email in users:
    return redirect('/')
  users[email] = ''
  return redirect('/create_account')

@app.route('/create_account')
def create_account():
  return render_template('create_account.html')

@app.route('/sign_up', methods=['POST'])
def sign_up():
  global users
  global current_user

  users[current_user] = request.form['name']

  return redirect('/')

@app.route("/sign_out", methods=["POST"])
def sign_out():
  global users
  global current_user

  current_user = None

  return redirect('/')

@app.route("/delete_account", methods=["POST"])
def delete_account():
  global users
  global current_user

  del users[current_user]
  current_user = None

  return redirect('/')

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=3000, debug=True)