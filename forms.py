from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Optional

class TeacherRegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    areas_of_expertise = TextAreaField('Areas of Expertise', validators=[DataRequired()])
    preferred_subjects = TextAreaField('Preferred Subjects', validators=[DataRequired()])

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class CourseCreationForm(FlaskForm):
    title = StringField('Course Title', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Course Description', validators=[DataRequired()])
    level = StringField('Course Level', validators=[DataRequired()])
    prerequisites = TextAreaField('Prerequisites', validators=[Optional()])
    lessons = TextAreaField('Lessons', validators=[DataRequired()])
    learning_outcomes = TextAreaField('Learning Outcomes', validators=[DataRequired()])
    is_template = BooleanField('Is Template')

class CourseUpdateForm(FlaskForm):
    title = StringField('Course Title', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Course Description', validators=[DataRequired()])
    level = StringField('Course Level', validators=[DataRequired()])
    prerequisites = TextAreaField('Prerequisites', validators=[Optional()])
    lessons = TextAreaField('Lessons', validators=[DataRequired()])
    learning_outcomes = TextAreaField('Learning Outcomes', validators=[DataRequired()])
    is_template = BooleanField('Is Template')

class CourseApprovalForm(FlaskForm):
    is_approved = BooleanField('Approve Course')
