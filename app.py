from flask import Flask, render_template, redirect, url_for, session, request,flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
from forms import RegisterForm, LoginForm
from email_validator import validate_email
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from bot import carrermate_aibot 
from functools import wraps
from forms import ForgotPasswordForm 
from MySQLdb.cursors import DictCursor
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY') 
app.config['SECRET_KEY'] = 'mycareermate21@'


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Nishasql21@.'
app.config['MYSQL_DB'] = 'nisha'
mysql = MySQL(app)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_query = request.form['user_input']
    bot_response = carrermate_aibot(user_query)
    return render_template('chatbot.html', user_input=user_query, bot_response=bot_response)

@app.route("/", methods=["GET", "POST"])
def index():
    suggestion = ""
    if request.method == "POST":
        user_prompt = request.form["prompt"]
        suggestion = carrermate_aibot(user_prompt)  
    return render_template("index.html", suggestion=suggestion)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['fullname']
        email = request.form['email']
        gender = request.form['gender']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords don't match!", "error")
            return redirect(url_for('register'))

        cur = mysql.connection.cursor()

        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        existing_user = cur.fetchone()

        if existing_user:
            flash("Email already exists!", "error")
            return redirect(url_for('register'))

        profile_pic = 'boy.png' if gender == 'boy' else 'woman.png'
        hashed_password = generate_password_hash(password)

        cur.execute("""
            INSERT INTO users (username, email, password, profile_pic)
            VALUES (%s, %s, %s, %s)
        """, (username, email, hashed_password, profile_pic))

        mysql.connection.commit()
        cur.close()

        flash("Registered successfully! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # Use DictCursor to get column names as keys
        cur = mysql.connection.cursor(DictCursor)
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user['password'], password):
            # ✅ Store all relevant session info
            session['user'] = user['username']         # For displaying on dashboard
            session['email'] = user['email']           # For fetching from DB
            session['gender'] = user['gender']
            session['profile_pic'] = user['profile_pic']
            
            flash(f'✅ Welcome back, {user["username"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('❌ Invalid email or password', 'danger')

    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']           
        email = request.form['email']         
        password = request.form['password']     
        
        hashed_password = generate_password_hash(password)  
        cur = mysql.connection.cursor()       
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        existing_user = cur.fetchone()
        
        if existing_user:
            flash('Email already registered, please login', 'error')
            cur.close()
            return redirect('/signup')

        cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                    (name, email, hashed_password))
        mysql.connection.commit()  
        cur.close()               
        
        flash('Signup successful! Please login.', 'success')
        return redirect('/login')
    return render_template('signup.html')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:   
            flash('Please login first', 'error')
            return redirect(url_for('login'))    
        return f(*args, **kwargs)  
    return decorated_function

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        flash('⚠️ Please login to access the dashboard.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        interest = request.form['interest']
        skills = request.form['skills']
        goal = request.form['goal']
        role = request.form['role']

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO career_data (username, interest, skills, goal, role) VALUES (%s, %s, %s, %s, %s)",
                        (session['user'], interest, skills, goal, role))
            mysql.connection.commit()
            cur.close()
            flash('✅ Career data saved successfully!', 'success')
        except Exception as e:
            flash('❌ Something went wrong while saving your data.', 'danger')

    cur = mysql.connection.cursor()

    # ✅ Fetch using email now (correct)
    cur.execute("SELECT profile_pic, gender FROM users WHERE email = %s", (session['email'],))
    result = cur.fetchone()

    if result:
        profile_pic, gender = result
        if profile_pic:
            user_pic = profile_pic
        else:
            if gender == 'girl':
                user_pic = 'woman.png'
            elif gender == 'boy':
                user_pic = 'boy.png'
            else:
                user_pic = 'default.png'
    else:
        user_pic = 'default.png'

    # ✅ Fetch user's career entries using username
    cur.execute("SELECT interest, skills, goal, role FROM career_data WHERE username = %s", (session['user'],))
    career_entries = cur.fetchall()
    cur.close()

    return render_template('dashboard.html', user_pic=user_pic, career_entries=career_entries)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    if request.method == 'POST':
        new_email = request.form['email']
        cur.execute("UPDATE users SET email = %s WHERE username = %s", (new_email, session['user']))
        mysql.connection.commit()

    cur.execute("SELECT username, email FROM users WHERE username = %s", (session['user'],))
    user_data = cur.fetchone()
    cur.close()

    return render_template('profile.html', user=user_data)

