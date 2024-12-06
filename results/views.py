from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .forms import ResultSelectionForm
from .models import StudentResult, GradeType, Grade, Subject, Student, Teacher


@login_required
def select_result_parameters(request):
    parent = request.user.parent  # Assuming OneToOne relation
    if request.method == 'POST':
        form = ResultSelectionForm(request.POST, parent=parent)
        if form.is_valid():
            session = form.cleaned_data['session']
            term = form.cleaned_data['term']
            child = form.cleaned_data['child']
            assessment = form.cleaned_data['assessment']
            # Redirect to the results page with selected parameters
            return redirect('view_results', session_id=session.id, 
                            term_id=term.id, child_id=child.id,
                            assessment_id = assessment.id)
    else:
        form = ResultSelectionForm(parent=parent)

    context = {
        'form': form
    }
    return render(request, 'results/select_results.html', context)


@login_required
def view_results(request, session_id, term_id, child_id, assessment_id):
    parent = request.user.parent
    # Verify that the selected child belongs to the parent
    child = get_object_or_404(Student, id=child_id, parents=parent)

    # Fetch the StudentResult
    student_result = get_object_or_404(
        StudentResult,
        student=child,
        term_id=term_id,
        section__term__session_id=session_id, 
        section = assessment_id
    )
    classroom = student_result.section.classroom #type:ignore
    try:
        class_teacher = Teacher.objects.filter(classroom=classroom, teacher_type='CT').first()
    except Teacher.DoesNotExist:
        class_teacher = None
    except:
        class_teacher = None 
    try:
        head_teacher = Teacher.objects.filter(teacher_type='HT').first()
    except Teacher.DoesNotExist:
        head_teacher = None

    # Fetch all GradeTypes, ordered by code or any desired order
    grade_types = GradeType.objects.all().order_by('code')

    # Fetch all Grades related to the StudentResult, select related fields to minimize queries
    grades = Grade.objects.filter(result=student_result).select_related(
        'assessment_sub_area__area__subject',
        'grade'
    )

    # Create a mapping of AssessmentSubArea to GradeType code
    grade_mapping = {
        grade.assessment_sub_area.id: grade.grade.code for grade in grades} #type:ignore

    # Fetch all Subjects related to the StudentResult's section and classroom
    subjects = Subject.objects.filter(
        classroom=student_result.section.classroom #type:ignore
    ).distinct()

    # Prepare structured data for the template
    subject_data = []
    for subject in subjects:
        # Fetch all AssessmentAreas for the subject
        assessment_areas = subject.assessment_areas.filter(section=assessment_id).select_related('section') #type:ignore
        area_data = []
        for area in assessment_areas:
            # Fetch all AssessmentSubAreas for the AssessmentArea
            sub_areas = area.assessment_subareas.all()
            for sub_area in sub_areas:
                assigned_grade_code = grade_mapping.get(sub_area.id, None)
                area_data.append({
                    'name': sub_area.name,
                    'grade_code': assigned_grade_code,
                })
        subject_data.append({
            'subject_name': subject.name,
            'assessment_areas': area_data,
        })

    context = {
        'student_result': student_result,
        'grade_types': grade_types,
        'subject_data': subject_data,
        'child': child,
        'class_teacher': class_teacher,
        'head_teacher': head_teacher,
        'classroom': classroom,
    }
    return render(request, 'results/view_results.html', context)
