from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import get_db, init_db
from functools import wraps
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'potolki-secret-2026'

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ADMIN_LOGIN = 'admin'
ADMIN_PASSWORD = 'potolki123'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/services')
def services():
    conn = get_db()
    services = conn.execute('SELECT * FROM services').fetchall()
    conn.close()
    return render_template('services.html', services=services)

@app.route('/portfolio')
def portfolio():
    conn = get_db()
    works = conn.execute('SELECT * FROM portfolio ORDER BY date DESC').fetchall()
    conn.close()
    return render_template('portfolio.html', works=works)

@app.route('/order', methods=['GET', 'POST'])
def order():
    conn = get_db()
    services = conn.execute('SELECT * FROM services WHERE unit = "м²"').fetchall()
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        area = request.form['area']
        service_id = request.form['service_id']
        conn.execute(
            'INSERT INTO orders (name, phone, area, service_id) VALUES (?, ?, ?, ?)',
            (name, phone, area, service_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('order_success'))
    conn.close()
    return render_template('order.html', services=services)

@app.route('/order/success')
def order_success():
    return render_template('order_success.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if (request.form['username'] == ADMIN_LOGIN and
                request.form['password'] == ADMIN_PASSWORD):
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            error = 'Неверный логин или пароль'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/admin')
@login_required
def admin():
    conn = get_db()
    orders = conn.execute('''
        SELECT orders.*, services.name as service_name
        FROM orders
        LEFT JOIN services ON orders.service_id = services.id
        ORDER BY orders.created_at DESC
    ''').fetchall()
    works = conn.execute('SELECT * FROM portfolio ORDER BY date DESC').fetchall()
    conn.close()
    return render_template('admin.html', orders=orders, works=works)

@app.route('/admin/add_work', methods=['POST'])
@login_required
def add_work():
    title = request.form['title']
    description = request.form['description']
    date = request.form['date']
    photo = None

    file = request.files.get('photo')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        photo = filename

    conn = get_db()
    conn.execute(
        'INSERT INTO portfolio (title, description, date, photo) VALUES (?, ?, ?, ?)',
        (title, description, date, photo)
    )
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/admin/delete_work/<int:id>')
@login_required
def delete_work(id):
    conn = get_db()
    conn.execute('DELETE FROM portfolio WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

