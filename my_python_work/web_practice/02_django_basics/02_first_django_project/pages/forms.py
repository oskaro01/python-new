"""Forms for the pages app."""

from django import forms

from dictionary.models import Category, Word


class WordForm(forms.ModelForm):
    category_name = forms.CharField(
        required=False,
        max_length=60,
        label="Category",
        widget=forms.TextInput(attrs={"placeholder": "vocabulary"}),
    )

    class Meta:
        model = Word
        fields = ["word", "meaning", "example", "focus_first"]
        labels = {
            "focus_first": "Focus first",
        }
        help_texts = {
            "word": "Required. The word you want to remember.",
            "meaning": "Optional for now.",
            "focus_first": "Keep this important daily-use word at the top of your list.",
        }
        widgets = {
            "word": forms.TextInput(attrs={"placeholder": "serene"}),
            "meaning": forms.Textarea(attrs={"rows": 3, "placeholder": "calm and peaceful"}),
            "example": forms.Textarea(attrs={"rows": 3, "placeholder": "The lake was serene."}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if self.instance.pk and self.instance.category:
            self.fields["category_name"].initial = self.instance.category.name

    def clean_word(self):
        word = self.cleaned_data["word"].strip()

        if len(word) < 2:
            raise forms.ValidationError("Use at least 2 characters.")

        return word

    def save(self, commit=True):
        word = super().save(commit=False)
        owner = word.owner or self.user
        category_name = self.cleaned_data["category_name"].strip()

        if category_name and owner:
            category = Category.objects.filter(
                owner=owner,
                name__iexact=category_name,
            ).first()
            if category is None:
                category = Category.objects.create(owner=owner, name=category_name)
            word.category = category
        else:
            word.category = None

        if commit:
            word.save()
        return word


class ImportWordsForm(forms.Form):
    file = forms.FileField(
        help_text="Use a UTF-8 .csv or .json file smaller than 1 MB."
    )
