import json
from django.contrib import admin, messages
from django import forms
from django.db import IntegrityError
from django.http import JsonResponse
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import render, redirect, get_object_or_404
from .models import (
    ClassRoom, ResultGeneration, Subject, AcademicSession, Term, AssessmentArea, AssessmentSection, AssessmentSubArea, StudentResult, Grade, GradeType, Teacher, Student
)


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
            self.fields['assessment_section'].queryset = AssessmentSection.objects.filter(
                term_id=term_id)  # type:ignore
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
        self.fields['classroom'].queryset = queryset  # type:ignore


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
            self.fields['student'].queryset = Student.objects.filter(  # type:ignore
                classroom=classroom)


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
        # Allow passing a custom queryset for students
        classroom = kwargs.pop('classroom', None)
        super().__init__(*args, **kwargs)

        if classroom:
            self.fields['student'].queryset = Student.objects.filter(  # type:ignore
                classroom=classroom)


@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['name', 'classroom', 'get_teacher_type_display']
    search_fields = ['name', 'classroom']
    list_filter = ['classroom']
    ordering = ['name']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'classroom']
    list_filter = ['classroom']


@admin.register(AcademicSession)
class AcademicSessionAdmin(admin.ModelAdmin):
    list_display = ['session']


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ['term', 'session']


@admin.register(GradeType)
class GradeTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'label', 'is_default']
    search_fields = ['code', 'label']
    ordering = ['code']

    def save_model(self, request, obj, form, change):
        # If this is marked as default, remove default from others
        if obj.is_default:
            GradeType.objects.filter(is_default=True).update(is_default=False)
        super().save_model(request, obj, form, change)


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
    list_filter = ('term', 'classroom')
    search_fields = ('name', 'term__term', 'classroom__name')
    inlines = [AssessmentAreaInline]


@admin.register(AssessmentArea)
class AssessmentAreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'section', 'subject')
    list_filter = ('section', 'subject__classroom')
    search_fields = ('name', 'section__name', 'subject__name')
    inlines = [AssessmentSubAreaInline]


