from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class course(models.Model):
    course_name=models.CharField(max_length=100)
    duration=models.CharField(max_length=100)

class faculty(models.Model):
    name=models.CharField(max_length=100)
    gender=models.CharField(max_length=100)
    dob=models.CharField(max_length=100)
    email=models.CharField(max_length=100)
    phone=models.CharField(max_length=100)
    place=models.CharField(max_length=100)
    city=models.CharField(max_length=100)
    state=models.CharField(max_length=100)
    pin=models.CharField(max_length=100)
    experience = models.CharField(max_length=100)
    image=models.CharField(max_length=100)
    LOGIN=models.ForeignKey(User, on_delete=models.CASCADE)

class subject(models.Model):
    sub_name=models.CharField(max_length=100)
    semester=models.CharField(max_length=100)
    COURSE=models.ForeignKey(course, on_delete=models.CASCADE)

class sub_allocation(models.Model):
    SUBJECT=models.ForeignKey(subject, on_delete=models.CASCADE)
    FACULTY=models.ForeignKey(faculty, on_delete=models.CASCADE)

class student(models.Model):
    std_name=models.CharField(max_length=100)
    COURSE=models.ForeignKey(course, on_delete=models.CASCADE)
    semester=models.CharField(max_length=100)
    ad_num=models.CharField(max_length=100)
    gender=models.CharField(max_length=100)
    dob=models.CharField(max_length=100)
    email=models.CharField(max_length=100)
    phone=models.CharField(max_length=100)
    place=models.CharField(max_length=100)
    state=models.CharField(max_length=100)
    city=models.CharField(max_length=100, default="")
    pin=models.CharField(max_length=100)
    image=models.CharField(max_length=100)
    LOGIN=models.ForeignKey(User, on_delete=models.CASCADE)

class progress(models.Model):
    STUDENT=models.ForeignKey(student, on_delete=models.CASCADE)
    prog_detail=models.CharField(max_length=100)

class suggestion(models.Model):
    FACULTY=models.ForeignKey(faculty, on_delete=models.CASCADE)
    suggestion=models.CharField(max_length=100)
    date=models.CharField(max_length=100)

class units(models.Model):
    unit_name=models.CharField(max_length=100)
    SUB_ALLOCATION=models.ForeignKey(sub_allocation, on_delete=models.CASCADE)

class reference_link(models.Model):
    date=models.CharField(max_length=100, default="")
    title=models.CharField(max_length=100, default="")
    ref_link=models.CharField(max_length=100)
    UNITS=models.ForeignKey(units, on_delete=models.CASCADE)

class questions(models.Model):
    question=models.CharField(max_length=5000, default="")
    answer=models.CharField(max_length=5000, default="")
    UNITS=models.ForeignKey(units, on_delete=models.CASCADE)

class student_answer(models.Model):
    score=models.CharField(max_length=5000, default="")
    answer=models.CharField(max_length=5000, default="")
    QUESTION=models.ForeignKey(questions, on_delete=models.CASCADE)
    STUDENT=models.ForeignKey(student, on_delete=models.CASCADE)

class internal_mark(models.Model):
    mark=models.CharField(max_length=100)
    SUBJECT=models.ForeignKey(subject, on_delete=models.CASCADE)
    STUDENT=models.ForeignKey(student, on_delete=models.CASCADE)

class chat(models.Model):
    chat=models.CharField(max_length=100)
    date=models.CharField(max_length=100)
    type=models.CharField(max_length=100)
    FACULTY=models.ForeignKey(faculty, on_delete=models.CASCADE)
    STUDENT=models.ForeignKey(student, on_delete=models.CASCADE)

class feedback(models.Model):
    feedback=models.CharField(max_length=500)
    date=models.CharField(max_length=100)
    STUDENT=models.ForeignKey(student, on_delete=models.CASCADE)
    UNITS=models.ForeignKey(units, on_delete=models.CASCADE)








