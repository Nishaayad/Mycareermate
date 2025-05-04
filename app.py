from flask import Flask, render_template, redirect, url_for, session, request
from flask_mysqldb import MySQL
from forms import RegisterForm, LoginForm
import config

app = Flask(__name__)
app.config.from_object(config)

mysql = MySQL(app)

@app.route('/')
def home():
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s AND password=%s", 
                    (form.email.data, form.password.data))
        user = cur.fetchone()
        if user:
            session['user'] = user[1]
            return redirect(url_for('index'))
        else:
            return 'Invalid Credentials'
    return render_template('login.html', form=form)

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
