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

    def test_form_validation_edge_cases(self):
        with app.app_context():
            # Test very long inputs
            form = TeacherRegistrationForm(
                name='A' * 101,
                email='a' * 100 + '@example.com',
                password='A' * 101,
                areas_of_expertise='A' * 1001,
                preferred_subjects='A' * 1001
            )
            self.assertFalse(form.validate())
            self.assertIn('name', form.errors)
            self.assertIn('password', form.errors)

            # Test special characters
            form = TeacherRegistrationForm(
                name='John @#$% Doe',
                email='john@example.com',
                password='secure_password',
                areas_of_expertise='Math, Science!',
                preferred_subjects='Algebra, Physics!'
            )
            self.assertTrue(form.validate())

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
            self.assertEqual(user.username, 'John Doe')
            self.assertEqual(user.areas_of_expertise, 'Math, Science')
            self.assertEqual(user.preferred_subjects, 'Algebra, Physics')

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

    def test_invalid_input_handling(self):
        response = self.client.post('/register', data={
            'name': '',
            'email': 'invalid_email',
            'password': 'short',
            'areas_of_expertise': '',
            'preferred_subjects': ''
        }, follow_redirects=True)
        self.assertIn(b'This field is required', response.data)
        self.assertIn(b'Invalid email address', response.data)
        self.assertIn(b'Field must be at least 6 characters long', response.data)

    def test_flash_messages(self):
        # Test successful registration flash message
        response = self.client.post('/register', data={
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': 'secure_password',
            'areas_of_expertise': 'Math, Science',
            'preferred_subjects': 'Algebra, Physics'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful!', response.data)

        # Test unsuccessful registration flash message
        response = self.client.post('/register', data={
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': 'secure_password',
            'areas_of_expertise': 'Math, Science',
            'preferred_subjects': 'Algebra, Physics'
        }, follow_redirects=True)
        self.assertIn(b'Email already registered', response.data)

    def test_redirect_after_registration(self):
        response = self.client.post('/register', data={
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': 'secure_password',
            'areas_of_expertise': 'Math, Science',
            'preferred_subjects': 'Algebra, Physics'
        }, follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/')

if __name__ == '__main__':
    unittest.main()
