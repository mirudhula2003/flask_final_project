from flask import Flask, render_template, request, redirect, url_for, flash, session
import matplotlib.pyplot as plt
plt.switch_backend('Agg')
import pandas as pd
import os
from functools import wraps
import seaborn as sns
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:rootroot@localhost/realestate_house_db'
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(10), nullable=False)

class RealEstate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    area_type = db.Column(db.String(100), nullable=False)
    availability = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    size = db.Column(db.String(50), nullable=False)
    society = db.Column(db.String(200), nullable=True)
    total_sqft = db.Column(db.Float, nullable=False)
    bath = db.Column(db.Integer, nullable=False)
    balcony = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

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

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            return 'Access denied: Admins only', 403
        return f(*args, **kwargs)
    return decorated_function

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

@app.route('/dashboard_action', methods=['POST'])
def dashboard_action():
    action = request.form['action']
    if action == 'add':
        return redirect(url_for('add_house'))
    elif action == 'delete':
        return redirect(url_for('delete_house'))
    elif action == 'update':
        return redirect(url_for('update_house'))
    elif action == 'view':
        return redirect(url_for('view_house'))
    elif action == 'charts':
        return redirect(url_for('view_charts'))
    else:
        return 'Invalid action selected!', 400

@app.route('/delete_house', methods=['GET', 'POST'])
@admin_required
def delete_house():
    if request.method == 'POST':
        house_id = request.form['house_id']
        house = RealEstate.query.filter_by(id=house_id).first()
        if not house:
            flash(f"No house found with ID {house_id}", "error")
            return redirect(url_for('delete_house'))
        db.session.delete(house)
        db.session.commit()
        flash(f"House with ID {house_id} has been deleted.", "success")
        return redirect(url_for('dashboard'))
    return render_template('delete_house.html')

@app.route('/update_house', methods=['GET', 'POST'])
@admin_required
def update_house():
    if request.method == 'POST':
        house_id = request.form['house_id']
        house = RealEstate.query.filter_by(id=house_id).first()
        if not house:
            flash(f"No house found with ID {house_id}", "error")
            return redirect(url_for('update_house'))
        house.area_type = request.form.get('area_type', RealEstate.area_type)
        house.availability = request.form.get('availability', RealEstate.availability)
        house.location = request.form.get('location', RealEstate.location)
        house.size = request.form.get('size', RealEstate.size)
        house.society = request.form.get('society', RealEstate.society)
        house.total_sqft = request.form.get('total_sqft', RealEstate.total_sqft)
        house.bath = request.form.get('bath', RealEstate.bath)
        house.balcony = request.form.get('balcony', RealEstate.balcony)
        house.price = request.form.get('price', RealEstate.price)
        db.session.commit()
        flash(f"House with ID {house_id} has been updated.", "success")
        return redirect(url_for('dashboard'))
    return render_template('update_house.html')

@app.route('/add_house', methods=['GET', 'POST'])
@admin_required
def add_house():
    if request.method == 'POST':
        area_type = request.form['area_type']
        availability = request.form['availability']
        location = request.form['location']
        size = request.form['size']
        society = request.form['society']
        total_sqft = request.form['total_sqft']
        bath = request.form['bath']
        balcony = request.form['balcony']
        price = request.form['price']
        new_house = RealEstate(
            area_type=area_type,
            availability=availability,
            location=location,
            size=size,
            society=society,
            total_sqft=total_sqft,
            bath=bath,
            balcony=balcony,
            price=price
        )
        db.session.add(new_house)
        db.session.commit()
        flash(f"House successfully added! Details: Area Type={area_type}, Availability={availability}, "
              f"Location={location}, Size={size}, Society={society}, Total Sqft={total_sqft}, "
              f"Baths={bath}, Balconies={balcony}, Price={price}")
        return redirect(url_for('dashboard'))
    return render_template('add_house.html')

@app.route('/view_house', methods=['GET', 'POST'])
def view_house():
    house = None
    if request.method == 'POST':
        house_id = request.form['house_id']
        house = RealEstate.query.filter_by(id=house_id).first()
        if not house:
            flash("No house found with the given ID.")
    return render_template('view_house.html', house=house)

def generate_histogram(data, title, xlabel, ylabel, file_path):
    plt.figure(figsize=(8, 6))
    plt.hist(data, bins=10, color='skyblue', edgecolor='black')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.savefig(file_path)
    plt.close()
    return file_path

def generate_heatmap(total_sqft, bath, price, availability, file_path):
    data = {
        'Total Sqft': total_sqft,
        'Bathrooms': bath,
        'Price': price,
        'Availability': availability
    }
    df = pd.DataFrame(data)
    correlation_matrix = df.corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
    plt.title('Correlation Heatmap')
    plt.savefig(file_path)
    plt.close()
    return file_path

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

def generate_pie_chart(data, title, file_path):
    unique_data = list(set(data))
    counts = [data.count(x) for x in unique_data]
    plt.figure(figsize=(8, 8))
    plt.pie(counts, labels=unique_data, autopct='%1.1f%%', startangle=140, colors=sns.color_palette('Set3', len(unique_data)))
    plt.title(title)
    plt.savefig(file_path)
    plt.close()
    return file_path

def generate_line_graph(total_sqft, price, file_path):
    plt.figure(figsize=(10, 6))
    plt.plot(total_sqft, price, marker='o', color='blue')
    plt.title('Total Sqft vs Price')
    plt.xlabel('Total Sqft')
    plt.ylabel('Price')
    plt.grid(True)
    plt.savefig(file_path)
    plt.close()
    return file_path

@app.route('/view_charts')
def view_charts():
    realestate = RealEstate.query.all()
    total_sqft = [property.total_sqft for property in realestate]
    bath = [property.bath for property in realestate]
    price = [property.price for property in realestate]
    availability = [property.availability for property in realestate]
    societies = [property.society for property in realestate]
    charts_dir = 'static/charts'
    os.makedirs(charts_dir, exist_ok=True)
    chart_files = []
    chart_files.append(generate_histogram(total_sqft, 'Total Sqft Distribution', 'Total Sqft', 'Frequency', os.path.join(charts_dir, 'total_sqft_distribution.png')))
    chart_files.append(generate_histogram(price, 'Price Distribution', 'Price', 'Frequency', os.path.join(charts_dir, 'price_distribution.png')))
    chart_files.append(generate_heatmap(total_sqft, bath, price, availability, os.path.join(charts_dir, 'heatmap.png')))
    chart_files.append(generate_bar_chart(societies, 'Society Distribution', 'Society', 'Count', os.path.join(charts_dir, 'society_distribution.png')))
    chart_files.append(generate_pie_chart(availability, 'Availability Pie Chart', os.path.join(charts_dir, 'availability_pie_chart.png')))
    chart_files.append(generate_line_graph(total_sqft, price, os.path.join(charts_dir, 'total_sqft_vs_price.png')))
    return render_template('view_charts.html', chart_files=[url_for('static', filename=f'charts/{os.path.basename(f)}') for f in chart_files])

if __name__ == "__main__":
    app.run(debug=True)
