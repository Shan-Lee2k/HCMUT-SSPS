from datetime import datetime
from flask import Flask, render_template, flash, redirect, url_for, request,session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from form import RegistrationForm, LoginForm

app = Flask(__name__) #name is special variable
# Config app
app.config['SECRET_KEY'] = '80ea24d9322a81681369a178028405b8'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config["MAX_CONTENT_PATH"] = 100

# Create an instance database
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager  = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id = user_id).all()

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    documents = db.relationship('Document', backref='user', lazy=True)
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
    
    def __repr__(self):
        return f"User({self.username},{self.email})"
    
class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, filename, file_type,file_size, user_id):
        self.filename = filename
        self.file_type = file_type
        self.file_size = file_size
        self.user_id = user_id

    def __repr__(self):
        return f"Document({self.filename})"

class Printer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand_name = db.Column(db.String(20), nullable=False)
    print_model = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(20), nullable=False)

    def __init__(self, brand_name, print_model,location):
        self.brand_name = brand_name
        self.print_model = print_model
        self.location = location
    def __repr__(self):
        return f"Brand_name:({self.brand_name}), Model:({self.print_model})"
@app.route('/', methods=["GET", "POST"])
def init():
    if request.method == "POST":
        user_type = request.form.get('user_type')
        # Storing userType in the session
        session['user_type'] = user_type

        # Redirect to appropriate page based on user type
        if user_type == 'user':
            return redirect(url_for('login'))  # Redirect to user login
        elif user_type == 'spso':
            return redirect(url_for('login'))  # Redirect to SPSO login
    return render_template("init.html")
@app.route('/home')
def home():
    if "user_type" in session:
        user_type = session['user_type']

        # Redirect to appropriate page based on user type
        if user_type == 'user':
            return render_template("user_dashboard.html") 
        elif user_type == 'spso':
            return render_template("spso_dashboard.html")
# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        with app.app_context():
            user = User.query.filter_by(email = form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)    
                if "user_type" in session:
                    user_type = session.get('user_type')
                    if user_type == 'user':
                        return render_template("user_dashboard.html")  
                    elif user_type == 'spso':
                        return render_template("spso_dashboard.html")  
            else:
                flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)


@app.route('/print', methods = ['GET', 'POST'])
def print():
    if request.method == 'POST':
      f = request.files['file']
      f.save(secure_filename(f.filename))
      return 'file uploaded successfully'
    render_template('print.html')
    
# Log out
@app.route('/logout')
def logout():
    session.pop("user_type",None)
    return redirect(url_for("init"))


with app.app_context():
    db.create_all()
if __name__ == '__main__':
    app.run(debug=True)
