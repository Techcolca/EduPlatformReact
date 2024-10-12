from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from app import app, db
from models import User, Course, Lesson
from forms import TeacherRegistrationForm, LoginForm, CourseCreationForm, CourseUpdateForm, CourseApprovalForm, LessonForm

@app.route('/')
def home():
    courses = Course.query.all()
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

@app.route('/course/<int:course_id>/approve', methods=['GET', 'POST'])
@login_required
def approve_course(course_id):
    if not current_user.is_admin:
        flash('You do not have permission to approve courses.', 'error')
        return redirect(url_for('course_details', course_id=course_id))
    
    course = Course.query.get_or_404(course_id)
    form = CourseApprovalForm(obj=course)
    
    if form.validate_on_submit():
        course.is_approved = form.is_approved.data
        db.session.commit()
        flash('Course approval status updated.', 'success')
        return redirect(url_for('course_details', course_id=course_id))
    
    return render_template('approve_course.html', form=form, course=course)

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
            course_id=course_id
        )
        db.session.add(new_lesson)
        db.session.commit()
        flash('Lesson created successfully!', 'success')
        return redirect(url_for('course_details', course_id=course_id))
    return render_template('create_lesson.html', form=form, course=course)

@app.route('/course/<int:course_id>/lesson/<int:lesson_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_lesson(course_id, lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    course = Course.query.get_or_404(course_id)
    if course.instructor_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to edit this lesson.', 'error')
        return redirect(url_for('course_details', course_id=course_id))

    form = LessonForm(obj=lesson)
    if form.validate_on_submit():
        form.populate_obj(lesson)
        db.session.commit()
        flash('Lesson updated successfully!', 'success')
        return redirect(url_for('course_details', course_id=course_id))
    return render_template('edit_lesson.html', form=form, course=course, lesson=lesson)

@app.route('/course/<int:course_id>/lesson/<int:lesson_id>/delete', methods=['POST'])
@login_required
def delete_lesson(course_id, lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    course = Course.query.get_or_404(course_id)
    if course.instructor_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to delete this lesson.', 'error')
        return redirect(url_for('course_details', course_id=course_id))

    db.session.delete(lesson)
    db.session.commit()
    flash('Lesson deleted successfully!', 'success')
    return redirect(url_for('course_details', course_id=course_id))

@app.route('/course/<int:course_id>/lesson/<int:lesson_id>')
def lesson_details(course_id, lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    course = Course.query.get_or_404(course_id)
    return render_template('lesson_details.html', lesson=lesson, course=course)
