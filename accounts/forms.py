from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import *

class RegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['username','email','role','password1','password2']


class CandidateProfileForm(forms.ModelForm):
    class Meta:
        model = CandidateProfile
        fields = ['skills','education','profile_pic','resume','linkedin_url']

    def clean_resume(self):

        resume = self.cleaned_data.get('resume')

        if resume:

            allowed_types = [
                'application/pdf',

                'application/msword',

                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            ]

            if resume.content_type not in allowed_types:

                raise forms.ValidationError(
                    'Only PDF, DOC and DOCX files are allowed.'
                )

            if resume.size > 5 * 1024 * 1024:

                raise forms.ValidationError(
                    'Resume must be smaller than 5 MB.'
                )

        return resume