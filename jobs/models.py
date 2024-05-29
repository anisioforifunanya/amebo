from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
from users.models import AppUsers


class Jobs(models.Model):
    job_type_options = (
        ('remote', 'Remote'),
        ('onsite', 'Onsite'),
        ('hybrid', 'Hybrid'),
    )
    employment_type_options = (
        ('internship', 'Internship'),
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
    )
    posted_by = models.ForeignKey(AppUsers, on_delete=models.CASCADE, null=True, blank=True)
    company = models.CharField(max_length= 500, null=True, blank=True)
    title = models.CharField(max_length= 500, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    job_type = models.CharField(choices=job_type_options, max_length= 500, null=True, blank=True)
    employment_type = models.CharField(choices=employment_type_options, max_length= 500, null=True, blank=True)
    location = models.CharField(max_length= 500, null=True, blank=True)
    apply_link = models.URLField(max_length= 500, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.company}"
