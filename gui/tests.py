from django.test import TestCase
from django.urls import reverse

from .forms import UserRegistrationForm
from .models import CustomUser, RegistrationCode
from django.contrib.auth import get_user_model


class UserRegistrationAndLoginTests(TestCase):
    def setUp(self):
        # This is a code that can be used when a new shelter user is registered
        self.valid_code = RegistrationCode.objects.create(code="validcode123", username="shelteruser", is_activated=False)
        # This is a code which is already activated (meaning that it's invalid and can't be used)
        self.activated_code = RegistrationCode.objects.create(code="activatedcode123", username="shelteruser2", is_activated=True)
        # An existing user is created to test if attempts to create a new user fail
        CustomUser.objects.create_user(username='existinguser', password='testpassword123', role='ordinary')

    def test_register_and_login_ordinary_user(self):
        url = reverse('register_and_login')
        register_response = self.client.post(url, {
            'username': 'ordinaryuser',
            'password': 'testpassword123',
            'role': 'ordinary',
            'action': 'register'
        }, follow=True)

        user_exists = get_user_model().objects.filter(username='ordinaryuser').exists()
        self.assertTrue(user_exists, "User registration failed")

        login_response = self.client.post(reverse('register_and_login'), {
            'username': 'ordinaryuser',
            'password': 'testpassword123',
            'action': 'login'
        }, follow=True)

        self.assertTrue(login_response.context['user'].is_authenticated, "User login failed")

    def test_shelter_registration_with_nonexistent_code(self):
        response = self.client.post(reverse('register_and_login'), {
            'username': 'shelteruser',
            'password': 'testpassword123',
            'role': 'shelter',
            'registration_code': 'nonexistent',
            'action': 'register'
        })
        reg_form = response.context.get('reg_form')

        self.assertFalse(reg_form.is_valid())
        self.assertIn('registration_code', reg_form.errors)
        self.assertEqual(reg_form.errors['registration_code'],
                         ["Invalid registration code for this username or code already activated."])

    def test_shelter_registration_with_activated_code(self):
        response = self.client.post(reverse('register_and_login'), {
            'username': 'shelteruser2',
            'password': 'testpassword123',
            'role': 'shelter',
            'registration_code': self.activated_code.code,
            'action': 'register'
        })
        reg_form = response.context.get('reg_form')

        self.assertFalse(reg_form.is_valid())
        self.assertIn('registration_code', reg_form.errors)
        self.assertEqual(reg_form.errors['registration_code'],
                         ["Invalid registration code for this username or code already activated."])

    def test_shelter_registration_without_code(self):
        response = self.client.post(reverse('register_and_login'), {
            'username': 'shelteruser3',
            'password': 'testpassword123',
            'role': 'shelter',
            'action': 'register'
        })
        reg_form = response.context.get('reg_form')

        self.assertFalse(reg_form.is_valid())
        self.assertIn('registration_code', reg_form.errors)
        self.assertIn("This field is required for shelters.", reg_form.errors['registration_code'])

    def test_register_and_login_shelter_user(self):
        url = reverse('register_and_login')
        self.client.post(url, {
            'username': 'shelteruser',
            'password': 'testpassword123',
            'role': 'shelter',
            'registration_code': 'validcode123',
            'action': 'register'
        })

        user_exists = get_user_model().objects.filter(username='shelteruser').exists()
        code_activated = RegistrationCode.objects.get(code='validcode123').is_activated
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
