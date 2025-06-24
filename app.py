from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Create DB if not exists
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS jobs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  company TEXT,
                  position TEXT,
                  status TEXT,
                  notes TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM jobs")
    jobs = c.fetchall()
    conn.close()
    return render_template('index.html', jobs=jobs)

@app.route('/add', methods=['POST'])
def add():
    company = request.form['company']
    position = request.form['position']
    status = request.form['status']
    notes = request.form['notes']
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO jobs (company, position, status, notes) VALUES (?, ?, ?, ?)",
              (company, position, status, notes))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/edit/<int:job_id>', methods=['GET', 'POST'])
def edit(job_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    if request.method == 'POST':
        company = request.form['company']
        position = request.form['position']
        status = request.form['status']
        notes = request.form['notes']
        c.execute("UPDATE jobs SET company=?, position=?, status=?, notes=? WHERE id=?",
                  (company, position, status, notes, job_id))
        conn.commit()
        conn.close()
        return redirect('/')
    
    c.execute("SELECT * FROM jobs WHERE id=?", (job_id,))
    job = c.fetchone()
    conn.close()
    return render_template('form.html', job=job)


@app.route('/delete/<int:job_id>')
def delete(job_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM jobs WHERE id=?", (job_id,))
    conn.commit()
    conn.close()
    return redirect('/')
