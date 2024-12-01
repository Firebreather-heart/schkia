from django.contrib import admin
from django import forms
from django.urls import path 
from django.shortcuts import render, redirect 
from .models import ClassRoom, Subject, Assessment, AcademicSession, Term
from results.models import Student  



class AssessmentAdminForm(forms.ModelForm):

    class Meta:
        model = Assessment
        fields = ['student', 'subject', 'name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Adding placeholders and improving the layout
        self.fields['student'].label = "Child's Name"
        self.fields['subject'].label = "Subject"
        self.fields['name'].label = "Assessment"

        # Add custom CSS classes for styling (use Jazzmin's existing styles or create custom ones)
        self.fields['name'].widget.attrs.update(
            {'class': 'custom-assessment-dropdown'})



class AssessmentInline(admin.TabularInline):
    model = Assessment
    extra = 1  


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
        ]
        return custom_urls + urls

    def select_view(self, request):
        if request.method == 'POST':
            student_id = request.POST.get('student')
            session_id = request.POST.get('session')
            term_id = request.POST.get('term')
            return redirect(f'/admin/results/assessment/?student={student_id}&session={session_id}&term={term_id}')

        context = dict(
            self.admin_site.each_context(request),
            students=Student.objects.all(),
            sessions=AcademicSession.objects.all(),
            terms=Term.objects.all(),
        )
        return render(request, "admin/select_assessment.html", context)

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

