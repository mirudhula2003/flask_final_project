from flask import Flask, render_template, request, redirect, url_for, flash, send_file,session,g
import matplotlib.pyplot as plt
plt.switch_backend('Agg') 
import pandas as pd
import io
import base64
from flask_sqlalchemy import SQLAlchemy
import os
from functools import wraps
import seaborn as sns
import pandas as pd
from flask_migrate import Migrate
# from flask_script import Manager
import subprocess

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///roles.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:rootroot@localhost/studentdb'
app.config['SECRET_KEY'] = os.urandom(24)  
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Define a User model with roles
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # "user" or "admin"

class Students(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(100), unique=True, nullable=False)
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    study_hours_per_week = db.Column(db.Float)
    attendance_rate = db.Column(db.Float)
    gpa = db.Column(db.Float)
    major = db.Column(db.String(100))
    part_time_job = db.Column(db.String(50))
    extra_curricular_activities = db.Column(db.String(255))



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid credentials!'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Admin role required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            return 'Access denied: Admins only', 403
        return f(*args, **kwargs)
    return decorated_function

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function






@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# New action handler
@app.route('/dashboard_action', methods=['POST'])
def dashboard_action():
    action = request.form['action']
    
    if action == 'add':
        return redirect(url_for('add_student'))
    elif action == 'delete':
        return redirect(url_for('delete_student'))
    elif action == 'update':
        return redirect(url_for('update_student'))
    elif action == 'view':
        return redirect(url_for('view_student'))
    elif action == 'charts':
        return redirect(url_for('view_charts'))
    else:
        return 'Invalid action selected!', 400
    

@app.route('/delete_student', methods=['GET', 'POST'])
# @login_required
@admin_required  # Ensure only admins can access this route
def delete_student():
    if request.method == 'POST':
        # Get the student_id from the form input
        student_id = request.form['student_id']
        
        # Query the student by student_id
        student = Students.query.filter_by(student_id=student_id).first()

        # If the student doesn't exist, show an error message
        if not student:
            flash(f"No student found with ID {student_id}", "error")
            return redirect(url_for('delete_student'))

        # Delete the student record from the database
        db.session.delete(student)
        db.session.commit()

        # Show a success message
        flash(f"Student with ID {student_id} has been deleted.", "success")
        return redirect(url_for('dashboard'))

    return render_template('delete_student.html')

@app.route('/update_student', methods=['GET', 'POST'])
@admin_required  # Ensure only admins can access this route
def update_student():
    if request.method == 'POST':
        # Get the student_id to search for the student
        student_id = request.form['student_id']
        
        # Fetch the student by student_id from the database
        student = Students.query.filter_by(student_id=student_id).first()

        # If student doesn't exist, show an error message
        if not student:
            flash(f"No student found with ID {student_id}", "error")
            return redirect(url_for('update_student'))

        # Update the student fields with the new data if provided
        student.gender = request.form.get('gender', student.gender)
        student.age = request.form.get('age', student.age)
        student.study_hours_per_week = request.form.get('study_hours_per_week', student.study_hours_per_week)
        student.attendance_rate = request.form.get('attendance_rate', student.attendance_rate)
        student.gpa = request.form.get('gpa', student.gpa)
        student.major = request.form.get('major', student.major)
        student.part_time_job = request.form.get('part_time_job', student.part_time_job)
        student.extra_curricular_activities = request.form.get('extra_curricular_activities', student.extra_curricular_activities)
        
        # Commit the changes to the database
        db.session.commit()

        # Show a success message
        flash(f"Student with ID {student_id} has been updated.", "success")
        return redirect(url_for('dashboard'))
    
    return render_template('update_student.html')

@app.route('/add_student', methods=['GET', 'POST'])
@admin_required  # Ensure only admins can access this route
def add_student():
    if request.method == 'POST':
        # Capture data from the form
        student_id = request.form['student_id']
        gender = request.form['gender']
        age = request.form['age']
        study_hours_per_week = request.form['study_hours_per_week']
        attendance_rate = request.form['attendance_rate']
        gpa = request.form['gpa']
        major = request.form['major']
        part_time_job = request.form['part_time_job']
        extra_curricular_activities = request.form['extra_curricular_activities']

        # Create a new Student object
        new_student = Students(
            student_id=student_id,
            gender=gender,
            age=age,
            study_hours_per_week=study_hours_per_week,
            attendance_rate=attendance_rate,
            gpa=gpa,
            major=major,
            part_time_job=part_time_job,
            extra_curricular_activities=extra_curricular_activities
        )

        # Add the student to the database
        db.session.add(new_student)
        db.session.commit()
        flash(f"Student successfully added! Details: ID={student_id}, Gender={gender}, Age={age}, "
              f"Study Hours/Week={study_hours_per_week}, Attendance Rate={attendance_rate}, GPA={gpa}, "
              f"Major={major}, Part-Time Job={part_time_job}, Extra-Curricular Activities={extra_curricular_activities}")
        
        # Redirect to the admin dashboard
        return redirect(url_for('dashboard'))
    
    return render_template('add_student.html')

