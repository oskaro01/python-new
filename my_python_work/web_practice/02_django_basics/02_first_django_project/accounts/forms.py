from django.contrib.auth.forms import UserCreationForm


class RegisterForm(UserCreationForm):
    """Django's secure registration form with clearer help text."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].help_text = "Letters, numbers, and @/./+/-/_ only."
