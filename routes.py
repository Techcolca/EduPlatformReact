from flask import render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from app import app, db
from models import User
from forms import TeacherRegistrationForm

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    print("Register route accessed")
    form = TeacherRegistrationForm()
    print(f"Form created: {form}")
    if form.validate_on_submit():
        print("Form submitted and validated")
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
        return redirect(url_for('home'))
    else:
        print(f"Form errors: {form.errors}")
    print("Rendering register template")
    return render_template('register.html', form=form)
