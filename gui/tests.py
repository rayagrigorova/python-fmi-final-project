from django.test import TestCase
from django.urls import reverse

from .forms import UserRegistrationForm
from .models import CustomUser, RegistrationCode, DogAdoptionPost, Shelter
from django.contrib.auth import get_user_model


class UserRegistrationAndLoginTests(TestCase):
    def setUp(self):
        # This is a code that can be used when a new shelter user is registered
        self.valid_code = RegistrationCode.objects.create(code="validcode123", username="shelteruser",
                                                          is_activated=False)
        # This is a code which is already activated (meaning that it's invalid and can't be used)
        self.activated_code = RegistrationCode.objects.create(code="activatedcode123", username="shelteruser2",
                                                              is_activated=True)
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

    def test_shelter_registration_with_code_belonging_to_other(self):
        response = self.client.post(reverse('register_and_login'), {
            'username': 'not_shelteruser2',
            'password': '123456',
            'role': 'shelter',
            'registration_code': self.valid_code.code,
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

    def test_shelter_registration_with_existing_username(self):
        valid_code_for_existing_user = RegistrationCode.objects.create(code="code123456", username="existinguser",
                                                                       is_activated=False)
        response = self.client.post(reverse('register_and_login'), {
            'username': 'existinguser',
            'password': 'testpassword123',
            'role': 'shelter',
            'registration_code': valid_code_for_existing_user.code,
            'action': 'register'
        })
        reg_form = response.context.get('reg_form')

        self.assertFalse(reg_form.is_valid())
        self.assertIn('username', reg_form.errors)
        self.assertEqual(reg_form.errors['username'], ["A user with that username already exists."])

    def test_ordinary_user_login_nonexistent_username(self):
        response = self.client.post(reverse('login'), {
            'username': 'nonexistent',
            'password': '123456',
        })
        self.assertEqual(response.context['form'].non_field_errors(),
                         ['Please enter a correct username and password. Note that both fields may be case-sensitive.'])

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

    def test_login_user_wrong_password(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'wrong_password1234'},
                                    follow=True)
        form = response.context.get('form')
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertTrue(form.errors)
        self.assertIn("Please enter a correct username and password.", str(form.errors))

    def test_login_user_nonexistent_profile(self):
        response = self.client.post(reverse('login'), {'username': 'nonexistent', 'password': '123456'}, follow=True)
        form = response.context.get('form')
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertTrue(form.errors)
        self.assertIn("Please enter a correct username and password.", str(form.errors))


class UserRegistrationFormTest(TestCase):
    def test_form_is_valid(self):
        form_data = {
            'username': 'testuser',
            'password': 'testpassword123',
            'role': 'ordinary',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors.as_text())


class DogAdoptionPostTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='shelteruser', password='123456', role='shelter')
        self.shelter = Shelter.objects.get(user=self.user)

    def test_create_post_as_shelter_user(self):
        self.client.login(username='shelteruser', password='123456')
        response = self.client.post(reverse('create_post'), {
            'name': 'kucho',
            'age': 927372,
            'gender': 'male',
            'breed': 'nqma',
            'description': 'bez komentar',
            'size': 'XL',
            'shelter': self.shelter.id
        }, follow=True)

        self.assertEqual(DogAdoptionPost.objects.count(), 1)
        self.assertEqual(DogAdoptionPost.objects.first().name, 'kucho')

    def test_create_post_as_non_shelter_user(self):
        ordinary_user = get_user_model().objects.create_user(username='ordinaryuser', password='123456',
                                                             role='ordinary')
        self.client.login(username='ordinaryuser', password='123456')
        response = self.client.post(reverse('create_post'), {
            'name': 'kucho',
            'age': 927372,
            'gender': 'male',
            'breed': 'nqma',
            'description': 'bez komentar',
            'size': 'XL',
            'shelter': self.shelter.id
        }, follow=True)
        self.assertRedirects(response, reverse('index'))
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You do not have permission to create a post.")
        self.assertEqual(DogAdoptionPost.objects.count(), 0)

    def test_create_post_form_validation(self):
        self.client.login(username='shelteruser', password='123456')
        # The required field 'age' is missing
        response = self.client.post(reverse('create_post'), {
            'name': 'kucho',
            'gender': 'male',
            'breed': 'nqma',
            'description': 'bez komentar',
            'size': 'XL',
            'shelter': self.shelter.id
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("This field is required.", str(response.context['form']))
