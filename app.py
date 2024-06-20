from flask import Flask, request, jsonify, render_template, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random
import sqlite3
import mimetypes
from flask_apscheduler import APScheduler
from sqlalchemy.sql.expression import func
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///numbers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.route('/static/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('a.html')

@app.route('/exercises')
def exercises():
    return render_template('es.html')

@app.route('/memories')
def memories():
    return render_template('m.html')

@app.route('/notes')
def notes():
    return render_template('n.html')

def get_random_excuse(table):
    connection = sqlite3.connect('excuses.db')
    cursor = connection.cursor()
    cursor.execute(f"SELECT excuse FROM {table}")
    excuses = cursor.fetchall()
    connection.close()
    if excuses:
        return random.choice(excuses)[0]
    return "No excuses found."

@app.route('/excuses')
def excuses():
    return render_template('e.html')

@app.route('/get_work_excuse')
def get_work_excuse():
    excuse = get_random_excuse('work_excuses')
    return jsonify({'excuse': excuse})

@app.route('/get_goout_excuse')
def get_goout_excuse():
    excuse = get_random_excuse('goout_excuses')
    return jsonify({'excuse': excuse})


@app.route('/happy')
def happy():
    return render_template('happy.html')

@app.route('/sad')
def sad():
    return render_template('sad.html')

app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.static_folder = 'static'
mimetypes.add_type('text/css', '.css')

class Number(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    date_generated = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Number {self.number}>'

class WorkMemory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    memory = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<WorkMemory {self.memory}>'

class OtherMemory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    other_memory = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<OtherMemory {self.other_memory}>'

# Initialize database
with app.app_context():
    db.create_all()

# Setup APScheduler
class Config:
    SCHEDULER_API_ENABLED = True

app.config.from_object(Config())
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

@app.route('/generate', methods=['POST'])
def generate_number():
    random_number = random.randint(1000, 10000)
    new_number = Number(number=random_number)
    db.session.add(new_number)
    db.session.commit()
    return jsonify({'number': random_number, 'message': 'Number generated and stored.'})

@app.route('/correct_answer', methods=['GET'])
def correct_answer():
    yesterday = datetime.utcnow() - timedelta(days=1)
    latest_generated_number = Number.query.filter(Number.date_generated >= yesterday).order_by(Number.date_generated.desc()).first()

    if latest_generated_number:
        return jsonify({'number': latest_generated_number.number})
    else:
        return jsonify({'number': 'No number generated in the last day'})

@app.route('/check', methods=['POST'])
def check_number():
    user_number = int(request.form['number'])
    yesterday = datetime.utcnow() - timedelta(days=1)
    generated_number = Number.query.filter(Number.date_generated >= yesterday).first()

    if generated_number and generated_number.number == user_number:
        return jsonify({'message': 'Correct!'})
    else:
        return jsonify({'message': 'Incorrect :('})

@app.route('/submit_work_memory', methods=['POST'])
def submit_work_memory():
    memory = request.form.get('memory')
    if memory:
        new_memory = WorkMemory(memory=memory)
        db.session.add(new_memory)
        db.session.commit()
        return jsonify({'message': 'Work memory saved successfully.'})
    else:
        return jsonify({'message': 'No memory provided.'}), 400

@app.route('/submit_other_memory', methods=['POST'])
def submit_other_memory():
    other_memory = request.form.get('other_memory')
    if other_memory:
        new_other_memory = OtherMemory(other_memory=other_memory)
        db.session.add(new_other_memory)
        db.session.commit()
        return jsonify({'message': 'Other memory saved successfully.'})
    else:
        return jsonify({'message': 'No other memory provided.'}), 400

@app.route('/get_work_memory')
def get_work_memory():
    work_memory = WorkMemory.query.order_by(func.random()).first()
    if work_memory:
        return jsonify({'id': work_memory.id, 'memory': work_memory.memory})
    else:
        return jsonify({'message': 'No work memory available.'}), 404

@app.route('/get_other_memory')
def get_other_memory():
    other_memory = OtherMemory.query.order_by(func.random()).first()
    if other_memory:
        return jsonify({'id': other_memory.id, 'other_memory': other_memory.other_memory})
    else:
        return jsonify({'message': 'No other memory available.'}), 404

@app.route('/delete_work_memory/<int:id>', methods=['DELETE'])
def delete_work_memory(id):
    work_memory = WorkMemory.query.get(id)
    if work_memory:
        db.session.delete(work_memory)
        db.session.commit()
        return jsonify({'message': 'Work memory deleted successfully.'})
    else:
        return jsonify({'message': 'Work memory not found.'}), 404

@app.route('/delete_other_memory/<int:id>', methods=['DELETE'])
def delete_other_memory(id):
    other_memory = OtherMemory.query.get(id)
    if other_memory:
        db.session.delete(other_memory)
        db.session.commit()
        return jsonify({'message': 'Other memory deleted successfully.'})
    else:
        return jsonify({'message': 'Other memory not found.'}), 404

def cleanup_old_records():
    with app.app_context():
        expiration_date = datetime.utcnow() - timedelta(days=1)
        Number.query.filter(Number.date_generated < expiration_date).delete()
        db.session.commit()

# Schedule the cleanup task
scheduler.add_job(id='cleanup_old_records', func=cleanup_old_records, trigger='interval', hours=24)
if __name__ == '__main__':
   app.run(ssl_context='adhoc', debug=True)
