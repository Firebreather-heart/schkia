from django.contrib import admin, messages
from django import forms
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import render, redirect, get_object_or_404
from .models import (
    ClassRoom, Subject, AcademicSession, Term, AssessmentArea, AssessmentSection, AssessmentSubArea, StudentResult, Grade
)
from results.models import Student


class AssessmentAreaInline(admin.TabularInline):
    model = AssessmentArea
    extra = 1


class AssessmentSubAreaInline(admin.TabularInline):
    model = AssessmentSubArea
    extra = 1
    verbose_name = 'Manage Items'
    verbose_name_plural = 'Manage_Items'


class GradeInline(admin.TabularInline):
    model = Grade
    extra = 1


class CreateResultsForm(forms.Form):
    term = forms.ModelChoiceField(
        queryset=Term.objects.all(),
        required=True,
        label='Term',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    assessment_section = forms.ModelChoiceField(
        queryset=AssessmentSection.objects.all(),
        required=True,
        label='Assessment Section',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        term_id = kwargs.pop('term_id', None)
        assessment_section_id = kwargs.pop('assessment_section_id', None)
        super().__init__(*args, **kwargs)
        if term_id:
            self.fields['assessment_section'].queryset = AssessmentSection.objects.filter(term_id=term_id)  # type:ignore
        if assessment_section_id:
            self.assessment_areas = AssessmentArea.objects.filter(
                section_id=assessment_section_id)
        else:
            self.assessment_areas = AssessmentArea.objects.none()


class SelectClassForm(forms.Form):
    classroom = forms.ModelChoiceField(
        queryset=ClassRoom.objects.none(),  # Will be customized in __init__
        required=True,
        label='Select Classroom',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        # Allow passing a custom queryset for classrooms
        queryset = kwargs.pop('classroom_queryset', ClassRoom.objects.all())
        super().__init__(*args, **kwargs)
        self.fields['classroom'].queryset = queryset # type:ignore


class SelectStudentForm(forms.Form):
    student = forms.ModelChoiceField(
        queryset=Student.objects.none(),  # Will be customized in __init__
        required=True,
        label='Select Student',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    term = forms.ModelChoiceField(
        queryset=Term.objects.all(),
        required=True,
        label='Select Term',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        # Allow passing a custom queryset for students
        classroom = kwargs.pop('classroom', None)
        super().__init__(*args, **kwargs)

        if classroom:
            self.fields['student'].queryset = Student.objects.filter(classroom=classroom) #type:ignore

class SelectStudentTermForm(forms.Form):
    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        required=True,
        label='Student',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    term = forms.ModelChoiceField(
        queryset=Term.objects.all(),
        required=True,
        label='Term',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(AcademicSession)
class AcademicSessionAdmin(admin.ModelAdmin):
    list_display = ['session']


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ['term', 'session']


class AssessmentSectionForm(forms.ModelForm):
    session = forms.ModelChoiceField(
        queryset=Term.objects.all(), required=True)
    term = forms.ModelChoiceField(queryset=Term.objects.all(), required=True)

    class Meta:
        model = AssessmentSection
        fields = ['name', 'classroom', 'term']


@admin.register(AssessmentSection)
class AssessmentSectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'term', 'classroom')
    search_fields = ('name', 'term__term', 'classroom__name')
    inlines = [AssessmentAreaInline]


@admin.register(AssessmentArea)
class AssessmentAreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'section', 'subject')
    search_fields = ('name', 'section__name', 'subject__name')
    inlines = [AssessmentSubAreaInline]





@admin.register(StudentResult)
class StudentResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'term']
    search_fields = ['student__fullname', 'term__term']
    change_list_template = 'admin/results_changelist.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('select_student_term/',
                 self.admin_site.admin_view(self.select_student_term_view),
                 name='select_student_term'),
            path('select_classroom/',
                 self.admin_site.admin_view(self.select_classroom_view),
                 name='select_classroom'),
            path('select_student/',
                 self.admin_site.admin_view(self.select_student_view),
                 name='select_student'),
            path('create_results/',
                 self.admin_site.admin_view(self.create_results_view),
                 name='create_results'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['select_classroom'] = reverse('admin:select_classroom')
        return super().changelist_view(request, extra_context=extra_context)

    def select_classroom_view(self, request):
        # Custom queryset for classrooms - you can modify this as needed
        # Customize filtering here if required
        classroom_queryset = ClassRoom.objects.filter(
            name__in = ['PG1', 'PG2', 'N1', 'N2'])

        if request.method == 'POST':
            form = SelectClassForm(
                request.POST, classroom_queryset=classroom_queryset)
            if form.is_valid():
                classroom = form.cleaned_data['classroom']
                return redirect(
                    reverse('admin:select_student') +
                    f'?classroom_id={classroom.id}'
                )
        else:
            form = SelectClassForm(classroom_queryset=classroom_queryset)

        context = {
            'form': form,
            'title': 'Select Classroom',
            'opts': StudentResult._meta,
        }
        return render(request, "admin/select_classroom.html", context)
    
    def select_student_view(self, request):
        classroom_id = request.GET.get('classroom_id')
        if not classroom_id:
            messages.error(request, "Please select a classroom first.")
            return redirect(reverse('admin:select_classroom'))

        classroom = get_object_or_404(ClassRoom, id=classroom_id)

        if request.method == 'POST':
            form = SelectStudentForm(
                request.POST, 
                classroom=classroom
            )
            if form.is_valid():
                student = form.cleaned_data['student']
                term = form.cleaned_data['term']
                return redirect(
                    reverse('admin:create_results') + 
                    f'?student_id={student.id}&term_id={term.id}'
                )
        else:
            form = SelectStudentForm(classroom=classroom)

        context = {
            'form': form,
            'classroom': classroom,
            'title': f'Select Student for {classroom.classname()}',
            'opts': StudentResult._meta,
        }
        return render(request, "admin/select_student.html", context)

    def select_student_term_view(self, request):
        if request.method == 'POST':
            form = SelectStudentTermForm(request.POST)
            if form.is_valid():
                student = form.cleaned_data['student']
                term = form.cleaned_data['term']
                # Redirect to results creation page with student and term
                return redirect(
                    reverse('admin:create_results') +
                    f'?student_id={student.id}&term_id={term.id}'
                )
        else:
            form = SelectStudentTermForm()

        context = {
            'form': form,
            'title': 'Select Student and Term',
            'opts': StudentResult._meta,
        }
        return render(request, "admin/select_student_term.html", context)

    def create_results_view(self, request):
        student_id = request.GET.get('student_id')
        term_id = request.GET.get('term_id')

        if not student_id or not term_id:
            messages.info(request, "Please select a student and term first.")
            return redirect(reverse('admin:select_student_term'))

        student = get_object_or_404(Student, id=student_id)
        term = get_object_or_404(Term, id=term_id)

        # Get assessment sections for the student's classroom and term
        assessment_sections = AssessmentSection.objects.filter(
            classroom=student.classroom,
            term=term
        )

        # Prepare data for the template
        assessment_data = []
        for section in assessment_sections:
            section_data = {
                'section_name': section.name,
                'areas': []
            }

            for area in section.assessment_areas.all(): #type:ignore
                area_data = {
                    'area_name': area.name,
                    'subareas': []
                }

                for subarea in area.assessment_subareas.all():
                    area_data['subareas'].append({
                        'subarea': subarea,
                        'grade_options': Grade.ASSESSMENT_OPTIONS
                    })

                section_data['areas'].append(area_data)

            assessment_data.append(section_data)

        if request.method == 'POST':
            # Process form submission
            result = StudentResult.objects.create(
                student=student,
                term=term
            )

            for key, value in request.POST.items():
                if key.startswith('grade_'):
                    subarea_id = key.split('_')[1]
                    subarea = AssessmentSubArea.objects.get(id=subarea_id)

                    Grade.objects.create(
                        grade=value,
                        assessment_sub_area=subarea,
                        student=student,
                        result=result
                    )

            messages.success(request, "Results created successfully.")
            return redirect(reverse('admin:results_studentresult_changelist'))

        context = {
            'student': student,
            'term': term,
            'assessment_data': assessment_data,
            'title': f'Create Results for {student.fullname} - {term}',
            'opts': StudentResult._meta,
            'app_label': 'results',  
            'original': student,
        }
        return render(request, "admin/create_results.html", context)
