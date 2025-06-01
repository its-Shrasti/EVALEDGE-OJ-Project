from django.db import models
from django.conf import settings

class Problem(models.Model):
    DIFFICULTY_CHOICES = [('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')]

    title = models.CharField(max_length=100)
    description = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    topic = models.CharField(max_length=50)
    hints = models.TextField(blank=True, null=True)
    constraints = models.TextField(blank=True, null=True)
    problem_statistics = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='my_problems')
    isSolved = models.BooleanField(default=False)


class Submission(models.Model):
    LANG_CHOICES=[('py','python'),
                  ('cpp','C++'),
                  ('c','C')]
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    verdict = models.CharField(max_length=50)
    submitted_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions')
    code = models.TextField()
    language = models.CharField(max_length=10, choices=LANG_CHOICES)
    exec_time = models.FloatField(blank=True, null=True)


class TestCase(models.Model):
    input = models.CharField(max_length=255)
    expected_output = models.CharField(max_length=255)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
# Create your models here.
