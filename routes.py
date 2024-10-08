from flask import render_template, request, redirect, url_for, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from app import app, db
from models import User, Course
from forms import TeacherRegistrationForm, LoginForm, CourseCreationForm, CourseUpdateForm, CourseApprovalForm
import logging

@app.route('/')
def home():
    courses = Course.query.filter_by(is_approved=True).all()
    return render_template('home.html', courses=courses)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = TeacherRegistrationForm()
    if form.validate_on_submit():
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
        try:
            db.session.commit()
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating new user: {str(e)}")
            flash('An error occurred. Please try again.')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Logged in successfully.')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('home'))

@app.route('/create_course', methods=['GET', 'POST'])
@login_required
def create_course():
    form = CourseCreationForm()
    if form.validate_on_submit():
        new_course = Course(
            title=form.title.data,
            description=form.description.data,
            level=form.level.data,
            prerequisites=form.prerequisites.data,
            lessons=form.lessons.data,
            learning_outcomes=form.learning_outcomes.data,
            is_template=form.is_template.data,
            instructor_id=current_user.id
        )
        db.session.add(new_course)
        try:
            db.session.commit()
            flash('Course created successfully!')
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating new course: {str(e)}")
            flash('An error occurred. Please try again.')
    return render_template('create_course.html', form=form)

@app.route('/courses')
def list_courses():
    courses = Course.query.filter_by(is_approved=True).all()
    return render_template('list_courses.html', courses=courses)

@app.route('/course/<int:course_id>')
def course_details(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('course_details.html', course=course)

@app.route('/course/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    if course.instructor_id != current_user.id and not current_user.is_admin:
        abort(403)
    form = CourseUpdateForm(obj=course)
    if form.validate_on_submit():
        form.populate_obj(course)
        try:
            db.session.commit()
            flash('Course updated successfully!')
            return redirect(url_for('course_details', course_id=course.id))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating course: {str(e)}")
            flash('An error occurred. Please try again.')
    return render_template('edit_course.html', form=form, course=course)

@app.route('/course/<int:course_id>/delete', methods=['POST'])
@login_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    if course.instructor_id != current_user.id and not current_user.is_admin:
        abort(403)
    try:
        db.session.delete(course)
        db.session.commit()
        flash('Course deleted successfully!')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting course: {str(e)}")
        flash('An error occurred. Please try again.')
    return redirect(url_for('home'))

@app.route('/course/<int:course_id>/approve', methods=['GET', 'POST'])
@login_required
def approve_course(course_id):
    if not current_user.is_admin:
        abort(403)
    course = Course.query.get_or_404(course_id)
    form = CourseApprovalForm(obj=course)
    if form.validate_on_submit():
        course.is_approved = form.is_approved.data
        course.admin_id = current_user.id if form.is_approved.data else None
        try:
            db.session.commit()
            flash('Course approval status updated successfully!')
            return redirect(url_for('course_details', course_id=course.id))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating course approval: {str(e)}")
            flash('An error occurred. Please try again.')
    return render_template('approve_course.html', form=form, course=course)

@app.route('/templates')
@login_required
def list_templates():
    templates = Course.query.filter_by(is_template=True, is_approved=True).all()
    return render_template('list_templates.html', templates=templates)

@app.route('/create_from_template/<int:template_id>', methods=['GET', 'POST'])
@login_required
def create_from_template(template_id):
    template = Course.query.get_or_404(template_id)
    form = CourseCreationForm(obj=template)
    if form.validate_on_submit():
        new_course = Course(
            title=form.title.data,
            description=form.description.data,
            level=form.level.data,
            prerequisites=form.prerequisites.data,
            lessons=form.lessons.data,
            learning_outcomes=form.learning_outcomes.data,
            is_template=False,
            instructor_id=current_user.id
        )
        db.session.add(new_course)
        try:
            db.session.commit()
            flash('Course created from template successfully!')
            return redirect(url_for('course_details', course_id=new_course.id))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating course from template: {str(e)}")
            flash('An error occurred. Please try again.')
    return render_template('create_from_template.html', form=form, template=template)