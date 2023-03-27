import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pyshorteners



app = Flask(__name__)

############# SQL Alchemy Configuration #################

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mykey'

db = SQLAlchemy(app)
Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)

# Tell users what view to go to when they need to login.
login_manager.login_view = "login"

#######################################################

############# Create a Model #################
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    @property
    def is_active(self):
        return True

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



class Url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination = db.Column(db.String(500))
    short_url = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('urls', lazy=True))

    def __init__(self, destination, short_url, user_id):
        self.destination = destination
        self.short_url = short_url
        self.user_id = user_id

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


##############################################


@app.route('/')
def welcome():
    return render_template("welcome.html")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        email = request.form.get('uemail')
        password = request.form.get('upassword')
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')



 
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            error = 'Invalid email or password'
            print(error)  # add this line to print out the error message
        else:
            login_user(user)
            flash('You were logged in')
            return redirect(url_for('welcome'))
    return render_template('login.html', error=error)






@app.route('/shorten', methods=['GET', 'POST'])
@login_required
def shorten():
    short_url = '' # default value for GET requests
    if request.method == 'POST':
        destination = request.form.get('url')
        s = pyshorteners.Shortener()
        short_url = s.tinyurl.short(destination)
        url = Url(destination=destination, short_url=short_url, user_id=current_user.id)
        db.session.add(url)
        db.session.commit()
        print(f"short_url: {short_url}")


    return render_template('Application.html', short_url=short_url)



@app.route('/history', methods=['GET', 'POST'])
@login_required
def history():
    if request.method == 'POST':
        # Handle form submission if necessary
        pass
    else:
        # Retrieve all records from the database
        records = Url.query.filter_by(user_id=current_user.id).all()
        # Render the history template with the retrieved records
        return render_template('history.html', records=records)






@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('welcome'))



if __name__ == '__main__':
    app.run(debug = True)