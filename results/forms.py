from django import forms
from .models import AcademicSession, AssessmentSection, Term, Student


class ResultSelectionForm(forms.Form):
    session = forms.ModelChoiceField(
        queryset=AcademicSession.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Select Session'
    )
    term = forms.ModelChoiceField(
        queryset=Term.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Select Term'
    )

    assessment = forms.ModelChoiceField(
        queryset = AssessmentSection.objects.all(),
        widget = forms.Select(attrs={'class': 'form-select'}),
        label='Select Assessment',
    )
    
    child = forms.ModelChoiceField(
        queryset=Student.objects.none(),  # Will be set in the view
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Select Child'
    )

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop('parent', None)
        super(ResultSelectionForm, self).__init__(*args, **kwargs)
        if parent:
            self.fields['child'].queryset = parent.students.all() #type:ignore
