from django import forms


class QuestionSetAddForm(forms.Form):
    title = forms.CharField(min_length=2, max_length=100, strip=True)
    prompt = forms.CharField(min_length=10, max_length=2048, strip=True)
    questions_number = forms.IntegerField(min_value=2, max_value=10, initial=5)
