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
        
        'title' : "Chào mừng bạn đến dịch vụ in ấn thông minh tại Trường Đại học Bách Khoa - ĐHQG HCM",
    
    },
]
   
@app.route('/')
def home():
    return render_template("hello.html", posts = posts)
@app.route('/print', methods = ['GET', 'POST'])
def print():
    if request.method == 'POST':
      f = request.files['file']
      f.save(secure_filename(f.filename))
      return 'file uploaded successfully'
    render_template('print.html')

@app.route('/account', methods = ['GET', 'POST'])
def account():

    render_template('account.html')

@app.route('/payment', methods = ['GET', 'POST'])
def payment():

    render_template('payment.html')

@app.route('/history', methods = ['GET', 'POST'])
def history():

    render_template('history.html')

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
