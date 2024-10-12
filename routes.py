from app import app, db
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from models import User, Course, Lesson
from forms import TeacherRegistrationForm, LoginForm, CourseCreationForm, CourseUpdateForm, CourseApprovalForm, LessonForm
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = TeacherRegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered.', 'error')
            return redirect(url_for('register'))
        
        user = User(username=form.name.data, email=form.email.data)
        user.set_password(form.password.data)
        user.areas_of_expertise = form.areas_of_expertise.data
        user.preferred_subjects = form.preferred_subjects.data
        
        db.session.add(user)
        db.session.commit()
        
        flash('Congratulations, you are now a registered teacher!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'error')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('home'))

@app.route('/')
def home():
    courses = Course.query.all()
    return render_template('home.html', courses=courses)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/courses')
def list_courses():
    courses = Course.query.all()
    return render_template('list_courses.html', courses=courses)

@app.route('/course/<int:course_id>')
def course_details(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('course_details.html', course=course)

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
            learning_outcomes=form.learning_outcomes.data,
            is_template=form.is_template.data,
            instructor_id=current_user.id
        )
        db.session.add(new_course)
        db.session.commit()
        flash('Course created successfully!', 'success')
        return redirect(url_for('course_details', course_id=new_course.id))
    return render_template('create_course.html', form=form)

@app.route('/lessons')
def list_lessons():
    lessons = Lesson.query.all()
    courses = {course.id: course for course in Course.query.all()}
    return render_template('list_lessons.html', lessons=lessons, courses=courses)

@app.route('/course/<int:course_id>/create_lesson', methods=['GET', 'POST'])
@login_required
def create_lesson(course_id):
    course = Course.query.get_or_404(course_id)
    if course.instructor_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to create lessons for this course.', 'error')
        return redirect(url_for('course_details', course_id=course_id))

    form = LessonForm()
    if form.validate_on_submit():
        new_lesson = Lesson(
            title=form.title.data,
            content=form.content.data,
            order=form.order.data,
            course=course  # Explicitly set the course relationship
        )
        db.session.add(new_lesson)
        db.session.commit()
        flash('Lesson created successfully!', 'success')
        return redirect(url_for('course_details', course_id=course_id))
    return render_template('create_lesson.html', form=form, course=course)

# Add other route definitions here...
