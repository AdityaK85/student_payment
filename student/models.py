from django.db import models
import random

class Student(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, blank=False)
    password = models.CharField(max_length=50, null=True,  blank=True , default=f'STU{random.randint(1111, 9999)}')
    contact = models.CharField(max_length=50, blank=False)
    address = models.CharField(max_length=150, blank=False)
    email = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
