import unittest
from app import app, db
from models import User, Course, Lesson
from flask_login import login_user
from werkzeug.security import generate_password_hash

class TestCourseAndLesson(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Clear the database before each test
        db.session.query(User).delete()
        db.session.query(Course).delete()
        db.session.query(Lesson).delete()
        db.session.commit()
        
        # Create a test user
        test_user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('testpassword'),
            areas_of_expertise='Testing',
            preferred_subjects='Unit Tests'
        )
        db.session.add(test_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, email, password):
        return self.client.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def test_course_creation(self):
        self.login('test@example.com', 'testpassword')
        response = self.client.post('/create_course', data=dict(
            title='Test Course',
            description='This is a test course',
            level='Beginner',
            prerequisites='None',
            learning_outcomes='Test outcomes',
            is_template=False
        ), follow_redirects=True)
        self.assertIn(b'Course created successfully!', response.data)

        # Check if the course was actually created in the database
        course = Course.query.filter_by(title='Test Course').first()
        self.assertIsNotNone(course)
        self.assertEqual(course.description, 'This is a test course')
        self.assertEqual(course.level, 'Beginner')
        self.assertEqual(course.prerequisites, 'None')
        self.assertEqual(course.learning_outcomes, 'Test outcomes')
        self.assertFalse(course.is_template)

    def test_course_editing(self):
        self.login('test@example.com', 'testpassword')
        # Create a course
        course = Course(
            title='Original Course',
            description='Original description',
            level='Intermediate',
            prerequisites='Some prerequisites',
            learning_outcomes='Original outcomes',
            is_template=False,
            instructor_id=User.query.filter_by(email='test@example.com').first().id
        )
        db.session.add(course)
        db.session.commit()

        # Edit the course
        response = self.client.post(f'/course/{course.id}/edit', data=dict(
            title='Updated Course',
            description='Updated description',
            level='Advanced',
            prerequisites='Updated prerequisites',
            learning_outcomes='Updated outcomes',
            is_template=True
        ), follow_redirects=True)
        self.assertIn(b'Course updated successfully!', response.data)

    def test_lesson_creation(self):
        self.login('test@example.com', 'testpassword')
        # Create a course
        course = Course(
            title='Test Course',
            description='Test description',
            level='Beginner',
            prerequisites='None',
            learning_outcomes='Test outcomes',
            is_template=False,
            instructor_id=User.query.filter_by(email='test@example.com').first().id
        )
        db.session.add(course)
        db.session.commit()

        # Create a lesson
        response = self.client.post(f'/course/{course.id}/lesson/create', data=dict(
            title='Test Lesson',
            content='This is a test lesson',
            order='1'
        ), follow_redirects=True)
        self.assertIn(b'Lesson created successfully!', response.data)

if __name__ == '__main__':
    unittest.main()
