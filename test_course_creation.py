import unittest
from app import app, db
from models import User, Course
from flask_login import login_user
from werkzeug.security import generate_password_hash
import logging

logging.basicConfig(level=logging.DEBUG)

class TestCourseCreation(unittest.TestCase):
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
        db.session.commit()
        
        # Create a test user with a unique email
        test_user = User(
            username='testuser',
            email='test_user@example.com',
            password_hash=generate_password_hash('testpassword'),
            areas_of_expertise='Testing',
            preferred_subjects='Unit Tests'
        )
        db.session.add(test_user)
        db.session.commit()
        logging.debug(f"Test user created: {test_user}")

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, email, password):
        return self.client.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def test_course_creation_page_load(self):
        with self.client:
            self.login('test_user@example.com', 'testpassword')
            response = self.client.get('/create_course')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Create a New Course', response.data)

    def test_course_creation(self):
        with self.client:
            self.login('test_user@example.com', 'testpassword')
            response = self.client.post('/create_course', data={
                'title': 'Test Course',
                'description': 'This is a test course',
                'level': 'Beginner',
                'prerequisites': 'None',
                'learning_outcomes': 'Outcome 1, Outcome 2',
                'is_template': False  # Explicitly set is_template to False
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Course created successfully!', response.data)

            # Check if the course was actually created in the database
            course = Course.query.filter_by(title='Test Course').first()
            self.assertIsNotNone(course)
            self.assertEqual(course.description, 'This is a test course')
            self.assertEqual(course.level, 'Beginner')
            self.assertEqual(course.prerequisites, 'None')
            self.assertEqual(course.learning_outcomes, 'Outcome 1, Outcome 2')
            self.assertFalse(course.is_template)

    def test_course_creation_validation(self):
        with self.client:
            self.login('test_user@example.com', 'testpassword')
            response = self.client.post('/create_course', data={
                'title': '',  # Empty title should fail validation
                'description': 'This is a test course',
                'level': 'Beginner',
                'prerequisites': 'None',
                'learning_outcomes': 'Outcome 1, Outcome 2',
                'is_template': False
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'This field is required', response.data)

    def test_course_creation_as_template(self):
        with self.client:
            self.login('test_user@example.com', 'testpassword')
            response = self.client.post('/create_course', data={
                'title': 'Template Course',
                'description': 'This is a template course',
                'level': 'Intermediate',
                'prerequisites': 'Basic knowledge',
                'learning_outcomes': 'Template Outcome 1, Template Outcome 2',
                'is_template': True
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Course created successfully!', response.data)

            # Check if the template course was created in the database
            course = Course.query.filter_by(title='Template Course').first()
            self.assertIsNotNone(course)
            self.assertTrue(course.is_template)

if __name__ == '__main__':
    unittest.main()
