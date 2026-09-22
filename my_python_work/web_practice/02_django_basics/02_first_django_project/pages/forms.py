"""Forms for the pages app."""

from django import forms

from dictionary.models import Word


class WordForm(forms.ModelForm):
    class Meta:
        model = Word
        fields = ["word", "meaning", "example", "category"]
        help_texts = {
            "word": "Required. The word you want to remember.",
            "meaning": "Optional for now.",
        }
        widgets = {
            "word": forms.TextInput(attrs={"placeholder": "serene"}),
            "meaning": forms.Textarea(attrs={"rows": 3, "placeholder": "calm and peaceful"}),
            "example": forms.Textarea(attrs={"rows": 3, "placeholder": "The lake was serene."}),
            "category": forms.TextInput(attrs={"placeholder": "vocabulary"}),
        }

    def clean_word(self):
        word = self.cleaned_data["word"].strip()

        if len(word) < 2:
            raise forms.ValidationError("Use at least 2 characters.")

        return word
