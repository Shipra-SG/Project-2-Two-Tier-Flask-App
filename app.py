import os
import time
import MySQLdb
from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL config
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'mysql_db')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'flaskuser')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'flaskpass')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'flaskapp')

mysql = MySQL(app)

def wait_for_db():
    retries = 10
    while retries > 0:
        try:
            conn = MySQLdb.connect(
                host=app.config['MYSQL_HOST'],
                user=app.config['MYSQL_USER'],
                passwd=app.config['MYSQL_PASSWORD'],
                db=app.config['MYSQL_DB']
            )
            conn.close()
            print("✅ MySQL is ready")
            return
        except Exception:
            print("⏳ Waiting for MySQL...")
            retries -= 1
            time.sleep(5)

    raise Exception("❌ Could not connect to MySQL")

def init_db():
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            message TEXT
        );
        """)
        mysql.connection.commit()
        cur.close()

@app.route('/')
def hello():
    cur = mysql.connection.cursor()
    cur.execute('SELECT message FROM messages')
    messages = cur.fetchall()
    cur.close()
    return render_template('index.html', messages=messages)

@app.route('/submit', methods=['POST'])
def submit():
    new_message = request.form.get('new_message')
    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO messages (message) VALUES (%s)', [new_message])
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': new_message})

if __name__ == '__main__':
    wait_for_db()     # ✅ FIRST wait
    init_db()         # ✅ THEN init
    app.run(host='0.0.0.0', port=5000, debug=True)

