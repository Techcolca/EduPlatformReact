from flask import render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
from app import app, db
from models import User
from forms import TeacherRegistrationForm, LoginForm
import logging

logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    logging.debug("Register route accessed")
    form = TeacherRegistrationForm()
    logging.debug(f"Form created: {form}")
    if form.validate_on_submit():
        logging.debug("Form submitted and validated")
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered. Please use a different email.')
            return redirect(url_for('register'))

        new_user = User(
            username=form.name.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            areas_of_expertise=form.areas_of_expertise.data,
            preferred_subjects=form.preferred_subjects.data
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    else:
        logging.debug(f"Form errors: {form.errors}")
    logging.debug("Rendering register template")
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    logging.debug("Login route accessed")
    form = LoginForm()
    logging.debug(f"Login form created: {form}")
    if form.validate_on_submit():
        logging.debug("Login form submitted and validated")
        logging.debug(f"Email entered: {form.email.data}")
        user = User.query.filter_by(email=form.email.data).first()
        logging.debug(f"User found: {user}")
        if user and check_password_hash(user.password_hash, form.password.data):
            logging.debug("Password check successful")
            login_user(user)
            flash('Logged in successfully.')
            return redirect(url_for('home'))
        else:
            logging.debug("Invalid email or password")
            if not user:
                logging.debug("User not found in database")
            else:
                logging.debug("Incorrect password")
            flash('Invalid email or password.')
    else:
        logging.debug(f"Login form errors: {form.errors}")
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('home'))
