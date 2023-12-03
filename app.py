from flask import Flask, render_template, flash, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from form import RegistrationForm, LoginForm
from datetime import datetime, timezone  # Import timezone from datetime module
import PyPDF2
from docx import Document
from flask import abort  # Import the abort function
from flask import send_file
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '80ea24d9322a81681369a178028405b8'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config["MAX_CONTENT_PATH"] = 100

db = SQLAlchemy(app)

# Define current_stage globally
current_stage = 'print_document'
# Define stage_history as a global variable
stage_history = []
# Initialize uploaded_file globally
uploaded_file = None
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
    return render_template("hello.html", posts=posts)

# Define the function to check if the file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file):
    file_path = f"uploads/{secure_filename(file.filename)}"
    file.save(file_path)
    return file_path

def is_file_valid(file_path):
    try:
        if file_path.lower().endswith(('.pdf', '.docx', '.txt')):
            return True
        else:
            return False
    except Exception as e:
        print(f"Error reading file: {e}")
        return False


#Function to find number of pages
def get_number_of_pages(file_path):
    try:
        if file_path.lower().endswith('.pdf'):
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfFileReader(file)
                return pdf_reader.numPages
        elif file_path.lower().endswith('.docx'):
            # Use the docx library for DOCX files
            doc = Document(file_path)
            return sum(1 for _ in doc.paragraphs)
        elif file_path.lower().endswith('.txt'):
            # Count the lines for TXT files
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                return len(lines)
        else:
            return 0  # Unsupported file type, return 0 pages
    except Exception as e:
        print(f"Error reading file: {e}")
        return 0  # Return 0 in case of an error

def get_pdf_or_txt_page_count(file_path):
    # Reusing existing logic from get_number_of_pages
    return get_number_of_pages(file_path)

def get_docx_page_count(file_path):
    # Reusing existing logic from get_number_of_pages
    return get_number_of_pages(file_path)


ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
FREE_PAGES_LIMIT = 10

@app.route('/print', methods=['GET', 'POST'])
def print_document():
    global current_stage, stage_history, uploaded_file, warning, file_extension

    # Reset warning and file_extension variables
    warning = False
    file_extension = ""

    if request.method == 'POST':
        if 'file' in request.files:
            uploaded_file = request.files['file']

            if uploaded_file and allowed_file(uploaded_file.filename):
                try:
                    uploaded_file_path = save_file(uploaded_file)
                    number_of_pages = get_number_of_pages(uploaded_file_path)

                    print(f"Number of pages: {number_of_pages}")
                    
                    _, file_extension = os.path.splitext(uploaded_file_path)
                    file_extension = file_extension.upper()                             

                    if not is_file_valid(uploaded_file_path):
                        current_stage = 'file_not_allowed'
                        allowed_types = ', '.join(ALLOWED_EXTENSIONS)
                        flash(f"Error: Invalid file content. Please choose a valid file.", 'danger')
                    elif number_of_pages > FREE_PAGES_LIMIT:
                        _, file_extension = os.path.splitext(uploaded_file_path)
                        file_extension = file_extension.upper()

                        # Check file type for specific warning messages
                        if file_extension == '.PDF':
                            warning = True
                            flash("Warning: You have exceeded the limit of free pages for PDF files.", 'warning')
                        elif file_extension == '.TXT':
                            warning = True
                            flash("Warning: You have exceeded the limit of free pages for TXT files.", 'warning')
                        else:
                            flash(f"Warning: You have exceeded the limit of free pages for {file_extension} files.", 'warning')
                    else:
                        stage_history.append(current_stage)
                        current_stage = 'upload_success'
                        return redirect(url_for('print_document'))
                except Exception as e:
                    current_stage = 'file_not_allowed'
                    flash(f"Error: An unexpected error occurred while processing the file.", 'danger')
                    print(f"Unexpected error: {e}")
            else:
                current_stage = 'file_not_allowed'
                allowed_types = ', '.join(ALLOWED_EXTENSIONS)
                flash(f"Error: Invalid file. Allowed file types: {allowed_types}", 'danger')

    return render_template('print.html', current_stage=current_stage, show_buy_button=False, uploaded_file=uploaded_file, warning=warning, file_extension=file_extension)


def upload():
    # Make sure to save the uploaded file to the desired location

    #  saving the file to the "uploads" folder
    uploaded_file = request.files['file']
    uploaded_file.save('uploads/' + uploaded_file.filename)

    # Redirect to the next stage or page
    return redirect(url_for('next_stage'))  # Update 'next_stage' to your actual next stage route

# ... (other imports)

@app.route('/printer_selection', methods=['GET', 'POST'])
def printer_selection():
    available_printers = ['Printer 1', 'Printer 2']  # Replace with your logic to get available printers

    if request.method == 'POST':
        selected_printer = request.form.get('printer')

        if selected_printer in available_printers:
            # Move to the next stage
            global current_stage
            current_stage = 'printing'  # Update to 'printing' or your next stage
            return render_template('print.html', current_stage=current_stage, selected_printer=selected_printer)
        else:
            # Display a notification if the selected printer is not available
            flash("Selected printer is not available. Please choose a different printer.", 'danger')

    # Display available printers
    if available_printers:
        return render_template('printer_selection.html', available_printers=available_printers)
    else:
        # Display a notification if no printers are available
        flash("No printers available. Please connect a printer and try again.", 'danger')
        return render_template('no_printer_available.html')
    

def determine_next_stage(current_stage):
    # Find the index of the current stage in the history
    current_stage_index = stage_history.index(current_stage) if current_stage in stage_history else -1

    if current_stage_index > 0:
        # If the current stage is not the first one in the history,
        # return the stage right behind it
        return stage_history[current_stage_index - 1]
    else:
        # If the current stage is the first one or not found in history,
        # return 'print_document' as the default next stage
        return 'print_document'

@app.route('/move_to_next_stage', methods=['GET'])
def move_to_next_stage():
    global current_stage, stage_history

    # Call the determine_next_stage function to get the next stage
    next_stage = determine_next_stage(current_stage)

    # Add the current stage to the history
    stage_history.append(current_stage)

    # Update the current stage to the next stage
    current_stage = next_stage

    # Redirect to the determined next stage
    return redirect(url_for(current_stage))




@app.route('/move_to_previous_stage', methods=['GET'])
def move_to_previous_stage():
    global current_stage, stage_history
    if len(stage_history) > 1:
        # Remove the current stage from history
        stage_history.pop()
        # Get the previous stage from history
        current_stage = stage_history[-1]
    else:
        # Handle the case where there is no previous stage
        current_stage = 'print_document'

    # Redirect to the previous or default stage
    return redirect(url_for(current_stage))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f"Account created for {form.username.data}", 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash("You have been logged in", 'success')
        return redirect(url_for('home'))
    else:
        flash("Login unsuccessfully! Please check email and password again!")
    return render_template('login.html', title='Login', form=form)

if __name__ == '__main__':
    app.run(debug=True)
