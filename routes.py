from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import User, Course, Lesson
from forms import TeacherRegistrationForm, LoginForm, CourseCreationForm, CourseUpdateForm, CourseApprovalForm
import logging

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
            db.session.commit()
            logging.debug(f"Course created: {new_course}")
            flash('Course created successfully!', 'success')
            return redirect(url_for('course_details', course_id=new_course.id))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating new course: {str(e)}")
            flash('An error occurred while creating the course. Please try again.', 'error')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", 'error')
                logging.error(f"Form validation error in {field}: {error}")

    return render_template('create_course.html', form=form)

# Add other route functions here...
