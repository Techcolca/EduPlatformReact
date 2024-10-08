import unittest
from app import app, db
from models import User
from werkzeug.security import generate_password_hash, check_password_hash

class TestLogin(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.client = app.test_client()
        with app.app_context():
            db.create_all()
            test_user = User(
                username='testuser',
                email='test@example.com',
                password_hash=generate_password_hash('password123'),
                areas_of_expertise='Testing',
                preferred_subjects='Unit Tests'
            )
            db.session.add(test_user)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_login_page_loads(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    def test_successful_login(self):
        response = self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Logged in successfully', response.data)

    def test_incorrect_password(self):
        response = self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertIn(b'Invalid email or password', response.data)

    def test_non_existent_user(self):
        response = self.client.post('/login', data={
            'email': 'nonexistent@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Invalid email or password', response.data)

    def test_logout(self):
        # First, log in
        self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        
        # Then, log out
        response = self.client.get('/logout', follow_redirects=True)
        self.assertIn(b'Logged out successfully', response.data)

    def test_user_creation(self):
        with app.app_context():
            user = User.query.filter_by(email='test@example.com').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.username, 'testuser')
            self.assertTrue(check_password_hash(user.password_hash, 'password123'))
            self.assertEqual(user.areas_of_expertise, 'Testing')
            self.assertEqual(user.preferred_subjects, 'Unit Tests')

if __name__ == '__main__':
    unittest.main()
