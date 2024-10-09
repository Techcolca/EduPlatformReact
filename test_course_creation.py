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
        test_user = User(
            username='testuser',
            email='test@example.com',
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

    def test_course_creation_page_load(self):
        response = self.client.get('/create_course')
        self.assertEqual(response.status_code, 302)  # Should redirect to login page
        logging.debug(f"Initial response: {response}")

        with self.client:
            user = User.query.filter_by(email='test@example.com').first()
            logging.debug(f"Retrieved user: {user}")
            login_user(user)
            response = self.client.get('/create_course')
            logging.debug(f"Response after login: {response}")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Create a New Course', response.data)

    def test_course_creation(self):
        with self.client:
            user = User.query.filter_by(email='test@example.com').first()
            logging.debug(f"Retrieved user for course creation: {user}")
            login_user(user)
            response = self.client.post('/create_course', data={
                'title': 'Test Course',
                'description': 'This is a test course',
                'level': 'Beginner',
                'prerequisites': 'None',
                'lessons': 'Lesson 1, Lesson 2',
                'learning_outcomes': 'Outcome 1, Outcome 2',
                'is_template': False
            }, follow_redirects=True)
            logging.debug(f"Course creation response: {response}")
            logging.debug(f"Response data: {response.data}")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Course created successfully!', response.data)

            # Check if the course was actually created in the database
            course = Course.query.filter_by(title='Test Course').first()
            logging.debug(f"Created course: {course}")
            self.assertIsNotNone(course)
            self.assertEqual(course.description, 'This is a test course')
            self.assertEqual(course.level, 'Beginner')
            self.assertEqual(course.prerequisites, 'None')
            self.assertEqual(course.lessons, 'Lesson 1, Lesson 2')
            self.assertEqual(course.learning_outcomes, 'Outcome 1, Outcome 2')
            self.assertFalse(course.is_template)

    def test_course_creation_validation(self):
        with self.client:
            user = User.query.filter_by(email='test@example.com').first()
            login_user(user)
            response = self.client.post('/create_course', data={
                'title': '',  # Empty title should fail validation
                'description': 'This is a test course',
                'level': 'Beginner',
                'prerequisites': 'None',
                'lessons': 'Lesson 1, Lesson 2',
                'learning_outcomes': 'Outcome 1, Outcome 2',
                'is_template': False
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'This field is required', response.data)

    def test_course_creation_as_template(self):
        with self.client:
            user = User.query.filter_by(email='test@example.com').first()
            login_user(user)
            response = self.client.post('/create_course', data={
                'title': 'Template Course',
                'description': 'This is a template course',
                'level': 'Intermediate',
                'prerequisites': 'Basic knowledge',
                'lessons': 'Template Lesson 1, Template Lesson 2',
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
