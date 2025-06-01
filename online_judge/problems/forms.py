from django import forms
from .models import Problem , Submission

class ProblemForm(forms.ModelForm):
    raw_inputs = forms.CharField(widget=forms.Textarea, required=False, help_text="One test case input per line.")
    raw_outputs = forms.CharField(widget=forms.Textarea, required=False, help_text="One expected output per line.")
    class Meta:
        model = Problem
        exclude = ['created_by', 'problem_statistics', 'isSolved','testcases']

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['code', 'language']
        widgets = {
            'code': forms.Textarea(attrs={'rows': 10, 'cols': 80}),
            'language': forms.Select(),
        }

