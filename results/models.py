from django.db import models
from django.contrib.auth import get_user_model
from django.forms import ValidationError
# Create your models here.


class ClassRoom(models.Model):
    NAME_CHOICES = (
        ('N1', 'Nursery 1'),
        ('N2', 'Nursery 2'),
        ('PG1', 'Playgroup 1'),
        ('PG2', 'Playgroup 2'),
        ('Y1', 'Year 1'),
        ('Y2', 'Year 2'),
        ('Y3', 'Year 3'),
        ('Y4', 'Year 4'),
        ('Y5', 'Year 5'),
        ('Y6', 'Year 6'),
    )
    name = models.CharField(max_length=50, choices=NAME_CHOICES, unique=True)

    def __str__(self):
        return self.classname()

    def classname(self):
        return self.get_name_display()  # type: ignore

    class Meta:
        verbose_name_plural = 'Classrooms'
        verbose_name = 'Classroom'


class Subject(models.Model):
    name = models.CharField(max_length=50)
    classroom = models.ForeignKey(
        ClassRoom, on_delete=models.CASCADE, related_name='subjects')

    def __str__(self):
        return f"{self.name} - {self.classroom}"


class AcademicSession(models.Model):
    session = models.CharField(max_length=50)

    def __str__(self):
        return self.session


class Term(models.Model):
    term = models.CharField(max_length=50)
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.term} - {self.session}"


class AssessmentSection(models.Model):
    name = models.CharField(max_length=50)
    term = models.ForeignKey(Term, on_delete=models.CASCADE,
                             related_name='assessment_sections')
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE,
                                  related_name='assessment_sections')

    def __str__(self):
        return f'{self.name} - {self.classroom}'

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            for subject in self.classroom.subjects.all():  # type: ignore
                AssessmentArea.objects.create(
                    name=subject.name, subject=subject, section=self)

    class Meta:
        verbose_name = "Result Section"
        verbose_name_plural = "Result Sections"


class AssessmentArea(models.Model):
    name = models.CharField(max_length=50)
    section = models.ForeignKey(
        AssessmentSection, on_delete=models.CASCADE, related_name='assessment_areas')
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name='subjects')
    teacher_comment = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Result Subsection'
        verbose_name_plural = 'Result Subsections'


class AssessmentSubArea(models.Model):
    name = models.CharField(max_length=50)
    area = models.ForeignKey(AssessmentArea,
                             on_delete=models.CASCADE, related_name='assessment_subareas')
    

    def __str__(self):
        return self.name


class GradeType(models.Model):
    code = models.CharField(max_length=15, unique=True)
    label = models.CharField(max_length=50)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Grade'
        verbose_name_plural = 'Grades'

    def __str__(self):
        return f"{self.code} - {self.label}"

    @classmethod
    def get_choices(cls):
        return [(grade.code, grade.label) for grade in cls.objects.all()]
    

class Grade(models.Model):
    DEFAULT_GRADES = [
        ('EX', 'Excellent'),
        ('VG', 'Very Good'),
        ('G', 'Good'),
        ('W.I.P', 'Work in Progress'),
        ('NA', 'Not Applicable'),
    ]

    grade = models.ForeignKey(
        GradeType,
        on_delete=models.PROTECT,  # Prevent deletion of grade types that are in use
        related_name='grades'
    )
    assessment_sub_area = models.ForeignKey(
        AssessmentSubArea,
        on_delete=models.CASCADE
    )
    student = models.ForeignKey(
        'Student',
        on_delete=models.CASCADE,
        related_name='grades'
    )
    result = models.ForeignKey(
        'StudentResult',
        on_delete=models.CASCADE,
        related_name='grades'
    )

    class Meta:
        unique_together = ('assessment_sub_area', 'student')

    def __str__(self):
        return str(self.grade)


class StudentResult(models.Model):
    student = models.ForeignKey(
        'Student', on_delete=models.CASCADE, related_name='results')
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    teacher_general_comment = models.CharField(max_length=200, blank=True, null=True)
    head_teacher_comment = models.CharField(max_length=200, blank=True, null=True)
    section = models.ForeignKey(
        AssessmentSection, 
        on_delete=models.CASCADE,
        related_name = 'student_results', 
        null = True
    )
    date = models.DateField(auto_now=True)

    class Meta:
        verbose_name = 'Result'
        verbose_name_plural = 'Results'
        unique_together = ('student', 'term', 'section')

    def __str__(self):
        return f'Result for {self.student} - {self.term}'




class Student(models.Model):
    fullname = models.CharField(max_length=50)
    date_of_birth = models.DateField(blank=True, null=True)
    hostel = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(max_length=50, choices=(
        ('M', "male"),
        ('F', 'female'),
        ('NA', 'not available')
    ), default='NA')
    phone_number = models.CharField(max_length=50)
    roll_id = models.CharField(max_length=10, unique=True)
    number = models.CharField(max_length=10, unique=True)
    classroom = models.ForeignKey(ClassRoom,
                                  on_delete=models.CASCADE,
                                  related_name='students',
                                  to_field='name'
                                  )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.fullname


class ResultGeneration(models.Model):
    id = models.AutoField(primary_key=True)
    
    class Meta:
        managed = True  # No database table needed
        verbose_name_plural = "Result Generation"
        app_label = 'results'
