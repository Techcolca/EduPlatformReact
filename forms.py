from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, PasswordField, SelectField, FieldList, FormField
from wtforms.validators import DataRequired, Length, Optional, Email

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
    learning_outcomes = TextAreaField('Learning Outcomes', validators=[DataRequired()])
    is_template = BooleanField('Is Template')

class LessonForm(FlaskForm):
    title = StringField('Lesson Title', validators=[DataRequired(), Length(max=120)])
    content = TextAreaField('Lesson Content', validators=[DataRequired()])
    order = StringField('Lesson Order', validators=[DataRequired()])

class CourseUpdateForm(FlaskForm):
    title = StringField('Course Title', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Course Description', validators=[DataRequired()])
    level = StringField('Course Level', validators=[DataRequired()])
    prerequisites = TextAreaField('Prerequisites', validators=[Optional()])
    learning_outcomes = TextAreaField('Learning Outcomes', validators=[DataRequired()])
    is_template = BooleanField('Is Template')
    lessons = FieldList(FormField(LessonForm), min_entries=1)

class CourseApprovalForm(FlaskForm):
    is_approved = BooleanField('Approve Course')
