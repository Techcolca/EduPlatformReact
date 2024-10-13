from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, login_required, logout_user, current_user
from app import app, db
from models import User, Course, Lesson, Quiz, Question
from forms import RegistrationForm, LoginForm, CourseForm, LessonForm, QuizForm
from sqlalchemy.exc import SQLAlchemyError

@app.route('/')
def index():
    courses = Course.query.all()
    return render_template('index.html', courses=courses)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, is_teacher=form.is_teacher.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/course/<int:course_id>')
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('course_detail.html', title=course.title, course=course)

@app.route('/create_course', methods=['GET', 'POST'])
@login_required
def create_course():
    if not current_user.is_teacher:
        flash('Only teachers can create courses.', 'warning')
        return redirect(url_for('index'))
    form = CourseForm()
    if form.validate_on_submit():
        course = Course(title=form.title.data, description=form.description.data, teacher=current_user)
        db.session.add(course)
        db.session.commit()
        flash('Your course has been created!', 'success')
        return redirect(url_for('index'))
    return render_template('create_course.html', title='Create Course', form=form)

@app.route('/course/<int:course_id>/create_lesson', methods=['GET', 'POST'])
@login_required
def create_lesson(course_id):
    course = Course.query.get_or_404(course_id)
    if course.teacher != current_user:
        flash('You can only add lessons to your own courses.', 'warning')
        return redirect(url_for('course_detail', course_id=course.id))
    form = LessonForm()
    if form.validate_on_submit():
        lesson = Lesson(title=form.title.data, content=form.content.data, course=course)
        db.session.add(lesson)
        db.session.commit()
        flash('Your lesson has been created!', 'success')
        return redirect(url_for('course_detail', course_id=course.id))
    return render_template('create_lesson.html', title='Create Lesson', form=form, course=course)

@app.route('/lesson/<int:lesson_id>/create_quiz', methods=['GET', 'POST'])
@login_required
def create_quiz(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    if lesson.course.teacher != current_user:
        flash('You can only add quizzes to your own lessons.', 'warning')
        return redirect(url_for('course_detail', course_id=lesson.course.id))
    form = QuizForm()
    if form.validate_on_submit():
        quiz = Quiz(lesson=lesson)
        db.session.add(quiz)
        question = Question(content=form.question.data, correct_answer=form.correct_answer.data, quiz=quiz)
        db.session.add(question)
        db.session.commit()
        flash('Your quiz question has been added!', 'success')
        return redirect(url_for('course_detail', course_id=lesson.course.id))
    return render_template('create_quiz.html', title='Create Quiz', form=form, lesson=lesson)

@app.route('/quiz/<int:quiz_id>/take', methods=['GET', 'POST'])
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if request.method == 'POST':
        score = 0
        total_questions = len(quiz.questions)
        for question in quiz.questions:
            user_answer = request.form.get(f'question_{question.id}')
            if user_answer and user_answer.lower() == question.correct_answer.lower():
                score += 1
        percentage = (score / total_questions) * 100
        return render_template('quiz_results.html', score=score, total=total_questions, percentage=percentage)
    return render_template('take_quiz.html', title='Take Quiz', quiz=quiz)

@app.route('/profile')
@login_required
def user_profile():
    return render_template('user_profile.html', title='User Profile', user=current_user)

@app.route('/course/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    if course.teacher != current_user:
        flash('You can only edit your own courses.', 'warning')
        return redirect(url_for('course_detail', course_id=course.id))
    
    form = CourseForm(obj=course)
    if form.validate_on_submit():
        form.populate_obj(course)
        db.session.commit()
        flash('Your course has been updated!', 'success')
        return redirect(url_for('course_detail', course_id=course.id))
    
    return render_template('edit_course.html', title='Edit Course', form=form, course=course)

@app.route('/lesson/<int:lesson_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    if lesson.course.teacher != current_user:
        flash('You can only edit lessons in your own courses.', 'warning')
        return redirect(url_for('course_detail', course_id=lesson.course.id))
    form = LessonForm()
    if form.validate_on_submit():
        lesson.title = form.title.data
        lesson.content = form.content.data
        db.session.commit()
        flash('Your lesson has been updated!', 'success')
        return redirect(url_for('course_detail', course_id=lesson.course.id))
    elif request.method == 'GET':
        form.title.data = lesson.title
        form.content.data = lesson.content
    return render_template('edit_lesson.html', title='Edit Lesson', form=form, lesson=lesson)

@app.route('/courses')
def list_courses():
    courses = Course.query.all()
    return render_template('courses.html', title='All Courses', courses=courses)

@app.route('/course/<int:course_id>/delete', methods=['POST'])
@login_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    if course.teacher != current_user:
        abort(403)  # Forbidden
    try:
        db.session.delete(course)
        db.session.commit()
        flash('Your course has been deleted!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        app.logger.error(f"Error deleting course: {str(e)}")
        flash('An error occurred while deleting the course. Please try again.', 'danger')
    return redirect(url_for('index'))