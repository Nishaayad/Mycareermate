from flask import Flask, render_template, redirect, url_for, session, request
from flask_mysqldb import MySQL
from forms import RegisterForm, LoginForm

app = Flask(__name__)
app.secret_key = 'nisha_secret_key'

# ✅ MySQL Configuration (using flask_mysqldb only)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Nishasql21@.'
app.config['MYSQL_DB'] = 'nisha'

mysql = MySQL(app)

# ✅ Home Route
@app.route('/')
def index():
    return render_template('index.html')

# ✅ Register Route
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
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid Credentials'
    return render_template('login.html', form=form)

# ✅ Dashboard Route (with form to store career data)
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
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
        return render_template('dashboard.html', message="Saved successfully!")
    
    return render_template('dashboard.html')

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
        return render_template('success.html')  # 👈 Required
    return render_template('career_form.html')

# ✅ Data Preview Route (for admin/testing)
@app.route('/data')
def show_data():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM career_info")
    data = cur.fetchall()
    cur.close()
    return str(data)

# ✅ Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
