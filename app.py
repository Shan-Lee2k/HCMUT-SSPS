from datetime import datetime
from flask import Flask, render_template, flash, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from form import RegistrationForm, LoginForm

app = Flask(__name__) #name is special variable
# Config app
app.config['SECRET_KEY'] = '80ea24d9322a81681369a178028405b8'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config["MAX_CONTENT_PATH"] = 100

# Create an instance database
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    
    def __repr__(self):
        return f"User({self.username},{self.email}, {self.image_file})"
    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

posts = [
    {
        'author' : 'Shan',
        'title' : "How to read?",
        'price' : 21
    },
    {
        'author' : 'Shan',
        'title' : "How to sing",
        'price' : 50
    }
]
@app.route('/')
def home():
    return render_template("hello.html", posts = posts)

current_stage = 'print_document'  # Initial stage
@app.route('/print', methods=['GET', 'POST'])
def print_document():
    global current_stage

    if request.method == 'POST':
        if current_stage == 'print_document':
            uploaded_file = request.files['file']
            if uploaded_file:
                # Process the file (example: save it to a folder)
                uploaded_file.save(uploaded_file.filename)

                # Move to the next stage
                current_stage = 'upload_success'

                # Redirect to the same route to render the updated stage
                return redirect(url_for('print_document'))

    return render_template('print.html', current_stage=current_stage)
def upload():
    # Make sure to save the uploaded file to the desired location

    #  saving the file to the "uploads" folder
    uploaded_file = request.files['file']
    uploaded_file.save('uploads/' + uploaded_file.filename)

    # Redirect to the next stage or page
    return redirect(url_for('next_stage'))  # Update 'next_stage' to your actual next stage route

@app.route('/printer_selection', methods=['GET', 'POST'])
def printer_selection():
    if request.method == 'POST':
        selected_printer = request.form.get('printer')
        # Add your logic here based on the selected printer

        # Move to the next stage
        global current_stage
        current_stage = 'printing'  # Update to 'printing' or your next stage
        return render_template('print.html', current_stage=current_stage)

    return render_template('print.html', current_stage='printer_selection')

@app.route('/move_to_printer_selection', methods=['GET'])
def move_to_printer_selection():
    
    # Move to the printer_selection stage
    global current_stage
    current_stage = 'printer_selection'  # Update to your actual next stage

    # Redirect to the printer_selection route
    return redirect(url_for('printer_selection'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f"Account created for {form.username.data}", 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title = 'Register', form = form)
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash("You have been logged in", 'success')
        return redirect(url_for('home'))
    else:
        flash("Login unsuccessfully! Please check email and password again!")
    return render_template('login.html', title = 'Login', form = form)

if __name__ == '__main__':
    app.run(debug=True)