@admin.register(StudentResult)
class StudentResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'term', 'student__classroom', 'section']
    search_fields = ['student__fullname', 'term__term', 'section__name']
    list_filter = ['term__term', 'student__classroom', 'section']
    change_list_template = 'admin/results_changelist.html'

    def get_grade_choices(self):
        return GradeType.get_choices()

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
            path('<path:object_id>/detail/',
                 self.admin_site.admin_view(self.result_detail_view),
                 name='studentresult_detail'),
            path('update_grade/',
                 self.admin_site.admin_view(self.update_grade),
                 name='update_grade'),
            path('select_assessment_section/',
                 self.admin_site.admin_view(
                     self.select_assessment_section_view),
                 name='select_assessment_section'),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['select_classroom'] = reverse('admin:select_classroom')
        return super().changelist_view(request, extra_context=extra_context)

    def select_classroom_view(self, request):
        classroom_queryset = ClassRoom.objects.filter(
            name__in=['PG1', 'PG2', 'N1', 'N2'])

        if request.method == 'POST':
            form = SelectClassForm(
                request.POST, classroom_queryset=classroom_queryset)
            if form.is_valid():
                classroom = form.cleaned_data['classroom']
                return redirect(
                    reverse('admin:select_student_term') +
                    f'?classroom_id={classroom.id}'
                )
        else:
            form = SelectClassForm(classroom_queryset=classroom_queryset)

        context = {
            'form': form,
            'title': 'Select Classroom',
            'opts': StudentResult._meta,
        }
        context = dict(
            self.admin_site.each_context(request),
            **context
        )
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
                    reverse('admin:select_assessment_section')
                )
        else:
            form = SelectStudentForm(classroom=classroom)

        context = {
            'form': form,
            'classroom': classroom,
            'title': f'Select Student for {classroom.classname()}',
            'opts': StudentResult._meta,
        }
        context = dict(
            self.admin_site.each_context(request),
            **context
        )
        return render(request, "admin/select_student.html", context)

    def select_student_term_view(self, request):
        classroom_id = request.GET.get('classroom_id')
        if not classroom_id:
            messages.error(request, "Please select a classroom first.")
            return redirect(reverse('admin:select_classroom'))

        classroom = get_object_or_404(ClassRoom, id=classroom_id)
        if request.method == 'POST':
            form = SelectStudentTermForm(request.POST)
            if form.is_valid():
                student = form.cleaned_data['student']
                term = form.cleaned_data['term']
                # Redirect to results creation page with student and term
                return redirect(
                    reverse('admin:select_assessment_section') +
                    f'?student_id={student.id}&term_id={term.id}'
                )
        else:
            form = SelectStudentTermForm(classroom=classroom)

        context = {
            'form': form,
            'title': 'Select Student and Term',
            'opts': StudentResult._meta,
        }
        context = dict(
            self.admin_site.each_context(request),
            **context
        )
        return render(request, "admin/select_student_term.html", context)

    def select_assessment_section_view(self, request):
        student_id = request.GET.get('student_id')
        term_id = request.GET.get('term_id')

        if not student_id or not term_id:
            messages.error(request, "Please select a student and term first.")
            return redirect('admin:select_student_term')

        student = get_object_or_404(Student, id=student_id)
        term = get_object_or_404(Term, id=term_id)

        if request.method == 'POST':
            section_id = request.POST.get('assessment_section')
            if section_id:
                return redirect(
                    reverse('admin:create_results') + 
                    f'?student_id={student_id}&term_id={term_id}&section_id={section_id}'
                )

        assessment_sections = AssessmentSection.objects.filter(
            classroom=student.classroom,
            term=term
        )

        context = {
            'title': f'Select Assessment Section for {student.fullname}',
            'student': student,
            'term': term,
            'assessment_sections': assessment_sections,
            'opts': self.model._meta,
        }
        context = dict(
            self.admin_site.each_context(request),
            **context
        )
        return render(request, 'admin/select_assessment_section.html', context)

    def create_results_view(self, request):
        student_id = request.GET.get('student_id')
        term_id = request.GET.get('term_id')
        section_id = request.GET.get('section_id')

        if not all([student_id, term_id, section_id]):
            messages.error(request, "Missing required parameters")
            return redirect('admin:select_student')

        student = get_object_or_404(Student, id=student_id)
        term = get_object_or_404(Term, id=term_id)
        section = get_object_or_404(AssessmentSection, id=section_id)

        assessment_data = []
        section_data = {
            'section_name': section.name,
            'areas': []
        }

        for area in section.assessment_areas.all():  # type:ignore
            area_data = {
                'id': area.id,
                'area_name': area.name,
                'subareas': []
            }

            for subarea in area.assessment_subareas.all():
                area_data['subareas'].append({
                    'subarea': subarea,
                    'grade_options': Grade.DEFAULT_GRADES
                })

            section_data['areas'].append(area_data)

        assessment_data.append(section_data)

        if request.method == 'POST':
            # Process form submission
            result = StudentResult.objects.create(
                student=student,
                term=term,
                section=section,
            )

            for key, value in request.POST.items():
                if key.startswith('grade_') and value:
                    try:
                        subarea_id = int(key.split('_')[1])
                        subarea = AssessmentSubArea.objects.get(id=subarea_id)
                        grade_type = GradeType.objects.get(code=value)
                        grade, created = Grade.objects.get_or_create(
                            grade=grade_type,
                            assessment_sub_area=subarea,
                            student=student,
                            result=result
                        )
                    except (ValueError, AssessmentSubArea.DoesNotExist, IntegrityError) as e:
                        messages.error(
                            request, f"Error creating grade for {subarea.name}")

                elif key.startswith('comment_') and value:
                    try:
                        area_id = int(key.split('_')[1])
                        area = AssessmentArea.objects.get(id=area_id)
                        area.teacher_comment = value
                        area.save()
                    except (ValueError, AssessmentArea.DoesNotExist) as e:
                        print(e)
                        messages.error(
                            request, f"Error saving comment for {area.name}")

            messages.success(request, "Results created successfully.")
            return redirect(reverse('admin:results_studentresult_changelist'))

        context = {
            'student': student,
            'term': term,
            'assessment_data': assessment_data,
            'title': f'Create Results for {student.fullname} - {term} - {section.name}',
            'opts': StudentResult._meta,
            'app_label': 'results',
            'original': student,
        }
        context = dict(
            self.admin_site.each_context(request),
            **context
        )
        context.update({
            'grade_choices': self.get_grade_choices(),
        })
        return render(request, "admin/create_results.html", context)

    def result_detail_view(self, request, object_id):
        # Get the specific StudentResult object
        result = get_object_or_404(StudentResult, pk=object_id)

        section_id = request.GET.get('section_id')
        if section_id:
            section = get_object_or_404(AssessmentSection, id=section_id)
        else:
            section = AssessmentSection.objects.filter(
                classroom=result.student.classroom,
                term=result.term
            ).first()

        if not section:
            messages.error(request, "No assessment section found")
            return redirect('admin:results_studentresult_changelist')

        structured_data = []

        for area in section.assessment_areas.all():  # type:ignore
            area_data = {
                'name': area.name,
                'subject': area.subject.name,
                'teacher_comment': area.teacher_comment,
                'id': area.id,
                'sub_areas': []
            }

            for sub_area in area.assessment_subareas.all():
                grade = Grade.objects.filter(
                    assessment_sub_area=sub_area,
                    student=result.student,
                    result=result
                ).first()

                sub_area_data = {
                    'name': sub_area.name,
                    'id': sub_area.id,
                    'grade': grade.grade if grade else None,
                    'grade_display': grade.grade.label if grade else 'Not Graded',  # type:ignore
                    'grade_options': Grade.DEFAULT_GRADES
                }
                area_data['sub_areas'].append(sub_area_data)

            structured_data.append(area_data)
        context = dict(
            self.admin_site.each_context(request),
            result=result,
            student=result.student,
            term=result.term,
            assessment_data=structured_data,
            title=f'{section.name} Result',
            opts=self.model._meta,
            app_label=self.model._meta.app_label,
            has_view_permission=self.has_view_permission(request, result),
        )
        return render(request, "admin/result_detail.html", context)

    def update_grade(self, request):
        if request.method == 'POST':
            data = json.loads(request.body)
            result_id = data.get('result_id')

            try:
                result = StudentResult.objects.get(id=result_id)

                # Handle grade updates
                if 'subarea_id' in data and 'grade' in data:
                    subarea_id = data.get('subarea_id')
                    grade_value = data.get('grade')
                    subarea = AssessmentSubArea.objects.get(id=subarea_id)
                    grade_type = GradeType.objects.get(code=grade_value) 
                    grade, created = Grade.objects.update_or_create(
                        assessment_sub_area=subarea,
                        student=result.student,
                        result=result,
                        defaults={'grade': grade_type}
                    )

                # Handle teacher comments
                if 'teacher_comment' in data and 'area_id' in data:
                    area_id = data.get('area_id')
                    comment = data.get('teacher_comment')
                    area = AssessmentArea.objects.get(id=area_id)
                    area.teacher_comment = comment
                    area.save()

                # Handle head teacher comment
                if 'head_teacher_comment' in data:
                    result.head_teacher_comment = data.get(
                        'head_teacher_comment')
                    result.save()

                if 'teacher_general_comment' in data:
                    result.teacher_general_comment = data.get(
                        'teacher_general_comment')
                    result.save()

                return JsonResponse({
                    'success': True,
                    'message': 'Updates saved successfully'
                })

            except (StudentResult.DoesNotExist, AssessmentSubArea.DoesNotExist, AssessmentArea.DoesNotExist) as e:
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                }, status=400)

        return JsonResponse({
            'success': False,
            'message': 'Invalid request method'
        }, status=405)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_detail_link'] = True
        extra_context['detail_link'] = reverse(  # type:ignore
            'admin:studentresult_detail',
            args=[object_id])
        return super().change_view(request, object_id, form_url, extra_context)


