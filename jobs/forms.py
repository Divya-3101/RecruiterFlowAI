from django import forms
from .models import Job


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title','company','location','salary','description','required_skills']
    def clean_title(self):

        title = self.cleaned_data.get('title')

        if not title.strip():

            raise forms.ValidationError(
                'Job title cannot be empty.'
            )

        return title

    def clean_salary(self):

        salary = self.cleaned_data.get('salary')

        if salary <= 0:

            raise forms.ValidationError(
                'Salary must be greater than zero.'
            )

        return salary

    def clean_required_skills(self):

        skills = self.cleaned_data.get(
            'required_skills'
        )

        if not skills.strip():

            raise forms.ValidationError(
                'Please enter at least one required skill.'
            )

        return skills