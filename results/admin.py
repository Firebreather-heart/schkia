from django.contrib import admin, messages
from django import forms
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import render, redirect, get_object_or_404
from .models import (
    ClassRoom, Subject, Assessment, AcademicSession, Term, AssessmentArea, AssessmentSection, AssessmentSubArea
)
from results.models import Student


class AssessmentAdminForm(forms.ModelForm):

    class Meta:
        model = Assessment
        fields = ['student', 'subject', 'name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['student'].label = "Child's Name"
        self.fields['subject'].label = "Subject"
        self.fields['name'].label = "Assessment"

        self.fields['name'].widget.attrs.update(
            {'class': 'custom-assessment-dropdown'})
        self.fields['student'].widget.attrs.update(
            {'class': 'form-control'})
        self.fields['subject'].widget.attrs.update({'class': 'form-control'})
        self.fields['name'].widget.attrs.update(
            {'class': 'custom-assessment-dropdown form-control'})


class AssessmentInline(admin.TabularInline):
    model = Assessment
    extra = 1


class AssessmentAreaInline(admin.TabularInline):
    model = AssessmentArea
    extra = 1

class AssessmentSubAreaInline(admin.TabularInline):
    model = AssessmentSubArea
    extra = 1
    verbose_name = 'Manage Items'
    verbose_name_plural = 'Manage_Items'


@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    form = AssessmentAdminForm
    list_display = ['student', 'subject', 'name']
    list_filter = ['subject', 'name']
    search_fields = ['student__fullname', 'subject__name']

    change_list_template = "admin/assessments_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('select/', self.admin_site.admin_view(self.select_view),
                 name='assessments_select'),
            path('select_student/<str:classroom_id>/<int:session_id>/<int:term_id>/',
                 self.admin_site.admin_view(self.select_student_view),
                 name='select_student'),
            path(
                "finalize_assessment/<int:student_id>/<str:classroom>/",
                self.admin_site.admin_view(self.finalize_assessment),
                name="finalize_assessment",
            ),
        ]
        return custom_urls + urls

    def select_view(self, request):
        if request.method == 'POST':
            classroom_id = request.POST.get('classroom')
            session_id = request.POST.get('session')
            term_id = request.POST.get('term')
            return redirect('admin:select_student', classroom_id=classroom_id, session_id=session_id, term_id=term_id)

        context = dict(
            self.admin_site.each_context(request),
            classrooms=ClassRoom.objects.all(),
            sessions=AcademicSession.objects.all(),
            terms=Term.objects.all(),
        )

        return render(request, "admin/select_assessment.html", context)

    def select_student_view(self, request, classroom_id, session_id, term_id):
        students = Student.objects.filter(classroom=classroom_id)

        if request.method == 'POST':
            student_id = request.POST.get('student')
            return redirect('admin:finalize_assessment', student_id=student_id,
                            classroom=classroom_id)

        context = dict(
            self.admin_site.each_context(request),
            students=students,
            classroom=ClassRoom.objects.get(name=classroom_id),
            session=AcademicSession.objects.get(id=session_id),
            term=Term.objects.get(id=term_id),
        )
        return render(request, "admin/select_student.html", context)

    def finalize_assessment(self, request, student_id, classroom):
        student = Student.objects.get(id=student_id)
        subjects = Subject.objects.filter(classroom__name=classroom)
        context = dict(
            subjects=subjects,
            student=student,
        )
        return render(request, "admin/finalize_assessment.html", context)

    fieldsets = (
        ("Student Details", {
            'fields': ('student', 'subject')
        }),
        ("Assessment", {
            'fields': ('name',),
        }),
    )


@admin.register(AcademicSession)
class AcademicSessionAdmin(admin.ModelAdmin):
    list_display = ['session']


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ['term', 'session']


@admin.register(AssessmentArea)
class AssessmentAreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'section', 'subject')
    search_fields = ('name', 'section__name', 'subject__name')
    inlines = [AssessmentSubAreaInline]


# @admin.register(AssessmentSubArea)
# class AssessmentSubAreaAdmin(admin.ModelAdmin):
#     list_display = ('name', 'area')
#     search_fields = ('name', 'area__name')


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
