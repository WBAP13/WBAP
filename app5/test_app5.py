# test_app5.py

import unittest
from app5 import app, db, User
from werkzeug.security import generate_password_hash

class FlaskAppTestCase(unittest.TestCase):

    # Set up test environment
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_users.db'
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

    # Tear down test environment
    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    # Test 1: Registration route with new user
    def test_register_user(self):
        response = self.client.post('/register', data={
            'username': 'testuser',
            'password': 'testpass'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'WBAP registration successful!', response.data)

    # Test 2: Registration route with existing user
    def test_register_existing_user(self):
        # Create a user directly in the test database
        with app.app_context():
            user = User(username='existinguser', password=generate_password_hash('testpass'))
            db.session.add(user)
            db.session.commit()

        # Try to register the same user
        response = self.client.post('/register', data={
            'username': 'existinguser',
            'password': 'testpass'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Username already exists in WBAP. Try another one.', response.data)

    # Test 3: Login with correct credentials
    def test_login_success(self):
        # Create a user directly in the test database
        with app.app_context():
            user = User(username='testuser', password=generate_password_hash('testpass'))
            db.session.add(user)
            db.session.commit()

        # Attempt to log in with the correct credentials
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'WBAP login successful!', response.data)

    # Test 4: Access home page without login (redirect to login)
    def test_home_redirect_without_login(self):
        response = self.client.get('/home', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please log in to access this page.', response.data)

    # Test 5: Logout after login
    def test_logout(self):
        # Create a user and log them in
        with app.app_context():
            user = User(username='testuser', password=generate_password_hash('testpass'))
            db.session.add(user)
            db.session.commit()

        # Log in
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass'
        }, follow_redirects=True)

        # Log out
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You have been logged out from WBAP.', response.data)

if __name__ == '__main__':
    unittest.main()