@admin.register(ResultGeneration)
class ResultGenerationAdmin(admin.ModelAdmin):
    # change_list_template = "admin/results/resultgeneration_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('generate-result/',
                 self.admin_site.admin_view(self.generate_results_view),
                 name='generate_result'),
            path("show-results/", self.admin_site.admin_view(self.show_results_view),
                 name="show_results"),
            path('get-classrooms/<int:session_id>/<int:term_id>/',
                 self.admin_site.admin_view(self.get_classrooms),
                 name='get_classrooms'),
            path('get-students/<int:classroom_id>/',
                 self.admin_site.admin_view(self.get_students),
                 name='get_students'),
            path('save-grade/',
                 self.admin_site.admin_view(self.save_grade),
                 name='save_grade'),
        ]
        return custom_urls + urls

    def generate_results_view(self, request):
        context = {
            'title': 'Generate Results',
            'sessions': AcademicSession.objects.all(),
            'terms': Term.objects.all(),
            'opts': self.model._meta,
            **self.admin_site.each_context(request),
        }
        return render(request, 'admin/results/generate_results.html', context)

    def show_results_view(self, request):
        """
        Processes the selected parameters and displays the generated results.
        """
        session_id = request.GET.get('session')
        term_id = request.GET.get('term')
        classroom_id = request.GET.get('classroom')
        student_id = request.GET.get('student')

        if not all([session_id, term_id, classroom_id, student_id]):
            messages.error(
                request, "All fields are required to generate results.")
            return redirect(reverse('admin:generate_result'))

        # Fetch the selected entities
        try:
            session = AcademicSession.objects.get(id=session_id)
            term = Term.objects.get(id=term_id)
            classroom = ClassRoom.objects.get(id=classroom_id)
            student = Student.objects.get(id=student_id)
        except (AcademicSession.DoesNotExist, Term.DoesNotExist, ClassRoom.DoesNotExist, Student.DoesNotExist):
            messages.error(request, "Invalid selection. Please try again.")
            return redirect(reverse('admin:generate_result'))

        # Fetch Assessment Sections related to the classroom and term
        assessment_sections = AssessmentSection.objects.filter(
            classroom=classroom, term=term).prefetch_related('assessment_areas__assessment_subareas')

        # Fetch Grade Types
        grade_types = GradeType.objects.all()

        # Fetch existing Student Results
        student_results = StudentResult.objects.filter(
            student=student, term=term, section__in=assessment_sections
        ).prefetch_related('grades__grade', 'grades__assessment_sub_area')

        # Prepare Grades Dictionary
        grades_dict = {}
        for result in student_results:
            for grade in result.grades.all():
                subarea_id = grade.assessment_sub_area.id
                grade_type_id = grade.grade.id  # Corrected from grade.grade_type.id
                grades_dict.setdefault(subarea_id, {})[grade_type_id] = grade
        context = {
            'title': 'Generated Results',
            'student': student,
            'session': session,
            'term': term,
            'classroom': classroom,
            'assessment_sections': assessment_sections,
            'grade_types': grade_types,
            'grades_dict': grades_dict,
            'opts': self.model._meta,
            **self.admin_site.each_context(request),
        }

        return render(request, 'admin/results/show_results.html', context)

    def save_grade(self, request):
        """
        Saves the grade selected by the admin.
        """
        if request.method == "POST":
            data = json.loads(request.body)
            subarea_id = data.get("subarea_id")
            grade_value = data.get("grade")
            student_id = data.get("student_id")

            try:
                grade_type = GradeType.objects.get(label=grade_value)
                sub_area = AssessmentSubArea.objects.get(id=subarea_id)
                student = Student.objects.get(id=student_id)

                # Create or update the grade
                grade, created = Grade.objects.update_or_create(
                    assessment_sub_area=sub_area,
                    student=student,
                    defaults={'grade': grade_type},
                )
                return JsonResponse({"success": True, "message": "Grade saved successfully."})
            except (GradeType.DoesNotExist, AssessmentSubArea.DoesNotExist, Student.DoesNotExist):
                return JsonResponse({"success": False, "message": "Invalid data provided."}, status=400)

        return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)

    def has_module_permission(self, request):
        # Always show in admin index
        return True

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_classrooms(self, request, session_id, term_id):
        """
        Returns classrooms based on selected session and term.
        """
        classrooms = ClassRoom.objects.filter(
            name__in=['PG1', 'PG2', 'N1', 'N2']
        ).distinct()
        classroom_list = [{"id": c.id, "name": c.name}
                          for c in classrooms]  # type:ignore
        return JsonResponse({"classrooms": classroom_list})

    def get_students(self, request, classroom_id):
        """
        Returns students based on selected classroom.
        """
        students = Student.objects.filter(classroom__id=classroom_id)
        student_list = [{"id": s.id, "fullname": s.fullname}
                        for s in students]  # type:ignore
        return JsonResponse({"students": student_list})
