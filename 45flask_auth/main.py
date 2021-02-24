from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

##CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
#Line below only required once, when creating DB. 
# db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return render_template("index.html", logged_in=current_user.is_authenticated)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        new_email = request.form['email']
        hashed_salted_password = generate_password_hash(password=request.form['password'], method='pbkdf2:sha256', salt_length=8)
        new_name = request.form['name']

        if bool(User.query.filter_by(email=new_email).first()):
            flash('This email is already registered', 'Please log in')
            return render_template("login.html", logged_in=current_user.is_authenticated)
        else:

            new_user = User(
                email=new_email,
                password=hashed_salted_password,
                name=new_name
            )
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)

            return redirect(url_for('secrets'))
    else:
        return render_template("register.html", logged_in=current_user.is_authenticated)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        given_password = request.form['password']
        given_email = request.form['email']
        user = User.query.filter_by(email=given_email).first()
        if user:
            if check_password_hash(user.password, given_password):
                login_user(user)
                return redirect(url_for('secrets'))
            else:
                flash(u'Password does not match email', 'error')
        else:
            flash(u'Invalid email', 'error')
    return render_template("login.html", logged_in=current_user.is_authenticated)


@app.route('/secrets')
@login_required
def secrets():
    username = current_user.name
    return render_template("secrets.html", name=username, logged_in=current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/download')
@login_required
def download():
    return send_from_directory('static', 'files/cheat_sheet.pdf')


if __name__ == "__main__":
    app.run(debug=True)
