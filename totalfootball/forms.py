from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from .models import User, Player, Team, League

class LoginForm(forms.Form):
    username = forms.CharField(label='', max_length=20, widget=forms.TextInput(attrs={'placeholder': 'username'}))
    password = forms.CharField(label='', max_length=200, widget=forms.PasswordInput(attrs={'placeholder': 'password'}))

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("Invalid username/password")

        # We must return the cleaned data we got from our parent.
        return cleaned_data

class RegisterForm(forms.Form):
    username      = forms.CharField(label='', max_length=20, widget=forms.TextInput(attrs={'id': 'id_username', 'placeholder': 'username'}))
    password1     = forms.CharField(label='', max_length=20, widget=forms.PasswordInput(attrs={'id': 'id_password', 'placeholder': 'password'}))
    password2     = forms.CharField(label='', max_length=20, widget=forms.PasswordInput(attrs={'id': 'id_confirm_password', 'placeholder': 'confirm password'}))
    email         = forms.CharField(label='', max_length=40, widget = forms.EmailInput(attrs={'id': 'id_email', 'placeholder': 'email'}))
    first_name     = forms.CharField(label='', max_length=20, widget=forms.TextInput(attrs={'id': 'id_first_name', 'placeholder': 'first name'}))
    last_name      = forms.CharField(label='', max_length=200, widget=forms.TextInput(attrs={'id': 'id_last_name', 'placeholder': 'last name'}))


    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords did not match.")

        # We must return the cleaned data we got from our parent.
        return cleaned_data

    # Customizes form validation for the username field.
    def clean_username(self):
        # Confirms that the username is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")

        # We must return the cleaned data we got from the cleaned_data
        # dictionary
        return username
        
class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['team_name', 'profile_image']
        widgets = {
            'team_name': forms.Textarea(attrs={'id':'id_bio_input_text', 'rows':'3'}),
            'profile_image': forms.FileInput(attrs={'id':'id_profile_picture'})
        }
        labels = {
            'team_name': "",
            'profile_image': "Upload image"
        }

class LineupSelectionForm(forms.ModelForm):
    players = forms.ModelMultipleChoiceField(
        queryset=Player.objects.none(),  # Start empty
        widget=forms.CheckboxSelectMultiple(),
        label="Select Your Starting 11 Players"
    )

    captain = forms.ModelChoiceField(
        queryset=Player.objects.none(),  # Start empty
        label="Select Your Captain",
        required=True
    )

    class Meta:
        model = Team
        fields = ['players', 'captain']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set the queryset dynamically
        player_queryset = Player.objects.order_by('position', 'name')
        self.fields['players'].queryset = player_queryset
        self.fields['captain'].queryset = player_queryset

    def clean(self):
        cleaned_data = super().clean()
        players = cleaned_data.get('players')
        captain = cleaned_data.get('captain')

        if players and len(players) != 11:
            raise forms.ValidationError("You must select exactly 11 players.")

        if captain and captain not in players:
            raise forms.ValidationError("The captain must be one of the selected players.")

        return cleaned_data
    
class CreateLeagueForm(forms.ModelForm):
    class Meta:
        model = League
        fields = ['name']

class JoinLeagueForm(forms.Form):
    code = forms.UUIDField(help_text="Enter the unique code to join a league.")