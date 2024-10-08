import unittest
from app import app, db
from models import User
from forms import TeacherRegistrationForm
from werkzeug.security import check_password_hash

class TestTeacherRegistration(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_form_validation(self):
        with app.app_context():
            form = TeacherRegistrationForm(
                name='',
                email='invalid_email',
                password='short',
                areas_of_expertise='',
                preferred_subjects=''
            )
            self.assertFalse(form.validate())
            self.assertIn('name', form.errors)
            self.assertIn('email', form.errors)
            self.assertIn('password', form.errors)
            self.assertIn('areas_of_expertise', form.errors)
            self.assertIn('preferred_subjects', form.errors)

    def test_successful_registration(self):
        response = self.client.post('/register', data={
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': 'secure_password',
            'areas_of_expertise': 'Math, Science',
            'preferred_subjects': 'Algebra, Physics'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful!', response.data)
        with app.app_context():
            user = User.query.filter_by(email='john@example.com').first()
            self.assertIsNotNone(user)

    def test_existing_email_registration(self):
        # First registration
        self.client.post('/register', data={
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': 'secure_password',
            'areas_of_expertise': 'Math, Science',
            'preferred_subjects': 'Algebra, Physics'
        })
        # Second registration with the same email
        response = self.client.post('/register', data={
            'name': 'Jane Doe',
            'email': 'john@example.com',
            'password': 'another_password',
            'areas_of_expertise': 'English, History',
            'preferred_subjects': 'Literature, World History'
        }, follow_redirects=True)
        self.assertIn(b'Email already registered', response.data)

    def test_password_hashing(self):
        self.client.post('/register', data={
            'name': 'Alice Smith',
            'email': 'alice@example.com',
            'password': 'secure_password',
            'areas_of_expertise': 'Art, Music',
            'preferred_subjects': 'Painting, Piano'
        })
        with app.app_context():
            user = User.query.filter_by(email='alice@example.com').first()
            self.assertIsNotNone(user)
            self.assertTrue(check_password_hash(user.password_hash, 'secure_password'))
            self.assertFalse(check_password_hash(user.password_hash, 'wrong_password'))

if __name__ == '__main__':
    unittest.main()
