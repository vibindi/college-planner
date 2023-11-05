drop table if exists users;
drop table if exists semesters;
drop table if exists courses;
drop table if exists assignments;
drop table if exists exams;

create table users (
  user_id integer primary key autoincrement,
  name text not null,
  email text not null,
  curr_semester_id integer not null
);

create table semesters (
  semester_id integer primary key autoincrement,
  user_id integer not null,
  season text not null,
  year integer not null,
  start_date text not null,
  end_date text not null,
  foreign key(user_id) references users(user_id)
);

create table courses (
  course_id integer primary key autoincrement,
  user_id integer not null,
  semester_id integer not null,
  course_prefix text not null,
  course_number text not null,
  course_name text not null,
  num_credits integer not null,
  foreign key(user_id) references users(user_id),
  foreign key(semester_id) references semesters(semester_id)
);

create table assignments (
  assignment_id integer primary key autoincrement,
  user_id integer not null,
  course_id integer not null,
  name text not null,
  description text not null,
  due_date text not null,
  is_completed integer not null,
  completed_date text not null,
  foreign key(user_id) references users(user_id),
  foreign key(course_id) references courses(course_id)
);

create table exams (
  exam_id integer primary key autoincrement,
  user_id integer not null,
  course_id integer not null,
  name text not null,
  exam_date text not null,
  exam_location text not null,
  foreign key(user_id) references users(user_id),
  foreign key(course_id) references courses(course_id)
);