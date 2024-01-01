from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a random string
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Use SQLite for simplicity
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Define User model for the database
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_seller = db.Column(db.Boolean, default=False)
    cars = db.relationship('Car', backref='owner', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

# Define Car model for the database
class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Form for adding a new car
class CarForm(FlaskForm):
    name = StringField('Car Name', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        is_seller = 'is_seller' in request.form  # Check if the user wants to be a seller

        user = User(username=username, email=email, is_seller=is_seller)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/profile')
@login_required
def profile():
    cars = Car.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', user=current_user, cars=cars)


@app.route('/cars')
@login_required
def display_cars():
    cars = Car.query.all()
    return render_template('cars.html', cars=cars)

@app.route('/add_car', methods=['GET', 'POST'])
@login_required
def add_car():
    form = CarForm()

    if form.validate_on_submit():
        car = Car(name=form.name.data, price=form.price.data, image_url='default_image_url', owner=current_user)
        db.session.add(car)
        db.session.commit()

        flash(f'Car "{form.name.data}" has been added for sale!', 'success')
        return redirect(url_for('display_cars'))

    return render_template('add_car.html', form=form)

@app.route('/buy/<int:car_id>')
@login_required
def buy_car(car_id):
    car = Car.query.get_or_404(car_id)
    # Implement logic for buying the car (e.g., updating user's owned cars)
    flash(f'You have successfully bought {car.name} for ${car.price}', 'success')
    return redirect(url_for('display_cars'))

@app.route('/sell/<int:car_id>')
@login_required
def sell_car(car_id):
    car = Car.query.get_or_404(car_id)
    # Implement logic for selling the car (e.g., updating car ownership)
    flash(f'You have successfully listed {car.name} for sale', 'success')
    return redirect(url_for('display_cars'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = 'remember' in request.form

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))

        flash('Login unsuccessful. Please check your email and password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables before running the app
    app.run(debug=True)
