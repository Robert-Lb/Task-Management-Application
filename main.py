from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="task_manager"
)
cursor = db.cursor(dictionary=True)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
             flash('Wrong username or password. Try again?', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            flash('Username already taken!', 'danger')
            return redirect(url_for('register'))
        else:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            db.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['description']
        cursor.execute("INSERT INTO tasks (user_id, title, description) VALUES (%s, %s, %s)", (session['user_id'], title, desc))
        db.commit()
        return redirect(url_for('dashboard'))
        
    cursor.execute("SELECT * FROM tasks WHERE user_id = %s", (session['user_id'],))
    tasks = cursor.fetchall()
    return render_template('dashboard.html', tasks=tasks)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_task(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['description']
        status = request.form['status']
        cursor.execute("UPDATE tasks SET title = %s, description = %s, status = %s WHERE id = %s", (title, desc, status, id))
        db.commit()
        return redirect(url_for('dashboard'))
        
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (id,))
    task = cursor.fetchone()
    return render_template('update_task.html', task=task)

@app.route('/delete/<int:id>')
def delete_task(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    cursor.execute("DELETE FROM tasks WHERE id = %s", (id,))
    db.commit()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)