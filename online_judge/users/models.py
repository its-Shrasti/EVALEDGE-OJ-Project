from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('participant', 'Participant'),
        ('setter', 'Problem Setter'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='participant')
    created_at = models.DateTimeField(auto_now_add=True)
    my_saved_problems = models.ManyToManyField('problems.Problem', related_name='saved_by', blank=True)

    def __str__(self):
        return self.username

# Create your models here.
