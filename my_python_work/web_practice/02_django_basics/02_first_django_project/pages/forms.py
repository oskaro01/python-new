"""Forms for the pages app."""

from django import forms


class WordForm(forms.Form):
    word = forms.CharField(
        max_length=80,
        help_text="Required. The word you want to remember.",
        widget=forms.TextInput(attrs={"placeholder": "serene"}),
    )
    meaning = forms.CharField(
        required=False,
        help_text="Optional for now.",
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "calm and peaceful"}),
    )
    example = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "The lake was serene."}),
    )
    category = forms.CharField(
        required=False,
        max_length=60,
        widget=forms.TextInput(attrs={"placeholder": "vocabulary"}),
    )

    def clean_word(self):
        word = self.cleaned_data["word"].strip()

        if len(word) < 2:
            raise forms.ValidationError("Use at least 2 characters.")

        return word

