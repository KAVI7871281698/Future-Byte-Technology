from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class AuthViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = "testuser"
        self.email = "testuser@example.com"
        self.password = "SecurePass123!"
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password,
            first_name="Test"
        )

    def test_login_page_renders_successfully(self):
        """Verify the login UI loads with 200 OK and uses the correct template."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myapp/login.html')
        self.assertContains(response, 'FutureByte')
        self.assertContains(response, 'Welcome back')

    def test_login_success(self):
        """Verify valid credentials log the user in and redirect to home."""
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password,
        })
        self.assertRedirects(response, reverse('home'))

    def test_login_failure_invalid_password(self):
        """Verify invalid credentials display an error message and do not authenticate."""
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': 'WrongPassword123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myapp/login.html')
        self.assertContains(response, 'Invalid username or password')

    def test_signup_page_renders_successfully(self):
        """Verify the signup UI loads with 200 OK."""
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myapp/signup.html')
        self.assertContains(response, 'Create an account')

    def test_signup_success(self):
        """Verify new user registration creates a user and redirects to home."""
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'NewPassword123!',
            'confirm_password': 'NewPassword123!',
        })
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_signup_mismatched_passwords(self):
        """Verify validation catches mismatched passwords."""
        response = self.client.post(reverse('signup'), {
            'username': 'anotheruser',
            'email': 'another@example.com',
            'password': 'PasswordOne123!',
            'confirm_password': 'PasswordTwo123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Passwords do not match')

    def test_home_page_requires_login(self):
        """Verify unauthenticated requests to the dashboard are redirected to login."""
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('home')}")

    def test_home_page_accessible_when_authenticated(self):
        """Verify logged in users can view the dashboard."""
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myapp/home.html')
        self.assertContains(response, self.username)

    def test_logout_redirects_to_login(self):
        """Verify logging out ends session and redirects to login."""
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
