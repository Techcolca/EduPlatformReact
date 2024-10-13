from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from app import app, db
from models import User, Course, Lesson
from forms import TeacherRegistrationForm, LoginForm, CourseCreationForm, CourseUpdateForm, CourseApprovalForm, LessonForm
from werkzeug.security import generate_password_hash, check_password_hash
import logging

@app.route('/course/<int:course_id>/create_lesson', methods=['GET', 'POST'])
@login_required
def create_lesson(course_id):
    logging.info(f"Received course_id: {course_id}")
    course = Course.query.get_or_404(course_id)
    logging.info(f"Retrieved course: {course}")
    if course.instructor_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to create lessons for this course.', 'error')
        return redirect(url_for('course_details', course_id=course_id))

    form = LessonForm()
    if form.validate_on_submit():
        logging.info(f"Form data: {form.data}")
        try:
            # Get the maximum order value for the current course
            max_order = db.session.query(db.func.max(Lesson.order)).filter_by(course_id=course_id).scalar() or 0
            new_order = max_order + 1

            new_lesson = Lesson(
                title=form.title.data,
                content=form.content.data,
                order=new_order,
                course=course
            )
            logging.info(f"New lesson object: {new_lesson}")
            db.session.add(new_lesson)
            db.session.commit()
            flash('Lesson created successfully!', 'success')
            return redirect(url_for('course_details', course_id=course_id))
        except Exception as e:
            logging.error(f"Error creating lesson: {str(e)}")
            db.session.rollback()
            flash('An error occurred while creating the lesson. Please try again.', 'error')
    else:
        logging.info(f"Form validation errors: {form.errors}")
    return render_template('create_lesson.html', form=form, course=course)
@app.route('/')
def home():
    return render_template('home.html')  # or redirect(url_for('login')) if you prefer
# Add other route definitions here...
