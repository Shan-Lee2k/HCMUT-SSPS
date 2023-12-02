from datetime import datetime
from flask import Flask, render_template, flash, redirect, url_for, request,session
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
        flash("You have been logged in", 'success')
        if "user_type" in session:
            user_type = session.get('user_type')
            if user_type == 'user':
                return render_template("user_dashboard.html")  
            elif user_type == 'spso':
                return render_template("spso_dashboard.html")  
    else:
        #flash("Login unsuccessfully! Please check email and password again!")
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
    return render_template("init.html")


if __name__ == '__main__':
    app.run(debug=True)
