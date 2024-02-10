from django.test import TestCase
from django.urls import reverse

from .forms import UserRegistrationForm
from .models import CustomUser, RegistrationCode
from django.contrib.auth import get_user_model


# The following tests are related to the register_and_login url
class UserRegistrationAndLoginTests(TestCase):
    def test_register_and_login_ordinary_user(self):
        register_response = self.client.post(reverse('register_and_login'), {
            'username': 'ordinaryuser',
            'password': 'testpassword123',
            'role': 'ordinary',
            'action': 'register'
        }, follow=True)

        if not register_response.context['user'].is_authenticated:
            print(register_response.content)

        # Check for registration form errors
        if register_response.context.get('reg_form'):
            print(register_response.context['reg_form'].errors)

        user_exists = get_user_model().objects.filter(username='ordinaryuser').exists()
        self.assertTrue(user_exists, "User registration failed")

        login_response = self.client.post(reverse('register_and_login'), {
            'username': 'ordinaryuser',
            'password': 'testpassword123',
            'action': 'login'
        }, follow=True)

        # Check for login form errors
        if login_response.context.get('login_form'):
            print(login_response.context['login_form'].errors)

        self.assertTrue(login_response.context['user'].is_authenticated, "User login failed")

    def test_register_and_login_shelter_user(self):
        registration_code = RegistrationCode.objects.create(code='sheltercode123', username='shelteruser',
                                                            is_activated=False)
        url = reverse('register_and_login')
        self.client.post(url, {
            'username': 'shelteruser',
            'password': 'testpassword123',
            'role': 'shelter',
            'registration_code': 'sheltercode123',
            'action': 'register'
        })
        user_exists = get_user_model().objects.filter(username='shelteruser').exists()
        code_activated = RegistrationCode.objects.get(code='sheltercode123').is_activated
        self.assertTrue(user_exists)
        self.assertTrue(code_activated)

        response = self.client.post(reverse('register_and_login'), {
            'username': 'shelteruser',
            'password': 'testpassword123',
            'action': 'login'
        }, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)


class UserLoginTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='password123', role='ordinary')

    def test_login_user(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'password123'}, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertRedirects(response, reverse('index'))


class UserRegistrationFormTest(TestCase):
    def test_form_is_valid(self):
        form_data = {
            'username': 'testuser',
            'password': 'testpassword123',
            'role': 'ordinary',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors.as_text())