@app.route('/view_student', methods=['GET', 'POST'])
def view_student():
    student = None  # Initialize student as None
    
    if request.method == 'POST':
        student_id = request.form['student_id']

        # Query the Students model to find the student by ID
        student = Students.query.filter_by(student_id=student_id).first()

        if not student:
            # If no student is found, flash a message
            flash("No student found with the given ID.")
    
    return render_template('view_student.html', student=student)
def generate_histogram(data, title, xlabel, ylabel, file_path):
    plt.figure(figsize=(8, 6))
    plt.hist(data, bins=10, color='skyblue', edgecolor='black')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.savefig(file_path)
    plt.close()
    return file_path

# Function to generate a heatmap
def generate_heatmap(ages, study_hours, attendance_rates, gpas, file_path):
    data = {
        'Age': ages,
        'Study Hours per Week': study_hours,
        'Attendance Rate': attendance_rates,
        'GPA': gpas
    }
    df = pd.DataFrame(data)
    correlation_matrix = df.corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
    plt.title('Correlation Heatmap')
    plt.savefig(file_path)
    plt.close()
    return file_path

# Function to generate a bar chart
def generate_bar_chart(data, title, xlabel, ylabel, file_path):
    unique_data = list(set(data))
    counts = [data.count(x) for x in unique_data]
    plt.figure(figsize=(10, 6))
    plt.bar(unique_data, counts, color='lightcoral')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45)
    plt.savefig(file_path)
    plt.close()
    return file_path

# Function to generate a pie chart
def generate_pie_chart(data, title, file_path):
    unique_data = list(set(data))
    counts = [data.count(x) for x in unique_data]
    plt.figure(figsize=(8, 8))
    plt.pie(counts, labels=unique_data, autopct='%1.1f%%', startangle=140, colors=sns.color_palette('Set3', len(unique_data)))
    plt.title(title)
    plt.savefig(file_path)
    plt.close()
    return file_path

# Function to generate a line graph
def generate_line_graph(ages, study_hours, file_path):
    plt.figure(figsize=(10, 6))
    plt.plot(ages, study_hours, marker='o', color='blue')
    plt.title('Age vs Study Hours per Week')
    plt.xlabel('Age')
    plt.ylabel('Study Hours per Week')
    plt.grid(True)
    plt.savefig(file_path)
    plt.close()
    return file_path

@app.route('/view_charts')
def view_charts():
    # Query data from the database
    students = Students.query.all()

    # Prepare data for charts
    ages = [student.age for student in students]
    gpas = [student.gpa for student in students]
    attendance_rates = [student.attendance_rate for student in students]
    study_hours = [student.study_hours_per_week for student in students]
    majors = [student.major for student in students]

    # Ensure charts directory exists
    charts_dir = 'static/charts'
    os.makedirs(charts_dir, exist_ok=True)

    # Generate charts
    chart_files = []
    
    # Histogram for Age Distribution
    chart_files.append(generate_histogram(ages, 'Age Distribution', 'Age', 'Frequency', os.path.join(charts_dir, 'age_distribution.png')))
    
    # Histogram for GPA Distribution
    chart_files.append(generate_histogram(gpas, 'GPA Distribution', 'GPA', 'Frequency', os.path.join(charts_dir, 'gpa_distribution.png')))
    
    # Heatmap for Correlation
    chart_files.append(generate_heatmap(ages, study_hours, attendance_rates, gpas, os.path.join(charts_dir, 'heatmap.png')))
    
    # Bar chart for Major Distribution
    chart_files.append(generate_bar_chart(majors, 'Major Distribution', 'Major', 'Count', os.path.join(charts_dir, 'major_distribution.png')))
    
    # Pie chart for Major Distribution
    chart_files.append(generate_pie_chart(majors, 'Major Distribution Pie Chart', os.path.join(charts_dir, 'major_pie_chart.png')))
    
    # Line graph for Age vs Study Hours
    chart_files.append(generate_line_graph(ages, study_hours, os.path.join(charts_dir, 'age_vs_study_hours.png')))

    return render_template('view_charts.html', chart_files=[url_for('static', filename=f'charts/{os.path.basename(f)}') for f in chart_files])
if __name__ == '__main__':
    app.run(debug=True)