@app.route('/career_suggestion', methods=['GET', 'POST'])
def career_suggestion():
    if 'user' not in session:
        return redirect(url_for('login'))

    suggestion = None

    if request.method == 'POST':
        interest = request.form['interest']
        skills = request.form['skills']
        goal = request.form['goal']

        prompt = f"""
        A student has the following:
        - Interests: {interest}
        - Skills: {skills}
        - Career Goal: {goal}

        Suggest 3 suitable career paths with a short explanation for each.
        """
        suggestion = carrermate_aibot(prompt)  

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO career_suggestions (username, interest, skills, goal, suggestion)
            VALUES (%s, %s, %s, %s, %s)
        """, (session['user'], interest, skills, goal, suggestion))
        mysql.connection.commit()
        cur.close()

    return render_template('career_suggestion.html', suggestion=suggestion)


@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if 'user' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        cur.execute("UPDATE users SET username=%s, email=%s, password=%s WHERE username=%s",
                    (username, email, password, session['user']))
        mysql.connection.commit()
        session['user'] = username
        message = "Profile updated successfully!"
        cur.close()
        return render_template('update_profile.html', message=message, user=username, email=email, password=password)

    cur.execute("SELECT username, email, password FROM users WHERE username=%s", (session['user'],))
    user_data = cur.fetchone()
    cur.close()

    return render_template('update_profile.html', user=user_data[0], email=user_data[1], password=user_data[2])

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user' not in session:
        return redirect(url_for('login'))

    message = None
    if request.method == 'POST':
        current = request.form['current_password']
        new = request.form['new_password']
        confirm = request.form['confirm_password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT password FROM users WHERE username = %s", (session['user'],))
        current_db_password = cur.fetchone()[0]
        if not check_password_hash(current_db_password, current):
            message = "Current password is incorrect"
        elif new != confirm:
            message = "New passwords do not match"
        else:
            new_hashed = generate_password_hash(new)
            cur.execute("UPDATE users SET password = %s WHERE username = %s", (new_hashed, session['user']))
            mysql.connection.commit()
            message = "Password changed successfully!"
        cur.close()

    return render_template('change_password.html', message=message)

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()

    if form.validate_on_submit():
        email = form.email.data

        cur = mysql.connection.cursor(DictCursor)
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user:
            flash("✅ Account found! You can now reset your password.", "success")
            # You can redirect to reset-password page or just render here
            return redirect(url_for('reset_password', email=email))
        else:
            flash("❌ Email not found in our records.", "danger")

    return render_template('forgot_password.html', form=form)


@app.route('/upload-picture', methods=['GET', 'POST'])
def upload_picture():
    message = None

    if request.method == 'POST':
        file = request.files['profile_pic']  # 'profile_pic' must match the form input name

        if file and allowed_file(file.filename):  # Check file type
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)  # Save file to folder

            # Update DB with new filename
            cur = mysql.connection.cursor()
            cur.execute("UPDATE users SET profile_pic=%s WHERE username=%s", (filename, session['user']))
            mysql.connection.commit()
            cur.close()
            message = "✅ Profile picture updated!"
        else:
            message = "❌ Invalid file type. Please upload PNG, JPG, or JPEG."

    return render_template('upload_picture.html', message=message)

@app.route('/career_form', methods=['GET', 'POST'])
def career_form():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        career_goal = request.form['career_goal']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO career_info (name, email, career_goal) VALUES (%s, %s, %s)", 
                    (name, email, career_goal))
        mysql.connection.commit()
        cur.close()
        return render_template('success.html')
    return render_template('career_form.html')

@app.route('/data')
def show_data():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM career_info")
    data = cur.fetchall()
    cur.close()
    return render_template('show_data.html', data=data)

@app.route('/logout')
def logout():
    session.clear()  # Clear user session
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))  

if __name__ == '__main__':
    app.run(debug=True)
