from django import forms
from .models import Application


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter', 'resume']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Explain why you are a great fit for this position...'
            }),
            'resume': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            }),
        }

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            allowed_types = [
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/octet-stream',  # Some browsers send octet-stream for docx
            ]
            # Also validate file extension
            import os
            ext = os.path.splitext(resume.name)[1].lower()
            if ext not in ['.pdf', '.doc', '.docx']:
                raise forms.ValidationError('Only PDF, DOC and DOCX files are allowed.')

            max_size = 5 * 1024 * 1024
            if resume.size > max_size:
                raise forms.ValidationError('Resume must be smaller than 5 MB.')

        return resume


class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'})
        }