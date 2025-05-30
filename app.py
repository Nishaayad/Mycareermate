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
from functools import wraps
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

from flask import session, g

@app.before_request
def load_user():
    g.user = session.get('user') 

from flask import session, redirect, url_for

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    user = session.get('user') 
    if not user:
        session['guest'] = True

    suggestion = None
    if request.method == 'POST':
        prompt = request.form['prompt']
        suggestion = carrermate_aibot(prompt)
    
    return render_template('chat.html', suggestion=suggestion)

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
        username = request.form['username']
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
            INSERT INTO users (username, email, password, gender, profile_pic)
            VALUES (%s, %s, %s, %s, %s)
        """, (username, email, hashed_password, gender, profile_pic))
        mysql.connection.commit()
        cur.close()

        flash("Registered successfully! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash("Please enter both username and password", "error")
            return redirect(url_for('login'))

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['user'] = user[1]
            session['email'] = user[2]
            session['gender'] = user[4]
            session['profile_pic'] = user[5]
            flash(f'✅ Welcome back, {user[1]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password!", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

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
            flash('Please login first', 'warning')
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
    cur.execute("SELECT interest, skills, goal, role FROM career_data WHERE username = %s", (session['user'],))
    career_entries = cur.fetchall()
    cur.close()

    return render_template('dashboard.html', user_pic=user_pic, career_entries=career_entries)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' not in session:
        flash("⚠️ Please login first.", "warning")
        return redirect(url_for('login'))

    username = session['user']

    if request.method == 'POST':
        email = request.form['email']
        address = request.form['address']
        skills = request.form['skills']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM profiles WHERE username = %s", (username,))
        existing = cur.fetchone()

        if existing:
            cur.execute("""
                UPDATE profiles SET email=%s, address=%s, skills=%s WHERE username=%s
            """, (email, address, skills, username))
        else:
            cur.execute("""
                INSERT INTO profiles (username, email, address, skills) 
                VALUES (%s, %s, %s, %s)
            """, (username, email, address, skills))

        mysql.connection.commit()
        cur.close()
        flash("✅ Profile updated successfully!", "success")
        return redirect(url_for('account'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT email, address, skills FROM profiles WHERE username = %s", (username,))
    profile_data = cur.fetchone()
    cur.close()

    return render_template('profile.html', profile=profile_data)

@app.route('/account')
def account():
    if 'user' not in session:
        flash("⚠️ Please login first.", "warning")
        return redirect(url_for('login'))

    username = session['user']
    cur = mysql.connection.cursor()

    cur.execute("SELECT email, address, skills FROM profiles WHERE username = %s", (username,))
    profile = cur.fetchone()

    cur.execute("SELECT profile_pic, role FROM users WHERE username = %s", (username,))
    user_info = cur.fetchone()

    cur.close()

    return render_template('account.html', profile=profile, user_info=user_info)

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

            return redirect(url_for('reset_password', email=email))
        else:
            flash("❌ Email not found in our records.", "danger")

    return render_template('forgot_password.html', form=form)


@app.route('/upload-picture', methods=['GET', 'POST'])
def upload_picture():
    message = None

    if request.method == 'POST':
        file = request.files['profile_pic']  

        if file and allowed_file(file.filename):  
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath) 

            
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

@app.route('/dashboard-visuals')
def dashboard_visuals():
    cur = mysql.connection.cursor()
    cur.execute("SELECT career_field, COUNT(*) FROM career_data GROUP BY career_field")
    results = cur.fetchall()

    labels = [row[0] for row in results]
    values = [row[1] for row in results]

    return render_template('dashboard_visuals.html', labels=labels, values=values)

@app.route('/data')
def show_data():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM career_info")
    data = cur.fetchall()
    cur.close()
    return render_template('show_data.html', data=data)

@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'user_id' not in session:
        flash("Please log in to delete your account.", "warning")
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    
    try:
        cur.execute("DELETE FROM users WHERE id = %s", (session['user_id'],))
        mysql.connection.commit()

        session.clear()
        flash("Your account has been successfully deleted.", "success")
        return redirect(url_for('signup'))

    except Exception as e:
        mysql.connection.rollback()
        flash("Something went wrong while deleting the account. Please try again.", "danger")
        return redirect(url_for('account'))

    finally:
        cur.close()

@app.route('/logout')
def logout():
    session.clear()  
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))  

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)
