from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from app import app, db
from models import User, Course, Lesson
from forms import TeacherRegistrationForm, LoginForm, CourseCreationForm, CourseUpdateForm, CourseApprovalForm

@app.route('/')
def home():
    courses = Course.query.filter_by(is_approved=True).all()
    return render_template('home.html', courses=courses)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/courses')
def list_courses():
    courses = Course.query.all()
    return render_template('list_courses.html', courses=courses)

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home'))
        else:
            flash('Invalid email or password', 'error')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('home'))

@app.route('/course/<int:course_id>')
def course_details(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('course_details.html', course=course)

@app.route('/course/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    if course.instructor_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to edit this course.', 'error')
        return redirect(url_for('course_details', course_id=course_id))
    
    form = CourseUpdateForm(obj=course)
    if form.validate_on_submit():
        form.populate_obj(course)
        db.session.commit()
        flash('Course updated successfully!', 'success')
        return redirect(url_for('course_details', course_id=course_id))
    
    return render_template('edit_course.html', form=form, course=course)

@app.route('/course/<int:course_id>/delete', methods=['POST'])
@login_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    if course.instructor_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to delete this course.', 'error')
        return redirect(url_for('course_details', course_id=course_id))
    
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted successfully!', 'success')
    return redirect(url_for('list_courses'))

@app.route('/lessons')
def list_lessons():
    lessons = Lesson.query.all()
    courses = {course.id: course for course in Course.query.all()}
    return render_template('list_lessons.html', lessons=lessons, courses=courses)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = TeacherRegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.name.data, email=form.email.data)
        user.set_password(form.password.data)
        user.areas_of_expertise = form.areas_of_expertise.data
        user.preferred_subjects = form.preferred_subjects.data
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered teacher!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
