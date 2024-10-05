from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///schedules.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(50), unique=True, nullable=False)
    buttons = db.relationship('Button', backref='schedule', lazy=True)


class Button(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=False)
    when = db.Column(db.String(100), nullable=True)
    where = db.Column(db.String(100), nullable=True)
    who = db.Column(db.String(100), nullable=True)
    color = db.Column(db.String(20), nullable=False)


# Создание базы данных, если она еще не существует
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/create_schedule', methods=['GET', 'POST'])
def create_schedule():
    if request.method == 'POST':
        when = request.form.get('when')
        where = request.form.get('where')
        who = request.form.get('who')
        return redirect(url_for('edit_temp_schedule', when=when, where=where, who=who))

    return render_template('create_schedule.html')


@app.route('/edit_temp_schedule', methods=['GET', 'POST'])
def edit_temp_schedule():
    if request.method == 'POST':
        when = request.form.get('when')
        where = request.form.get('where')
        who = request.form.get('who')
        temp_buttons = request.args.getlist('temp_buttons')

        if when or where or who:
            temp_buttons.append((when, where, who))

        return render_template('edit_temp_schedule.html', temp_buttons=temp_buttons)

    temp_buttons = request.args.getlist('temp_buttons', type=str)
    return render_template('edit_temp_schedule.html', temp_buttons=temp_buttons)


@app.route('/save_schedule', methods=['POST'])
def save_schedule():
    password = request.form['password']
    temp_buttons = request.form.getlist('temp_buttons')

    new_schedule = Schedule(password=password)
    db.session.add(new_schedule)
    db.session.commit()

    for button_data in temp_buttons:
        when, where, who = button_data.split(',')
        color = 'pink' if when and where else 'lightgreen' if when else 'gray'
        new_button = Button(schedule_id=new_schedule.id, when=when, where=where, who=who, color=color)
        db.session.add(new_button)

    db.session.commit()
    return redirect(url_for('home'))

@app.route('/edit_schedule/<int:schedule_id>', methods=['GET', 'POST'])
def edit_schedule(schedule_id):
    schedule = Schedule.query.get(schedule_id)
    if request.method == 'POST':
        password = request.form['password']
        schedule.password = password
        db.session.commit()
        return redirect(url_for('edit_schedule', schedule_id=schedule.id))

    buttons = Button.query.filter_by(schedule_id=schedule.id).all()
    return render_template('schedule.html', schedule=schedule, buttons=buttons)

if __name__ == '__main__':
    app.run(debug=True)