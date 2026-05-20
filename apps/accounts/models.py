from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('alumni', 'Alumni'),
        ('admin', 'Admin'),
    )

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    @property
    def full_name(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return name if name else self.email.split('@')[0]

    @property
    def profile(self):
        """Returns the corresponding profile object based on role."""
        if self.role == 'student':
            return getattr(self, 'student_profile', None)
        elif self.role == 'alumni':
            return getattr(self, 'alumni_profile', None)
        return None

    def __str__(self):
        return f"{self.full_name} ({self.email})"


class WhitelistEmail(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('alumni', 'Alumni'),
    )
    
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    enrollment_number = models.CharField(max_length=50)
    batch = models.CharField(max_length=10)
    department = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return f"{self.full_name} <{self.email}> - {self.role} ({self.batch})"


class StudentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    bio = models.TextField(blank=True)
    current_year = models.CharField(max_length=20)
    skills = models.CharField(max_length=255, blank=True)
    profile_image = models.ImageField(upload_to='avatars/students/', null=True, blank=True)

    def __str__(self):
        return f"Student: {self.user.email}"


class AlumniProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='alumni_profile')
    company = models.CharField(max_length=150, blank=True)
    designation = models.CharField(max_length=150, blank=True)
    location = models.CharField(max_length=100, blank=True)
    graduation_year = models.CharField(max_length=10)
    linkedin = models.URLField(blank=True)
    skills = models.CharField(max_length=255, blank=True)
    profile_image = models.ImageField(upload_to='avatars/alumni/', null=True, blank=True)
    is_mentor_available = models.BooleanField(default=False)

    def __str__(self):
        return f"Alumni: {self.user.email}"
