from flask import Flask, render_template, redirect, url_for, session, request
from flask_mysqldb import MySQL
from forms import RegisterForm, LoginForm
from email_validator import validate_email
from flask import flash
import os
from werkzeug.utils import secure_filename
import openai

openai.api_key = 'YOUR_OPENAI_API_KEY'

app = Flask(__name__)
app.secret_key = 'nisha_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Nishasql21@.'
app.config['MYSQL_DB'] = 'nisha'

mysql = MySQL(app)

# ✅ Home Route
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", 
                    (form.username.data, form.email.data, form.password.data))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


# ✅ Login Route

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s AND password=%s", 
                    (form.email.data, form.password.data))
        user = cur.fetchone()
        cur.close()
        if user:
            session['user'] = user[1]
            flash("Login Successful! 👏", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password ❌", "danger")
    return render_template('login.html', form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    message = None

    if request.method == 'POST':
        interest = request.form['interest']
        skills = request.form['skills']
        goal = request.form['goal']
        role = request.form['role']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO career_data (username, interest, skills, goal, role) VALUES (%s, %s, %s, %s, %s)",
                    (session['user'], interest, skills, goal, role))
        mysql.connection.commit()
        cur.close()
        message = "Saved successfully!"

    # ✅ Fetch user profile pic
    cur = mysql.connection.cursor()
    cur.execute("SELECT profile_pic FROM users WHERE username=%s", (session['user'],))
    user_pic = cur.fetchone()[0] or 'default.png'

    # ✅ Fetch user-specific career data
    cur.execute("SELECT interest, skills, goal, role FROM career_data WHERE username = %s", (session['user'],))
    career_entries = cur.fetchall()
    cur.close()

    return render_template('dashboard.html', message=message, user_pic=user_pic, career_entries=career_entries)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    if request.method == 'POST':
        new_email = request.form['email']
        cur.execute("UPDATE users SET email = %s WHERE username = %s", (new_email, session['user']))
        mysql.connection.commit()

    # Fetch updated user info
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
        # after AI generates suggestion
        cur = mysql.connection.cursor()
        cur.execute("""
                    INSERT INTO career_suggestions (username, interest, skills, goal, suggestion)
                    VALUES (%s, %s, %s, %s, %s)
                    """, (session['user'], interest, skills, goal, suggestion))
        mysql.connection.commit()
        cur.close()
        prompt = f"""
        A student has the following:
        - Interests: {interest}
        - Skills: {skills}
        - Career Goal: {goal}
        
        Suggest 3 suitable career paths with a short explanation for each.
        """
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=300,
            temperature=0.7
        )

        suggestion = response.choices[0].text.strip()
        

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
        session['user'] = username  # Update session
        message = "Profile updated successfully!"
        cur.close()
        return render_template('update_profile.html', message=message, user=session['user'], email=email, password=password)

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

        if current != current_db_password:
            message = "Current password is incorrect"
        elif new != confirm:
            message = "New passwords do not match"
        else:
            cur.execute("UPDATE users SET password = %s WHERE username = %s", (new, session['user']))
            mysql.connection.commit()
            message = "Password changed successfully!"
        cur.close()

    return render_template('change_password.html', message=message)

@app.route('/upload_picture', methods=['GET', 'POST'])
def upload_picture():
    if 'user' not in session:
        return redirect(url_for('login'))

    message = None
    if request.method == 'POST':
        file = request.files['profile_pic']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Save filename in DB
            cur = mysql.connection.cursor()
            cur.execute("UPDATE users SET profile_pic=%s WHERE username=%s", (filename, session['user']))
            mysql.connection.commit()
            cur.close()
            message = "Profile picture updated!"
        else:
            message = "Invalid file type. Please upload PNG, JPG, or JPEG."
    
    return render_template('upload_picture.html', message=message)


# ✅ Career Form Page
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

# ✅ Data Preview Route (for admin/testing)
@app.route('/data')
def show_data():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM career_info")
    data = cur.fetchall()
    cur.close()
    return render_template('show_data.html', data=data)

# ✅ Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
