import uuid, os
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


def validate_file_size(value):
    filesize = value.size
    if filesize > 512000:  # 500KB = 512000 bytes
        raise ValidationError("Maximum file size is 500KB")
    

def signature_upload_path(instance, filename):
    # Get the file extension
    ext = filename.split('.')[-1]
    # Create filename pattern: student_id_term_id.extension
    return f'signatures/{instance.student.id}_{instance.term.id}.{ext}'

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The username must be set')
        user = self.model(username = username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=False)
    username = models.CharField(max_length=50, blank=True, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    signature = models.ImageField(
        upload_to=signature_upload_path,
        validators=[validate_file_size],
        blank=True,
        null=True,
        help_text="Signature image (max 500KB)"
    )

    objects = CustomUserManager()

    
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        return super(CustomUser, self).save(*args, **kwargs)


class Parent(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    fullname = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=50, unique=True)
    address = models.CharField(max_length=50)
    gender = models.CharField(max_length=50)
    occupation = models.CharField(max_length=50)
    photo = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    student = models.ForeignKey('results.Student', on_delete=models.CASCADE, related_name='parents', null=True, blank=True)

    def __str__(self):
        return self.fullname
    

    
