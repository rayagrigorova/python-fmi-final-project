from django.contrib.auth import get_user_model
from django import forms
from .models import RegistrationCode, DogAdoptionPost, Shelter, Comment


class UserRegistrationForm(forms.ModelForm):
    # widget=forms.PasswordInput() specifies the widget to use for rendering the field in HTML
    # PasswordInput() is used, which renders the characters in the field as '****'
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        # This form will use the custom user model defined in models.py
        model = get_user_model()
        fields = ['username', 'password', 'role', 'registration_code']

    # Provide custom validation for this form by overriding the clean() method.
    def clean(self):
        # Call the parent method to ensure basic validation logic
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        username = cleaned_data.get('username')
        registration_code = cleaned_data.get('registration_code')

        if role == 'shelter':
            if registration_code:
                try:
                    RegistrationCode.objects.get(code=registration_code, username=username,
                                                 is_activated=False)
                except RegistrationCode.DoesNotExist:
                    self.add_error('registration_code',
                                   "Invalid registration code for this username or code already activated.")
            else:
                self.add_error('registration_code', "This field is required for shelters.")

        return cleaned_data


class DogAdoptionPostForm(forms.ModelForm):
    class Meta:
        model = DogAdoptionPost
        fields = ['name', 'age', 'gender', 'breed', 'description', 'image', 'size', 'adoption_stage']


class ShelterForm(forms.ModelForm):
    class Meta:
        model = Shelter
        fields = ['name', 'working_hours', 'phone', 'address', 'latitude', 'longitude']
        #  The 'widgets' attribute in the Meta class allows customization of
        #  how each form field is rendered in the form (in this case, I have set the precision to 7 decimal places)
        widgets = {
            'latitude': forms.NumberInput(attrs={'step': '0.0000001'}),
            'longitude': forms.NumberInput(attrs={'step': '0.0000001'}),
        }


class SortFilterForm(forms.Form):
    shelter = forms.ModelChoiceField(queryset=Shelter.objects.all(), required=False, empty_label="All Shelters")
    size = forms.ChoiceField(choices=[('', 'All')] + DogAdoptionPost.SIZE_CHOICES, required=False)
    breed = forms.ChoiceField(choices=[], required=False)  # The choices for this field will be initialized in __init__
    gender = forms.ChoiceField(choices=[('', 'All'), ('male', 'Male'), ('female', 'Female')], required=False)
    sort_by = forms.ChoiceField(choices=[('name', 'Name'), ('age', 'Age'), ('size', 'Size')], required=False)

    def __init__(self, *args, **kwargs):
        super(SortFilterForm, self).__init__(*args, **kwargs)
        # Get the unique breeds from dog adoption posts (flat=True is used so the data is not returned as
        # tuples of only one element like so: [('breed1',)...('breedN',)])
        unique_breeds = DogAdoptionPost.objects.values_list('breed', flat=True).distinct()
        self.fields['breed'].choices = [('', 'All')] + [(breed, breed) for breed in unique_breeds if breed]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
