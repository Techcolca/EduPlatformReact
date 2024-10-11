from flask import render_template, request, redirect, url_for, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from app import app, db
from models import User, Course, Lesson
from forms import TeacherRegistrationForm, LoginForm, CourseCreationForm, CourseUpdateForm, CourseApprovalForm, LessonForm
import logging

@app.route('/')
def home():
    courses = Course.query.all()
    logging.debug(f"Home page: Retrieved {len(courses)} courses")
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
        try:
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
            db.session.flush()

            for lesson_form in form.lessons:
                new_lesson = Lesson(
                    title=lesson_form.title.data,
                    content=lesson_form.content.data,
                    order=lesson_form.order.data,
                    course_id=new_course.id
                )
                db.session.add(new_lesson)

            db.session.commit()
            logging.debug(f"Course created: {new_course}")
            flash('Course created successfully!', 'success')
            return redirect(url_for('course_details', course_id=new_course.id))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating new course: {str(e)}")
            flash('An error occurred while creating the course. Please try again.', 'error')
    return render_template('create_course.html', form=form)

@app.route('/courses')
def list_courses():
    courses = Course.query.all()
    logging.debug(f"Course listing: Retrieved {len(courses)} courses")
    for course in courses:
        logging.debug(f"Course ID: {course.id}, Title: {course.title}, Approved: {course.is_approved}")
    return render_template('list_courses.html', courses=courses)

@app.route('/course/<int:course_id>')
def course_details(course_id):
    course = Course.query.get_or_404(course_id)
    logging.debug(f"Course details: Retrieved course {course}")
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
            existing_lesson_ids = [lesson.id for lesson in course.lessons]
            for lesson_form in form.lessons.data:
                if 'id' in lesson_form and lesson_form['id']:
                    lesson = Lesson.query.get(lesson_form['id'])
                    lesson.title = lesson_form['title']
                    lesson.content = lesson_form['content']
                    lesson.order = int(lesson_form['order'])
                    existing_lesson_ids.remove(lesson.id)
                else:
                    new_lesson = Lesson(
                        title=lesson_form['title'],
                        content=lesson_form['content'],
                        order=int(lesson_form['order']),
                        course_id=course.id
                    )
                    db.session.add(new_lesson)
            
            for lesson_id in existing_lesson_ids:
                lesson_to_delete = Lesson.query.get(lesson_id)
                db.session.delete(lesson_to_delete)

            db.session.commit()
            logging.debug(f"Course updated: {course}")
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
        logging.debug(f"Course deleted: {course}")
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
        try:
            db.session.commit()
            logging.debug(f"Course approval status updated: {course}")
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
    logging.debug(f"Template listing: Retrieved {len(templates)} approved templates")
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
            learning_outcomes=form.learning_outcomes.data,
            is_template=False,
            instructor_id=current_user.id
        )
        db.session.add(new_course)
        try:
            db.session.flush()

            for lesson_form in form.lessons.data:
                new_lesson = Lesson(
                    title=lesson_form['title'],
                    content=lesson_form['content'],
                    order=int(lesson_form['order']),
                    course_id=new_course.id
                )
                db.session.add(new_lesson)

            db.session.commit()
            logging.debug(f"Course created from template: {new_course}")
            flash('Course created from template successfully!')
            return redirect(url_for('course_details', course_id=new_course.id))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating course from template: {str(e)}")
            flash('An error occurred. Please try again.')
    return render_template('create_from_template.html', form=form, template=template)

@app.route('/course/<int:course_id>/lesson/create', methods=['GET', 'POST'])
@login_required
def create_lesson(course_id):
    course = Course.query.get_or_404(course_id)
    if course.instructor_id != current_user.id and not current_user.is_admin:
        abort(403)
    form = LessonForm()
    if form.validate_on_submit():
        new_lesson = Lesson(
            title=form.title.data,
            content=form.content.data,
            order=form.order.data,
            course_id=course.id
        )
        db.session.add(new_lesson)
        try:
            db.session.commit()
            flash('Lesson created successfully!', 'success')
            return redirect(url_for('course_details', course_id=course.id))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating new lesson: {str(e)}")
            flash('An error occurred while creating the lesson. Please try again.', 'error')
    return render_template('create_lesson.html', form=form, course=course)

@app.route('/course/<int:course_id>/lesson/<int:lesson_id>')
def lesson_details(course_id, lesson_id):
    course = Course.query.get_or_404(course_id)
    lesson = Lesson.query.get_or_404(lesson_id)
    if lesson.course_id != course.id:
        abort(404)
    return render_template('lesson_details.html', course=course, lesson=lesson)

@app.route('/course/<int:course_id>/lesson/<int:lesson_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_lesson(course_id, lesson_id):
    course = Course.query.get_or_404(course_id)
    lesson = Lesson.query.get_or_404(lesson_id)
    if course.instructor_id != current_user.id and not current_user.is_admin:
        abort(403)
    if lesson.course_id != course.id:
        abort(404)
    form = LessonForm(obj=lesson)
    if form.validate_on_submit():
        form.populate_obj(lesson)
        try:
            db.session.commit()
            flash('Lesson updated successfully!', 'success')
            return redirect(url_for('lesson_details', course_id=course.id, lesson_id=lesson.id))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating lesson: {str(e)}")
            flash('An error occurred while updating the lesson. Please try again.', 'error')
    return render_template('edit_lesson.html', form=form, course=course, lesson=lesson)

@app.route('/course/<int:course_id>/lesson/<int:lesson_id>/delete', methods=['POST'])
@login_required
def delete_lesson(course_id, lesson_id):
    course = Course.query.get_or_404(course_id)
    lesson = Lesson.query.get_or_404(lesson_id)
    if course.instructor_id != current_user.id and not current_user.is_admin:
        abort(403)
    if lesson.course_id != course.id:
        abort(404)
    try:
        db.session.delete(lesson)
        db.session.commit()
        flash('Lesson deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting lesson: {str(e)}")
        flash('An error occurred while deleting the lesson. Please try again.', 'error')
    return redirect(url_for('course_details', course_id=course.id))

@app.route('/lessons')
def list_lessons():
    lessons = Lesson.query.order_by(Lesson.course_id, Lesson.order).all()
    courses = Course.query.all()
    course_dict = {course.id: course for course in courses}
    
    logging.debug(f"Number of lessons retrieved: {len(lessons)}")
    logging.debug(f"Number of courses retrieved: {len(courses)}")
    logging.debug(f"Is user authenticated: {current_user.is_authenticated}")
    
    if current_user.is_authenticated:
        logging.debug(f"Current user ID: {current_user.id}")
        logging.debug(f"Current user is admin: {current_user.is_admin}")
    
    return render_template('list_lessons.html', lessons=lessons, courses=course_dict, courses_exist=bool(courses))