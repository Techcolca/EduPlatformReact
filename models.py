from app import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    areas_of_expertise = db.Column(db.Text, nullable=True)
    preferred_subjects = db.Column(db.Text, nullable=True)
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.username}>'

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    level = db.Column(db.String(50))
    prerequisites = db.Column(db.Text)
    lessons = db.Column(db.Text)
    learning_outcomes = db.Column(db.Text)
    is_template = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    instructor = db.relationship('User', foreign_keys=[instructor_id], backref='courses_taught')
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    admin = db.relationship('User', foreign_keys=[admin_id], backref='courses_approved')

    def __repr__(self):
        return f'<Course {self.title}>'
