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
        self.client.post(url, {
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


class DogAdoptionPostCreateTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='shelteruser', password='123456', role='shelter')
        self.shelter = Shelter.objects.get(user=self.user)

    def test_create_post_as_shelter_user(self):
        self.client.login(username='shelteruser', password='123456')
        self.client.post(reverse('create_post'), {
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
        get_user_model().objects.create_user(username='ordinaryuser', password='123456',
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


class DogAdoptionPostEditTests(TestCase):

    def setUp(self):
        self.shelter_user = get_user_model().objects.create_user(username='shelteruser', password='123456',
                                                                 role='shelter')
        self.shelter = Shelter.objects.get(user=self.shelter_user)
        self.other_shelter_user = get_user_model().objects.create_user(username='othershelteruser',
                                                                       password='123456', role='shelter')
        self.ordinary_user = get_user_model().objects.create_user(username='ordinaryuser', password='123456',
                                                                  role='ordinary')

        self.post = DogAdoptionPost.objects.create(name="kuchence", age=1, gender="male", breed="ulichna prevuzhodna",
                                                   description="mqu",
                                                   shelter=Shelter.objects.get(user=self.shelter_user), size="XS")

    def test_edit_post_as_creator_with_valid_changes(self):
        self.client.login(username='shelteruser', password='123456')
        post_edit_url = reverse('edit_post', kwargs={'pk': self.post.pk})
        response = self.client.post(post_edit_url, {
            'name': 'novo ime',
            'age': 29922,
            'gender': 'female',
            'breed': 'kotence',
            'description': 'malak pisan',
            'size': 'XL',
        }, follow=True)
        self.post.refresh_from_db()
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(self.post.name, 'novo ime')
        self.assertEqual(self.post.age, 29922)

    def test_edit_post_as_creator_with_invalid_field(self):
        self.client.login(username='shelteruser', password='123456')
        post_edit_url = reverse('edit_post', kwargs={'pk': self.post.pk})
        response = self.client.post(post_edit_url, {
            'name': 'novo ime',
            'age': 'dieset',
            'gender': 'female',
            'breed': 'kotence',
            'description': 'malak pisan',
            'size': 'XL',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIn('age', form.errors)
        self.assertEqual(form.errors['age'], ['Enter a whole number.'])

    def test_edit_post_as_creator_with_missing_field(self):
        self.client.login(username='shelteruser', password='123456')
        post_edit_url = reverse('edit_post', kwargs={'pk': self.post.pk})
        response = self.client.post(post_edit_url, {
            # 'age' field is left empty
            'name': 'novo ime',
            'gender': 'female',
            'breed': 'kotence',
            'description': 'malak pisan',
            'size': 'XL',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue('age' in response.context['form'].errors)

    def test_edit_post_as_other_shelter_user(self):
        self.client.login(username='othershelteruser', password='123456')
        post_edit_url = reverse('edit_post', kwargs={'pk': self.post.pk})
        response = self.client.get(post_edit_url)
        self.assertNotEqual(response.status_code, 200)

    def test_edit_post_as_ordinary_user(self):
        self.client.login(username='ordinaryuser', password='123456')
        post_edit_url = reverse('edit_post', kwargs={'pk': self.post.pk})
        response = self.client.get(post_edit_url)
        self.assertNotEqual(response.status_code, 200)


class PostDeletionTests(TestCase):

    def setUp(self):
        self.shelter1 = get_user_model().objects.create_user(username='shelter1', password='123456',
                                                             role='shelter')
        self.shelter2 = get_user_model().objects.create_user(username='shelter2', password='123456',
                                                             role='shelter')

        self.ordinary_user = get_user_model().objects.create_user(username='ordinaryuser', password='123456',
                                                                  role='ordinary')

        self.post = DogAdoptionPost.objects.create(name="doggo", age=7, gender="male", breed="poroda",
                                                   description="dobro momche po princip ne hape mnogo",
                                                   shelter=Shelter.objects.get(user=self.shelter1), size="M")

        self.delete_url = reverse('delete_post', kwargs={'post_id': self.post.id})

    def test_shelter_user_delete_own_post(self):
        self.client.login(username='shelter1', password='123456')
        response = self.client.post(self.delete_url)
        self.assertRedirects(response, reverse('index'))
        self.assertFalse(DogAdoptionPost.objects.filter(id=self.post.id).exists())

    def test_ordinary_user_cannot_delete_post(self):
        self.client.login(username='ordinaryuser', password='123456')
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(DogAdoptionPost.objects.filter(id=self.post.id).exists())

    def test_cannot_delete_another_shelters_post(self):
        self.client.login(username='shelter2', password='123456')
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(DogAdoptionPost.objects.filter(id=self.post.id).exists())

    def test_redirect_after_delete(self):
        self.client.login(username='shelter1', password='123456')
        response = self.client.post(self.delete_url, follow=True)
        self.assertRedirects(response, reverse('index'))


class ShelterProfileEditTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='shelter1', password='123456', role='shelter')
        self.shelter = Shelter.objects.get(user=self.user)
        self.edit_url = reverse('edit_shelter', kwargs={'pk': self.shelter.pk})

    def test_shelter_can_edit_profile(self):
        self.client.login(username='shelter1', password='123456')
        response = self.client.post(self.edit_url, {
            'name': 'new name',
            'working_hours': '9-17',
            'phone': '01234',
            'address': 'new address',
            'latitude': 2.4,
            'longitude': 4.5
        })
        self.shelter.refresh_from_db()
        if response.status_code != 302:
            print(response.context['form'].errors)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.shelter.name, 'new name')
        self.assertEqual(self.shelter.working_hours, '9-17')
        self.assertEqual(self.shelter.phone, '01234')
        self.assertEqual(self.shelter.address, 'new address')
        self.assertEqual(self.shelter.latitude, 2.4)
        self.assertEqual(self.shelter.longitude, 4.5)

    def test_cannot_edit_profile_ordinary(self):
        get_user_model().objects.create_user(username='evil', password='666')
        self.client.login(username='evil', password='666')
        response = self.client.post(self.edit_url, {'name': 'hehehehehehee'})
        self.shelter.refresh_from_db()
        self.assertNotEqual(self.shelter.name, 'hehehehehehee')
        self.assertNotEqual(response.status_code, 302)

    def test_cannot_edit_profile_shelter(self):
        get_user_model().objects.create_user(username='evil_shelter', password='666', role='shelter')
        self.client.login(username='evil_shelter', password='666')
        response = self.client.post(self.edit_url, {'name': 'hehehehehehee'})
        self.shelter.refresh_from_db()
        self.assertNotEqual(self.shelter.name, 'hehehehehehee')
        self.assertNotEqual(response.status_code, 302)

    def test_shelter_edit_invalid_form(self):
        self.client.login(username='shelter1', password='123456')
        response = self.client.post(self.edit_url, {
            'name': 'new name',
            'working_hours': '9-17',
            'phone': '01234',
            'address': 'new address',
            'longitude': 4.5
        })
        self.shelter.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        form_errors = response.context['form'].errors
        self.assertIn('latitude', form_errors)
        self.assertIn('This field is required.', form_errors['latitude'])

    def test_edit_without_login(self):
        response = self.client.get(self.edit_url, follow=True)
        expected_login_url = reverse('register_and_login') + f"?next={self.edit_url}"
        self.assertRedirects(response, expected_login_url)

    def test_response_and_redirect_after_successful_edit(self):
        self.client.login(username='shelter1', password="123456")
        response = self.client.post(self.edit_url, {
            'name': 'new name',
            'working_hours': '9-17',
            'phone': '1111',
            'address': 'new address',
            'latitude': 30.0,
            'longitude': 40.0,
        }, follow=True)
        self.shelter.refresh_from_db()

        self.assertRedirects(response, reverse('index'))
        self.assertEqual(self.shelter.name, 'new name')

